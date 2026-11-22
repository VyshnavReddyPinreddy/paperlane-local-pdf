"""Paperlane Local PDF - loopback-only HTTP service, without cloud APIs."""
from __future__ import annotations

import atexit
import base64
import io
import json
import os
import secrets
import shutil
import tempfile
import threading
import time
import webbrowser
from pathlib import Path

import fitz
from fastapi import FastAPI, HTTPException, Request, UploadFile
from starlette.datastructures import UploadFile as StarletteUploadFile
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image
from starlette.concurrency import run_in_threadpool

from engine import (ALL_TOOLS, IMAGE_TOOLS, IMAGE_EXTS, OFFICE_TOOLS,
                    ToolError, find_libreoffice, get_pdf, process, safe_name)

BASE = Path(__file__).resolve().parent
app = FastAPI(title='Paperlane Local PDF', docs_url=None, redoc_url=None, openapi_url=None)
app.mount('/static',StaticFiles(directory=BASE/'static'),name='static')

# Download jobs exist in the OS temp directory only until shutdown or one hour.
_jobs: dict[str,tuple[Path,Path,str,float]] = {}
_lock = threading.Lock()
TTL = 3600


def cleanup_jobs(force=False):
    now = time.time()
    old = []
    with _lock:
        for token,(_,folder,_,created) in list(_jobs.items()):
            if force or now-created > TTL:
                old.append(folder)
                del _jobs[token]
    for path in old:
        shutil.rmtree(path,ignore_errors=True)

atexit.register(lambda: cleanup_jobs(force=True))


@app.middleware('http')
async def same_machine_only(request: Request, call_next):
    host = request.url.hostname or ''
    if host.lower() not in ('127.0.0.1','localhost'):
        return JSONResponse({'error':'Only local connections are allowed.'},status_code=403)
    if request.url.path.startswith('/api/') and request.method=='POST':
        if request.headers.get('X-Paperlane-Local') != '1':
            return JSONResponse({'error':'This operation must originate from the local app.'},status_code=403)
        origin=request.headers.get('origin','').rstrip('/')
        port=request.url.port or 80
        if origin and origin not in (f'http://127.0.0.1:{port}',f'http://localhost:{port}'):
            return JSONResponse({'error':'Cross-origin requests are blocked.'},status_code=403)
    response = await call_next(request)
    response.headers['Content-Security-Policy']=(
        "default-src 'self'; script-src 'self'; style-src 'self'; "
        "img-src 'self' data: blob:; connect-src 'self'; object-src 'none'; "
        "base-uri 'none'; frame-ancestors 'none'; form-action 'self'")
    response.headers['X-Content-Type-Options']='nosniff'
    response.headers['Referrer-Policy']='no-referrer'
    response.headers['Permissions-Policy']='camera=(self), microphone=()'
    if request.url.path.startswith('/api/'):
        response.headers['Cache-Control']='no-store'
    return response


@app.get('/')
async def index():
    return FileResponse(BASE/'static'/'index.html',media_type='text/html')


@app.get('/api/health')
async def health():
    cleanup_jobs()
    soffice = find_libreoffice()
    return {'ok':True,'offline':True,'office':bool(soffice),
            'version':'1.0.0','engine':f'PyMuPDF {fitz.VersionBind}',
            'tools':len(ALL_TOOLS)}


def check_inputs(tool, uploads):
    exts = IMAGE_EXTS if tool in IMAGE_TOOLS else (
        OFFICE_TOOLS.get(tool,set()) if tool in OFFICE_TOOLS else {'.pdf'})
    for f in uploads:
        suffix=Path(f.filename or '').suffix.lower()
        if suffix not in exts:
            raise ToolError(f'{f.filename or "Unnamed file"} is not supported. Allowed: {", ".join(sorted(exts))}')
    if tool == 'merge' and len(uploads) < 2:
        raise ToolError('Select at least two PDF files to merge.')
    if tool == 'organize' and len(uploads) != 1:
        raise ToolError('Organize one PDF at a time. You can reorder or remove any number of pages.')


async def store_files(uploads: list[UploadFile], tmp: Path):
    paths,names=[],[]
    for j,upload in enumerate(uploads,1):
        name=safe_name(upload.filename or f'file_{j}')
        target=tmp/f'{j:04d}_{name}'
        with target.open('wb') as out:
            while chunk := await upload.read(1024*1024):
                out.write(chunk)
        if target.stat().st_size == 0:
            raise ToolError(f'{name} is empty.')
        paths.append(target)
        names.append(name)
    return paths,names


