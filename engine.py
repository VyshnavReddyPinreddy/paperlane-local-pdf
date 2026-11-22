"""Offline PDF operations. All inputs/outputs are local temporary files."""
from __future__ import annotations

import io
import math
import os
import re
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path
from typing import Any
from urllib.parse import unquote

import fitz
from PIL import Image, ImageEnhance, ImageOps

PDF_TOOLS = {
    'merge', 'split', 'remove', 'extract', 'organize', 'compress',
    'pdf-jpg', 'rotate', 'page-numbers', 'watermark', 'crop', 'unlock', 'protect',
}
IMAGE_TOOLS = {'jpg-pdf', 'scan-pdf'}
OFFICE_TOOLS = {'word-pdf': {'.doc', '.docx', '.odt', '.rtf'},
                'powerpoint-pdf': {'.ppt', '.pptx', '.odp'},
                'excel-pdf': {'.xls', '.xlsx', '.ods', '.csv'},
                'html-pdf': {'.html', '.htm'}}
IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tif', '.tiff'}
ALL_TOOLS = PDF_TOOLS | IMAGE_TOOLS | set(OFFICE_TOOLS)

class ToolError(Exception):
    """User-facing operational error."""


def safe_name(name: str, fallback='document') -> str:
    value = Path(str(name).replace('\\', '/')).name
    value = re.sub(r'[^A-Za-z0-9_.-]+', '_', value).strip('._')
    return value[:100] or fallback


def clean_stem(name: str) -> str:
    return Path(safe_name(name)).stem or 'document'


def integer(value: Any, default: int, low: int, high: int) -> int:
    try:
        n = int(value)
    except (TypeError, ValueError):
        n = default
    return max(low, min(n, high))


def float_number(value: Any, default: float, low: float, high: float) -> float:
    try:
        n = float(value)
        if not (low <= n <= high):
            raise ValueError
        return n
    except (TypeError, ValueError):
        return default


def parse_groups(text: str, n: int, required=True) -> list[list[int]]:
    """One-based '1-3, 7, 9-11' -> zero-based grouped indices."""
    text = str(text or '').strip()
    if not text:
        if required:
            raise ToolError('Enter page numbers such as 1-3, 5, 8-10.')
        return []
    groups = []
    for item in text.split(','):
        item = item.strip()
        match = re.fullmatch(r'(\d+)\s*(?:-\s*(\d+))?', item)
        if not match:
            raise ToolError(f'Invalid page range: {item!r}. Example: 1-3, 5, 8-10.')
        a, b = int(match.group(1)), int(match.group(2) or match.group(1))
        if a < 1 or b < a or b > n:
            raise ToolError(f'Page range {item} is outside this PDF (1-{n}).')
        groups.append(list(range(a-1, b)))
    return groups


def flat_unique(groups: list[list[int]]) -> list[int]:
    return list(dict.fromkeys(i for group in groups for i in group))


def get_pdf(path: Path, password: str='') -> fitz.Document:
    try:
        doc = fitz.open(str(path))
        if not doc.is_pdf:
            doc.close()
            raise ToolError('The selected file is not a valid PDF.')
        if doc.needs_pass:
            if not password or not doc.authenticate(password):
                doc.close()
                raise ToolError(f'{path.name} is password-protected. Enter the correct PDF password.')
        if doc.page_count == 0:
            doc.close()
            raise ToolError(f'{path.name} has no pages.')
        return doc
    except ToolError:
        raise
    except Exception as ex:
        raise ToolError(f'Could not open {path.name}: {ex}') from ex


def save_pdf(doc: fitz.Document, dest: Path, *, encrypted=False, user_pw='', owner_pw='', permissions=0):
    try:
        kwargs = dict(garbage=4, deflate=True, use_objstms=1)
        if encrypted:
            kwargs.update(encryption=fitz.PDF_ENCRYPT_AES_256, user_pw=user_pw,
                          owner_pw=owner_pw, permissions=permissions)
        else:
            kwargs['encryption'] = fitz.PDF_ENCRYPT_NONE
        doc.save(str(dest), **kwargs)
    finally:
        doc.close()


def find_libreoffice() -> str | None:
    env = os.environ.get('LIBREOFFICE_PATH', '').strip('"')
    if env and Path(env).is_file():
        return env
    for cmd in ('soffice', 'libreoffice'):
        result = shutil.which(cmd)
        if result:
            return result
    if os.name == 'nt':
        candidates = [Path(os.environ.get('PROGRAMFILES', 'C:/Program Files')) / 'LibreOffice/program/soffice.exe',
                      Path(os.environ.get('PROGRAMFILES(X86)', 'C:/Program Files (x86)')) / 'LibreOffice/program/soffice.exe']
        for path in candidates:
            if path.is_file():
                return str(path)
    return None


