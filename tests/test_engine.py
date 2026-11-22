"""Run from the project root: python -m pytest tests -v"""
import sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import fitz
import pytest
from PIL import Image,ImageDraw
from engine import process, ToolError,ALL_TOOLS

@pytest.fixture
def samples(tmp_path):
    pdf=tmp_path/'source.pdf'
    d=fitz.open()
    for i in range(4):
        p=d.new_page(width=400,height=500)
        p.insert_text((40,60),f'Unique source page {i+1}',fontsize=20)
    d.save(pdf);d.close()
    pdf2=tmp_path/'other.pdf'
    d=fitz.open();d.new_page().insert_text((30,30),'Another PDF');d.save(pdf2);d.close()
    image=tmp_path/'photo.jpg'
    img=Image.new('RGB',(300,400),'white')
    ImageDraw.Draw(img).text((20,20),'Private local image',fill='black')
    img.save(image,quality=93)
    return pdf,pdf2,image


def call(tmp_path,tool,files,opts=None):
    output=tmp_path/('job_'+tool.replace('-','_'))
    output.mkdir(exist_ok=True)
    path,name=process(tool,files,[p.name for p in files],opts or {},output)
    assert path.exists() and path.stat().st_size>0
    return path


def test_all_tools_present():
    assert len(ALL_TOOLS)==19


def test_merge(tmp_path,samples):
    a,b,_=samples
    out=call(tmp_path,'merge',[a,b])
    with fitz.open(out) as d:assert d.page_count==5

@pytest.mark.parametrize('mode,extra,expected',[
    ('every',{},4),('chunks',{'chunk':2},2),('ranges',{'ranges':'1-2, 4'},2),
])
def test_split(tmp_path,samples,mode,extra,expected):
    import zipfile
    out=call(tmp_path,'split',[samples[0]],{'mode':mode,**extra})
    with zipfile.ZipFile(out) as z:assert len(z.namelist())==expected


def test_remove(tmp_path,samples):
    out=call(tmp_path,'remove',[samples[0]],{'ranges':'2-3'})
    with fitz.open(out) as d:
        assert d.page_count==2
        assert 'page 4' in d[1].get_text()


def test_extract(tmp_path,samples):
    out=call(tmp_path,'extract',[samples[0]],{'ranges':'1,4'})
    with fitz.open(out) as d:assert d.page_count==2


def test_organize(tmp_path,samples):
    out=call(tmp_path,'organize',[samples[0]],{'pages':[{'i':3,'rot':90},{'i':0,'rot':0}]})
    with fitz.open(out) as d:
        assert d.page_count==2 and d[0].rotation==90
        assert 'page 4' in d[0].get_text()


def test_images_to_pdf(tmp_path,samples):
    im=samples[2]
    for tool in ('jpg-pdf','scan-pdf'):
        out=call(tmp_path,tool,[im,im],{'size':'a4','effect':'document'})
        with fitz.open(out) as d:assert d.page_count==2


def test_pdf_to_jpg(tmp_path,samples):
    import zipfile
    out=call(tmp_path,'pdf-jpg',[samples[0]],{'dpi':96})
    with zipfile.ZipFile(out) as z:
        assert len(z.namelist())==4
        assert all(z.read(s).startswith(b'\xff\xd8') for s in z.namelist())


def test_compression(tmp_path,samples):
    for level in ('lossless','balanced','strong'):
        out=call(tmp_path,'compress',[samples[0]],{'level':level})
        with fitz.open(out) as d:assert d.page_count==4 and 'source' in d[0].get_text()


def test_rotate(tmp_path,samples):
    out=call(tmp_path,'rotate',[samples[0]],{'scope':'odd','angle':90})
    with fitz.open(out) as d:assert [p.rotation for p in d]==[90,0,90,0]


def test_page_numbers(tmp_path,samples):
    out=call(tmp_path,'page-numbers',[samples[0]],{'style':'full','start':2})
    with fitz.open(out) as d:
        assert 'Page 2 of 5' in d[0].get_text()


def test_watermark(tmp_path,samples):
    out=call(tmp_path,'watermark',[samples[0]],{'text':'SECRET','angle':0})
    with fitz.open(out) as d:assert 'SECRET' in d[0].get_text()


def test_crop(tmp_path,samples):
    out=call(tmp_path,'crop',[samples[0]],{'left':10,'top':10,'right':10,'bottom':10})
    with fitz.open(out) as d:
        assert d[0].rect.width<400 and d[0].rect.height<500


def test_protect_unlock(tmp_path,samples):
    locked=call(tmp_path,'protect',[samples[0]],{'user_password':'hello123','owner_password':'owner456'})
    d=fitz.open(locked)
    assert d.needs_pass
    assert not d.authenticate('wrong')
    assert d.authenticate('hello123')
    d.close()
    unlocked=call(tmp_path,'unlock',[locked],{'password':'hello123'})
    with fitz.open(unlocked) as d:assert not d.needs_pass and d.page_count==4


def test_invalid_ranges(tmp_path,samples):
    with pytest.raises(ToolError):call(tmp_path,'remove',[samples[0]],{'ranges':'999'})


def test_batch(tmp_path,samples):
    import zipfile
    a,b,_=samples
    out=call(tmp_path,'rotate',[a,b],{'angle':180})
    with zipfile.ZipFile(out) as z:assert len(z.namelist())==2


def test_local_http_api(tmp_path,samples):
    from fastapi.testclient import TestClient
    from app import app
    with TestClient(app,base_url='http://127.0.0.1:8765') as client:
        assert client.get('/api/health').json()['tools']==19
        forbidden=client.post('/api/run/merge')
        assert forbidden.status_code==403
        pdf=samples[0]
        payload={'files':(pdf.name,pdf.read_bytes(),'application/pdf')}
        r=client.post('/api/inspect',headers={'X-Paperlane-Local':'1'},files=payload)
        assert r.status_code==200,r.text
        assert r.json()['total']==4
        r=client.post('/api/run/rotate',headers={'X-Paperlane-Local':'1'},
                      files=payload,data={'options':'{"angle":90}'})
        assert r.status_code==200,r.text
        job=r.json()
        download=client.get(job['download_url'])
        assert download.status_code==200 and download.content.startswith(b'%PDF')


def test_office_html(tmp_path):
    from engine import find_libreoffice
    if not find_libreoffice():pytest.skip('LibreOffice not installed')
    src=tmp_path/'sample.html'
    src.write_text('<html><body><h1>Local HTML</h1><p>A private report.</p></body></html>')
    out=call(tmp_path,'html-pdf',[src])
    with fitz.open(out) as d: assert d.page_count>=1


def test_office_formats(tmp_path):
    from engine import find_libreoffice
    if not find_libreoffice():pytest.skip('LibreOffice not installed')
    import docx,pptx,openpyxl
    word=tmp_path/'sample.docx'
    d=docx.Document();d.add_paragraph('Offline private Word content');d.save(word)
    presentation=tmp_path/'sample.pptx'
    p=pptx.Presentation();slide=p.slides.add_slide(p.slide_layouts[5]);slide.shapes.title.text='Offline PPT';p.save(presentation)
    spreadsheet=tmp_path/'sample.xlsx'
    w=openpyxl.Workbook();w.active['A1']='Local Excel';w.save(spreadsheet)
    for tool,path in [('word-pdf',word),('powerpoint-pdf',presentation),('excel-pdf',spreadsheet)]:
        out=call(tmp_path,tool,[path])
        with fitz.open(out) as result:assert result.page_count>=1