async def uploaded_parts(request):
    # Starlette's default is 1,000 files; use an effectively unbounded local limit.
    form=await request.form(max_files=2**31-1, max_fields=2**31-1, max_part_size=2**31-1)
    files=[v for k,v in form.multi_items() if k=='files' and isinstance(v,StarletteUploadFile) and v.filename]
    return form,files


@app.post('/api/run/{tool}')
async def run_tool(tool: str, request: Request):
    if tool not in ALL_TOOLS:
        raise HTTPException(status_code=404,detail='Unknown tool.')
    temp=Path(tempfile.mkdtemp(prefix='paperlane_'))
    try:
        form,uploads=await uploaded_parts(request)
        if not uploads:
            raise ToolError('Choose your files first.')
        check_inputs(tool,uploads)
        try:
            opts=json.loads(form.get('options','{}'))
        except (ValueError,TypeError):
            raise ToolError('Invalid processing options.')
        if not isinstance(opts,dict):
            raise ToolError('Invalid processing options.')
        paths,names=await store_files(uploads,temp)
        output,filename=await run_in_threadpool(process,tool,paths,names,opts,temp)
        token=secrets.token_urlsafe(24)
        with _lock:
            _jobs[token]=(output,temp,filename,time.time())
        cleanup_jobs()
        return {'ok':True,'filename':filename,'download_url':f'/api/download/{token}',
                'bytes':output.stat().st_size}
    except ToolError as ex:
        shutil.rmtree(temp,ignore_errors=True)
        return JSONResponse({'error':str(ex)},status_code=400)
    except Exception as ex:
        shutil.rmtree(temp,ignore_errors=True)
        import traceback
        traceback.print_exc()
        return JSONResponse({'error':f'Processing failed: {ex}'},status_code=500)


@app.get('/api/download/{token}')
async def download(token: str):
    cleanup_jobs()
    with _lock:
        data=_jobs.get(token)
    if not data or not data[0].is_file():
        raise HTTPException(status_code=404,detail='Download expired. Process the files again.')
    path,_,filename,_=data
    return FileResponse(path,filename=filename,media_type=(
        'application/zip' if filename.lower().endswith('.zip') else 'application/pdf'
        if filename.lower().endswith('.pdf') else 'application/octet-stream'))


@app.post('/api/inspect')
async def inspect_pdf(request: Request):
    tmp=Path(tempfile.mkdtemp(prefix='paperlane_preview_'))
    try:
        form,uploads=await uploaded_parts(request)
        if not uploads or Path(uploads[0].filename or '').suffix.lower()!='.pdf':
            raise ToolError('Choose a valid PDF.')
        paths,_=await store_files(uploads[:1],tmp)
        start=max(0,int(form.get('start','0')))
        count=min(48,max(1,int(form.get('count','36'))))
        pwd=str(form.get('password',''))
        with get_pdf(paths[0],pwd) as doc:
            total=doc.page_count
            imgs=[]
            for i in range(start,min(start+count,total)):
                page=doc[i]
                scale=min(.4,220/max(page.rect.width,page.rect.height))
                pix=page.get_pixmap(matrix=fitz.Matrix(scale,scale),alpha=False,colorspace=fitz.csRGB)
                with Image.frombytes('RGB',(pix.width,pix.height),pix.samples) as img:
                    b=io.BytesIO()
                    img.save(b,'JPEG',quality=67,optimize=True)
                imgs.append({'i':i,'src':'data:image/jpeg;base64,'+base64.b64encode(b.getvalue()).decode('ascii')})
        return {'ok':True,'total':total,'start':start,'images':imgs}
    except (ToolError,ValueError) as ex:
        return JSONResponse({'error':str(ex)},status_code=400)
    except Exception as ex:
        return JSONResponse({'error':f'Could not preview PDF: {ex}'},status_code=500)
    finally:
        shutil.rmtree(tmp,ignore_errors=True)


def main():
    import argparse
    import uvicorn
    p=argparse.ArgumentParser(description='Local/offline PDF workspace')
    p.add_argument('--port',type=int,default=8765)
    p.add_argument('--no-browser',action='store_true')
    args=p.parse_args()
    address=f'http://127.0.0.1:{args.port}'
    print('\n'+'='*58)
    print(' PAPERLANE | Local PDF Workspace')
    print(' Open:',address)
    print(' All document processing stays on this device.')
    print(' Press Ctrl+C to stop the server.')
    print('='*58+'\n')
    if not args.no_browser:
        threading.Timer(1.4,lambda:webbrowser.open(address)).start()
    uvicorn.run(app,host='127.0.0.1',port=args.port,log_level='warning')


if __name__=='__main__':
    main()