def office_to_pdf(src: Path, dest: Path, temp: Path):
    soffice = find_libreoffice()
    if not soffice:
        raise ToolError('LibreOffice is not installed or could not be found. Install the desktop LibreOffice app, then restart Paperlane. No online service is used.')
    outputdir = temp / ('office-output-' + src.stem)
    outputdir.mkdir(exist_ok=True)
    profile = temp / ('lo-profile-' + src.stem)
    try:
        command = [soffice, '-env:UserInstallation=' + profile.resolve().as_uri(),
                   '--headless', '--convert-to', 'pdf', '--outdir', str(outputdir), str(src)]
        lo_env = os.environ.copy()
        if os.name != 'nt':
            lo_env.pop('DISPLAY', None)
            lo_env['SAL_USE_VCLPLUGIN'] = 'svp'
        result = subprocess.run(command, capture_output=True, text=True, timeout=600, env=lo_env)
    except subprocess.TimeoutExpired as ex:
        raise ToolError(f'LibreOffice took too long converting {src.name}.') from ex
    except OSError as ex:
        raise ToolError(f'Could not start LibreOffice: {ex}') from ex
    produced = outputdir / (src.stem + '.pdf')
    if result.returncode != 0 or not produced.is_file() or produced.stat().st_size == 0:
        details = (result.stderr or result.stdout or '').strip()[-350:]
        raise ToolError(f'LibreOffice could not convert {src.name}. {details}')
    shutil.move(produced, dest)


def sanitize_html(src: Path):
    """Remove common external resource loading and active content before opening in LO."""
    try:
        content = src.read_text(encoding='utf-8-sig')
    except UnicodeDecodeError:
        content = src.read_text(encoding='latin-1')
    content = re.sub(r'<(script|iframe|object|embed|form|meta|base)\b[^>]*>.*?</\1\s*>',
                     '', content, flags=re.I | re.S)
    content = re.sub(r'<(script|iframe|object|embed|form|meta|base)\b[^>]*?/?>',
                     '', content, flags=re.I | re.S)
    content = re.sub(r'<link\b[^>]*>', '', content, flags=re.I)
    content = re.sub(r'url\s*\([^)]*\)', 'none', content, flags=re.I)
    content = re.sub(r'\b(src|href|background|action|data)\s*=\s*([\"\'])\s*(?:https?:|ftp:|file:|//|data:)[^\2]*?\2',
                     '', content, flags=re.I)
    # Also remove unquoted external src/href values.
    content = re.sub(r'\b(src|href|background|action|data)\s*=\s*(?:https?:|ftp:|file:|//|data:)[^\s>]+',
                     '', content, flags=re.I)
    src.write_text(content, encoding='utf-8')


def write_image_pdf(files: list[Path], dest: Path, options: dict, scan=False):
    doc = fitz.open()
    mode = str(options.get('size', 'a4'))
    margin = float_number(options.get('margin', 16), 16, 0, 80)
    effect = str(options.get('effect', 'color')) if scan else 'color'
    for path in files:
        try:
            with Image.open(path) as im:
                im = ImageOps.exif_transpose(im)
                if effect == 'grayscale':
                    im = ImageOps.grayscale(im)
                elif effect == 'document':
                    im = ImageEnhance.Contrast(ImageOps.grayscale(im)).enhance(1.65)
                im = im.convert('RGB')
                w, h = im.size
                if w < 1 or h < 1:
                    raise ToolError(f'{path.name} has invalid dimensions.')
                buf = io.BytesIO()
                im.save(buf, format='JPEG', quality=94, optimize=True)
                img_bytes = buf.getvalue()
        except ToolError:
            raise
        except Exception as ex:
            raise ToolError(f'Cannot read image {path.name}: {ex}') from ex
        if mode == 'original':
            factor = min(1.0, 1800.0/max(w, h))
            width, height = max(36,w*factor), max(36,h*factor)
            rect = fitz.Rect(0,0,width,height)
        else:
            width, height = (595.28,841.89) if mode != 'letter' else (612,792)
            box = fitz.Rect(margin,margin,width-margin,height-margin)
            scale = min(box.width/w,box.height/h)
            dw, dh = w*scale, h*scale
            rect = fitz.Rect((width-dw)/2, (height-dh)/2,
                             (width+dw)/2, (height+dh)/2)
        page = doc.new_page(width=width,height=height)
        page.insert_image(rect, stream=img_bytes, keep_proportion=True)
    save_pdf(doc, dest)


def compress_pdf(doc: fitz.Document, level: str):
    if level == 'lossless':
        return
    target_dpi, quality = (150, 77) if level == 'balanced' else (110, 56)
    seen = set()
    for page in doc:
        for img in page.get_images(full=True):
            xref, smask = img[0], img[1]
            if xref in seen or smask or xref < 1:
                continue
            seen.add(xref)
            try:
                original = doc.extract_image(xref)
                source = original['image']
                with Image.open(io.BytesIO(source)) as image:
                    if image.mode not in ('RGB', 'L', 'P') or image.info.get('transparency') is not None:
                        continue
                    rects = page.get_image_rects(xref)
                    if rects:
                        maxw = max(max(r.width, 1) for r in rects)
                        maxh = max(max(r.height, 1) for r in rects)
                        limit_w = max(1, int(maxw * target_dpi/72))
                        limit_h = max(1, int(maxh * target_dpi/72))
                        ratio = min(1.0, limit_w/image.width, limit_h/image.height)
                        if ratio < 1:
                            image = image.resize((max(1,int(image.width*ratio)),
                                                  max(1,int(image.height*ratio))), Image.Resampling.LANCZOS)
                    out = io.BytesIO()
                    image.convert('RGB').save(out, 'JPEG', quality=quality, optimize=True)
                    newer = out.getvalue()
                if len(newer) < len(source):
                    page.replace_image(xref, stream=newer)
            except Exception:
                # Some exotic PDF image encodings cannot safely be re-encoded.
                # Keep them unchanged rather than harming the PDF.
                continue


def tool_single(tool: str, src: Path, dest_dir: Path, opts: dict, base: str) -> list[Path]:
    """Process one PDF; outputs are returned as actual file paths."""
    password = str(opts.get('password', ''))
    doc = get_pdf(src, password)
    n = doc.page_count
    out = dest_dir / (base + '.pdf')
    if tool == 'split':
        mode = str(opts.get('mode', 'every'))
        if mode == 'every':
            groups = [[i] for i in range(n)]
        elif mode == 'chunks':
            chunk = integer(opts.get('chunk', 2), 2, 1, 100000000)
            groups = [list(range(i,min(i+chunk,n))) for i in range(0,n,chunk)]
        else:
            groups = parse_groups(str(opts.get('ranges','')), n)
        output = []
        for j, group in enumerate(groups,1):
            part = fitz.open()
            for i in group:
                part.insert_pdf(doc, from_page=i, to_page=i, links=True, annots=True)
            target = dest_dir / f'{base}_part_{j:03d}.pdf'
            save_pdf(part,target)
            output.append(target)
        doc.close()
        return output
    if tool == 'remove':
        gone = set(flat_unique(parse_groups(str(opts.get('ranges', '')), n)))
        kept = [i for i in range(n) if i not in gone]
        if not kept:
            doc.close()
            raise ToolError('Removing every page would create an empty PDF.')
        doc.select(kept)
    elif tool == 'extract':
        groups = parse_groups(str(opts.get('ranges','')), n, required=False)
        if not groups:
            groups = [list(range(n))]
        if opts.get('separate'):
            output = []
            for j, group in enumerate(groups,1):
                part = fitz.open()
                for i in group:
                    part.insert_pdf(doc, from_page=i, to_page=i, links=True, annots=True)
                target = dest_dir / f'{base}_selection_{j:03d}.pdf'
                save_pdf(part,target)
                output.append(target)
            doc.close()
            return output
        doc.select(flat_unique(groups))
    elif tool == 'organize':
        pages = opts.get('pages')
        if not isinstance(pages,list) or not pages:
            doc.close()
            raise ToolError('No pages were selected for organizing.')
        try:
            indices = [int(x['i']) for x in pages]
            degrees = [int(x.get('rot',0)) for x in pages]
        except (TypeError, ValueError, KeyError) as ex:
            doc.close()
            raise ToolError('Invalid page order.') from ex
        if len(set(indices)) != len(indices) or min(indices) < 0 or max(indices) >= n:
            doc.close()
            raise ToolError('Page order has invalid or repeated source pages.')
        if any(d not in (0,90,180,270) for d in degrees):
            doc.close()
            raise ToolError('Invalid page rotation requested.')
        doc.select(indices)
        for j, angle in enumerate(degrees):
            if angle:
                page = doc[j]
                page.set_rotation((page.rotation + angle) % 360)
    elif tool == 'compress':
        compress_pdf(doc, str(opts.get('level','balanced')))
    elif tool == 'rotate':
        scope = str(opts.get('scope','all'))
        if scope == 'ranges':
            selected = set(flat_unique(parse_groups(str(opts.get('ranges','')), n)))
        elif scope == 'odd':
            selected = set(range(0,n,2))
        elif scope == 'even':
            selected = set(range(1,n,2))
        else:
            selected = set(range(n))
        angle = integer(opts.get('angle',90),90,0,270)
        if angle not in (90,180,270):
            doc.close()
            raise ToolError('Rotation must be 90, 180, or 270 degrees.')
        for i in selected:
            p = doc[i]
            p.set_rotation((p.rotation+angle)%360)
    elif tool == 'page-numbers':
        pos = str(opts.get('position','bottom-center'))
        size = integer(opts.get('fontsize',11),11,7,36)
        start = integer(opts.get('start',1),1,0,100000000)
        style = str(opts.get('style','numeric'))
        for i,p in enumerate(doc):
            text = f'{start+i}' if style == 'numeric' else f'Page {start+i} of {start+n-1}'
            area = p.rect
            tw = fitz.get_text_length(text,fontname='helv',fontsize=size)
            x = 20 if pos.endswith('left') else (area.width-tw-20 if pos.endswith('right') else (area.width-tw)/2)
            y = 22+size if pos.startswith('top') else area.height-22
            p.insert_text(fitz.Point(x,y), text, fontsize=size, fontname='helv', color=(.22,.27,.34),overlay=True)
    elif tool == 'watermark':
        text = str(opts.get('text', 'CONFIDENTIAL')).strip()
        if not text:
            doc.close()
            raise ToolError('Enter watermark text.')
        size = integer(opts.get('fontsize',48),48,9,140)
        opacity = float_number(opts.get('opacity',.20),.20,.05,1)
        angle = int(opts.get('angle',-45))
        if angle not in (-45,0,45):
            doc.close()
            raise ToolError('Watermark angle must be -45, 0, or 45.')
        for p in doc:
            width, height = p.rect.width, p.rect.height
            used_size = min(size, max(12,int(min(width,height)*.16)))
            text_width = fitz.get_text_length(text, fontsize=used_size,fontname='helv')
            max_width = min(width,height)*1.1 if angle else width*.85
            if text_width > max_width:
                used_size *= max_width/text_width
                text_width = fitz.get_text_length(text, fontsize=used_size,fontname='helv')
            radians = math.radians(angle)
            dx = text_width * math.cos(radians)
            dy = -text_width * math.sin(radians)
            point = fitz.Point((width-dx)/2, (height-dy)/2)
            morph = (point, fitz.Matrix(1,1).prerotate(angle)) if angle else None
            p.insert_text(point,text,fontsize=used_size,fontname='helv',color=(.40,.44,.51),
                          fill_opacity=opacity,overlay=True,morph=morph)
    elif tool == 'crop':
        margins = [float_number(opts.get(k,0),0,0,10000)*72/25.4 for k in ('left','top','right','bottom')]
        l,t,r,b = margins
        for p in doc:
            box = p.cropbox
            if l+r >= box.width-12 or t+b >= box.height-12:
                doc.close()
                raise ToolError('Crop margins leave no usable page area. Reduce the margins.')
            p.set_cropbox(fitz.Rect(box.x0+l,box.y0+t,box.x1-r,box.y1-b))
    elif tool == 'unlock':
        if not src.is_file():
            doc.close()
            raise ToolError('PDF not found.')
    elif tool == 'protect':
        upw = str(opts.get('user_password',''))
        opw = str(opts.get('owner_password','')) or upw
        if not upw:
            doc.close()
            raise ToolError('Enter a password for the protected PDF.')
        perms = fitz.PDF_PERM_ACCESSIBILITY
        if opts.get('allow_print',True):
            perms |= fitz.PDF_PERM_PRINT | fitz.PDF_PERM_PRINT_HQ
        if opts.get('allow_copy',False):
            perms |= fitz.PDF_PERM_COPY
        if opts.get('allow_edit',False):
            perms |= fitz.PDF_PERM_MODIFY | fitz.PDF_PERM_ANNOTATE | fitz.PDF_PERM_FORM | fitz.PDF_PERM_ASSEMBLE
        save_pdf(doc,out,encrypted=True,user_pw=upw,owner_pw=opw,permissions=perms)
        return [out]
    else:
        doc.close()
        raise ToolError(f'Unknown PDF task: {tool}')
    save_pdf(doc,out)
    return [out]


def organize_combined(inputs: list[Path], opts: dict, dest: Path):
    """Build one output PDF from arbitrarily ordered pages across source PDFs."""
    pages = opts.get('pages')
    if not isinstance(pages, list) or not pages:
        raise ToolError('Keep at least one page in the organized document.')
    docs = []
    result = fitz.open()
    try:
        for src in inputs:
            docs.append(get_pdf(src, str(opts.get('password', ''))))
        used = set()
        for item in pages:
            if not isinstance(item, dict):
                raise ToolError('Invalid page selection.')
            try:
                file_index = int(item['file'])
                page_index = int(item['i'])
                angle = int(item.get('rot', 0))
            except (KeyError, ValueError, TypeError) as ex:
                raise ToolError('Invalid page selection.') from ex
            if not 0 <= file_index < len(docs) or not 0 <= page_index < docs[file_index].page_count:
                raise ToolError('Page selection references an invalid source file or page.')
            if angle not in (0,90,180,270):
                raise ToolError('Page rotation must be 0, 90, 180 or 270 degrees.')
            key = (file_index, page_index)
            if key in used:
                raise ToolError('The same source page appears more than once.')
            used.add(key)
            result.insert_pdf(docs[file_index], from_page=page_index, to_page=page_index,
                              links=True, annots=True)
            if angle:
                new_page = result[-1]
                new_page.set_rotation((new_page.rotation + angle) % 360)
        save_pdf(result, dest)
    except Exception:
        result.close()
        raise
    finally:
        for doc in docs:
            doc.close()


def process(tool: str, inputs: list[Path], names: list[str], opts: dict, tmp: Path) -> tuple[Path,str]:
    if tool not in ALL_TOOLS:
        raise ToolError('Unknown tool.')
    if not inputs:
        raise ToolError('Choose at least one input file.')
    outdir = tmp/'outputs'
    outdir.mkdir(exist_ok=True)
    results = []
    if tool == 'merge':
        combined = fitz.open()
        try:
            for src in inputs:
                with get_pdf(src,str(opts.get('password',''))) as doc:
                    combined.insert_pdf(doc, links=True, annots=True, widgets=True)
            output = outdir/'merged.pdf'
            save_pdf(combined,output)
        except Exception:
            combined.close()
            raise
        results.append(output)
    elif tool == 'organize':
        target = outdir/'organized.pdf'
        organize_combined(inputs, opts, target)
        results.append(target)
    elif tool in IMAGE_TOOLS:
        target = outdir/('scanned.pdf' if tool == 'scan-pdf' else 'images.pdf')
        write_image_pdf(inputs,target,opts,scan=(tool=='scan-pdf'))
        results.append(target)
    elif tool in OFFICE_TOOLS:
        for i,(src,name) in enumerate(zip(inputs,names),1):
            stem = f'{i:03d}_{clean_stem(name)}' if len(inputs)>1 else clean_stem(name)
            target = outdir / f'{stem}.pdf'
            if tool == 'html-pdf':
                sanitize_html(src)
            office_to_pdf(src,target,tmp)
            results.append(target)
    elif tool == 'pdf-jpg':
        dpi = integer(opts.get('dpi',150),150,72,300)
        for j,(src,name) in enumerate(zip(inputs,names),1):
            base = f'{j:03d}_{clean_stem(name)}' if len(inputs)>1 else clean_stem(name)
            with get_pdf(src,str(opts.get('password',''))) as doc:
                for i,page in enumerate(doc):
                    pix = page.get_pixmap(matrix=fitz.Matrix(dpi/72,dpi/72),alpha=False, colorspace=fitz.csRGB)
                    with Image.frombytes('RGB', (pix.width,pix.height),pix.samples) as im:
                        target = outdir/f'{base}_page_{i+1:04d}.jpg'
                        im.save(target,'JPEG',quality=88,optimize=True)
                        results.append(target)
    else:
        for j,(src,name) in enumerate(zip(inputs,names),1):
            base = f'{j:03d}_{clean_stem(name)}' if len(inputs)>1 else clean_stem(name)
            base += {'split':'_split', 'remove':'_pages_removed', 'extract':'_extracted',
                     'organize':'_organized','compress':'_compressed','rotate':'_rotated',
                     'page-numbers':'_numbered','watermark':'_watermarked',
                     'crop':'_cropped','unlock':'_unlocked','protect':'_protected'}.get(tool,'')
            results.extend(tool_single(tool,src,outdir,opts,base))
    if not results:
        raise ToolError('No output files were produced.')
    force_zip = tool in ('pdf-jpg','split') or (tool=='extract' and bool(opts.get('separate')))
    if len(results)==1 and not force_zip:
        return results[0], results[0].name
    archive = tmp/('paperlane_results.zip')
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_STORED,allowZip64=True) as z:
        for item in results:
            z.write(item, arcname=item.name)
    return archive, archive.name
