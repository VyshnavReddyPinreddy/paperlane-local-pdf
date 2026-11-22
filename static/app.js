'use strict';

const icons = {
  merge:'<path d="M8 3H5a2 2 0 0 0-2 2v11a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-3"/><path d="M9 7h10a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H9a2 2 0 0 1-2-2V9a2 2 0 0 1 2-2Z"/><path d="M11 14h6m-3-3v6"/>',
  split:'<circle cx="6" cy="6" r="2"/><circle cx="6" cy="18" r="2"/><path d="M8 8l11 11M14 12l5-5M8 16l3-3"/>',
  remove:'<path d="M7 3h7l4 4v14H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2Z"/><path d="M14 3v5h4M9 12l6 6M15 12l-6 6"/>',
  extract:'<rect x="4" y="4" width="11" height="15" rx="2"/><path d="M9 9h11v12H9M12 14h5M14.5 11.5v5"/>',
  organize:'<rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><path d="M14 17.5h7M17.5 14v7"/>',
  scan:'<path d="M4 8V5a2 2 0 0 1 2-2h3M15 3h3a2 2 0 0 1 2 2v3M20 16v3a2 2 0 0 1-2 2h-3M9 21H6a2 2 0 0 1-2-2v-3M3 12h18M8 16h8"/>',
  compress:'<path d="m8 3 0 5-5 0M16 3v5h5M3 8l6-6M21 8l-6-6M8 21v-5H3M16 21v-5h5M3 16l6 6m12-6-6 6"/>',
  image:'<rect x="3" y="4" width="18" height="16" rx="2"/><circle cx="8.5" cy="9" r="2"/><path d="m4 18 6-6 4 4 3-3 4 4"/>',
  word:'<path d="M7 3h9l4 4v14H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2Z"/><path d="M16 3v5h4M8.5 12l1.5 5 2-4 2 4 1.5-5"/>',
  presentation:'<path d="M3 3h18v12H3zM12 15v6m-5 0h10M7 7h4v4H7zM14 8h4M14 11h4"/>',
  spreadsheet:'<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M3 10h18M10 4v16M3 15h18"/>',
  html:'<rect x="4" y="3" width="16" height="18" rx="2"/><path d="m10 9-3 3 3 3m4-6 3 3-3 3"/>',
  rotate:'<path d="M21 12a9 9 0 1 1-2.3-6M21 3v6h-6"/><path d="M9 9h5v6H9z"/>',
  numbers:'<path d="M4 5h7M4 11h7M4 17h7M16 5h4v5h-4V5Zm0 8h4v5h-4v-5Z"/>',
  watermark:'<path d="M4 19h16M7 15l3-10h4l3 10M8 12h8M3 22l18-18"/>',
  crop:'<path d="M6 2v15a2 2 0 0 0 2 2h14M2 6h15a2 2 0 0 1 2 2v14"/>',
  unlock:'<rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 7.7-1.5"/><circle cx="12" cy="16" r="1"/>',
  protect:'<rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4M12 15v2"/>',
};
const svg = name => `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${icons[name]||icons.word}</svg>`;
const categories = [
  {name:'Organize PDF', slug:'organize', color:'blue', items:[
    ['merge','Merge PDF','Combine several PDFs into a single file.','merge'],
    ['split','Split PDF','Separate PDF pages into new files.','split'],
    ['remove','Remove pages','Delete selected pages from a PDF.','remove'],
    ['extract','Extract pages','Save just the pages you need.','extract'],
    ['organize','Organize PDF','Reorder, rotate, or delete pages.','organize'],
    ['scan-pdf','Scan to PDF','Make a PDF from photos or scans.','scan']]},
  {name:'Optimize PDF', slug:'optimize', color:'green', items:[
    ['compress','Compress PDF','Reduce file size while keeping text.','compress']]},
  {name:'Convert to PDF', slug:'to-pdf', color:'amber', items:[
    ['jpg-pdf','JPG to PDF','Turn images into a PDF document.','image'],
    ['word-pdf','Word to PDF','Convert DOC and DOCX documents.','word'],
    ['powerpoint-pdf','PowerPoint to PDF','Convert presentations to PDF.','presentation'],
    ['excel-pdf','Excel to PDF','Convert spreadsheets to PDF.','spreadsheet'],
    ['html-pdf','HTML to PDF','Convert an HTML file to PDF.','html']]},
  {name:'Convert from PDF', slug:'from-pdf', color:'violet', items:[
    ['pdf-jpg','PDF to JPG','Export each PDF page as a JPG.','image']]},
  {name:'Edit PDF', slug:'edit', color:'cyan', items:[
    ['rotate','Rotate PDF','Rotate all or selected pages.','rotate'],
    ['page-numbers','Add page numbers','Number PDF pages automatically.','numbers'],
    ['watermark','Add watermark','Place a text watermark on pages.','watermark'],
    ['crop','Crop PDF','Trim the visible PDF page margins.','crop']]},
  {name:'PDF Security', slug:'security', color:'rose', items:[
    ['unlock','Unlock PDF','Remove a password you know.','unlock'],
    ['protect','Protect PDF','Add AES-256 PDF password protection.','protect']]}
];
const tools = Object.fromEntries(categories.flatMap(c=>c.items.map(([id,title,description,icon]) => [id,{id,title,description,icon,category:c.name,color:c.color}])));
const pdfTools = new Set(['merge','split','remove','extract','organize','compress','pdf-jpg','rotate','page-numbers','watermark','crop','unlock','protect']);
const officeTools = new Set(['word-pdf','powerpoint-pdf','excel-pdf','html-pdf']);
const imageTools = new Set(['jpg-pdf','scan-pdf']);
const acceptMap = {'word-pdf':'.doc,.docx,.odt,.rtf','powerpoint-pdf':'.ppt,.pptx,.odp','excel-pdf':'.xls,.xlsx,.ods,.csv','html-pdf':'.html,.htm','jpg-pdf':'image/jpeg,image/png,image/webp,image/bmp,image/tiff','scan-pdf':'image/jpeg,image/png,image/webp,image/bmp,image/tiff'};
const $ = id => document.getElementById(id);
const escapeHtml = value => String(value).replace(/[&<>"']/g, c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let state = {tool:null,files:[],pages:[],totalPages:0,nextStart:0,officeAvailable:false,working:false,previewBusy:false,previewGeneration:0,previewComplete:false,pendingFileStart:null,dragIndex:null,latestDownload:null,removed:new Set()};

function renderDashboard(){
  $('categoryNav').innerHTML=categories.map((c,i)=>`<a class="category-link ${i===0?'active':''}" href="#cat-${c.slug}" data-category="${c.slug}">${c.name}</a>`).join('');
  $('toolSections').innerHTML=categories.map(c=>`<section class="tool-group" id="cat-${c.slug}" data-category-section="${c.slug}"><div class="group-heading"><h3>${c.name}</h3><span class="group-count">${c.items.length}</span><span class="group-line"></span></div><div class="cards-grid">${c.items.map(([id,title,desc,icon])=>`<button type="button" class="tool-card" data-tool="${id}"><span class="tool-icon ${c.color}">${svg(icon)}</span><strong>${title}</strong><span>${desc}</span></button>`).join('')}</div></section>`).join('');
  document.querySelectorAll('.tool-card').forEach(b=>b.addEventListener('click',()=>{location.hash='tool-'+b.dataset.tool; openTool(b.dataset.tool)}));
  document.querySelectorAll('.category-link').forEach(a=>a.addEventListener('click',()=>{
    document.querySelectorAll('.category-link').forEach(x=>x.classList.toggle('active',x===a));
  }));
}
function filterTools(){
  const q=$('toolSearch').value.toLowerCase().trim();
  let visible=0;
  document.querySelectorAll('.tool-group').forEach(section=>{
    let found=0;
    section.querySelectorAll('.tool-card').forEach(b=>{
      const t=tools[b.dataset.tool];
      const match=(!q || (t.title+' '+t.description+' '+t.category).toLowerCase().includes(q));
      b.hidden=!match;
      if(match)found++;
    });
    section.hidden=found===0;
    section.querySelector('.group-count').textContent=found;
    visible+=found;
  });
  $('visibleCount').textContent=visible;
  $('emptySearch').hidden=visible!==0;
}
function field(label,name,placeholder='',value='',hint='',type='text'){
  return `<div class="setting-group"><label for="s_${name}">${label}</label><input id="s_${name}" name="${name}" type="${type}" placeholder="${escapeHtml(placeholder)}" value="${escapeHtml(value)}">${hint?`<span class="setting-hint">${hint}</span>`:''}</div>`;
}
function number(label,name,value,min,max,hint=''){
  return `<div class="setting-group"><label for="s_${name}">${label}</label><input id="s_${name}" name="${name}" type="number" value="${value}" min="${min}" max="${max}">${hint?`<span class="setting-hint">${hint}</span>`:''}</div>`;
}
function selection(label,name,options,selected){
  return `<div class="setting-group"><label for="s_${name}">${label}</label><select id="s_${name}" name="${name}">${options.map(([v,n])=>`<option value="${v}" ${selected===v?'selected':''}>${n}</option>`).join('')}</select></div>`;
}
function check(label,name,checked){return `<div class="setting-group check-group"><label><input type="checkbox" name="${name}" ${checked?'checked':''}><span>${label}</span></label></div>`;}
function when(name,val,html){return `<div data-when="${name}:${val}">${html}</div>`;}
function toolOptions(id){
  let s='';
  switch(id){
    case 'merge': s='<div class="setting-note">Files will merge in the order shown. Use the arrows beside each file to rearrange them.</div>'; break;
    case 'split': s=selection('Split method','mode',[['every','Every page'],['chunks','Every N pages'],['ranges','Custom page ranges']],'every')+when('mode','chunks',number('Pages per PDF','chunk',2,1,10000000))+when('mode','ranges',field('Page ranges','ranges','1-3, 4-7','', 'Each comma-separated group becomes a separate PDF.')); break;
    case 'remove': s=field('Pages to remove','ranges','2, 5-7','', 'Click the thumbnails below or enter page numbers, e.g. 1, 3-6. Crossed pages will be deleted.'); break;
    case 'extract': s=field('Pages to extract','ranges','1-3, 5, 8-10','', 'Leave this blank to extract ALL pages.')+'<button type="button" class="outline-small" id="extractAllBtn">Extract all pages</button>'+check('Save each comma-separated range as its own PDF','separate',false); break;
    case 'organize': s='<div class="setting-note">Add one or more PDFs. Every page appears below in a single grid. Drag pages between files to reorder, ↻ rotates individual pages and × deletes pages. Save to produce one combined PDF.</div>';break;
    case 'compress': s=selection('Compression level','level',[['lossless','Lossless — retain original quality'],['balanced','Balanced — optimize embedded images'],['strong','Strong — smaller embedded images']],'balanced')+'<div class="setting-note">Selectable text and vector graphics are preserved. PDFs with little image content may not shrink significantly. Results can occasionally be larger.</div>';break;
    case 'jpg-pdf': s=selection('Page size','size',[['a4','A4'],['letter','US Letter'],['original','Match image dimensions']],'a4')+number('Margin (points)','margin',16,0,80);break;
    case 'scan-pdf': s=selection('Page size','size',[['a4','A4'],['letter','US Letter'],['original','Match image dimensions']],'a4')+selection('Image processing','effect',[['color','Keep original colors'],['grayscale','Grayscale'],['document','High contrast grayscale']],'document')+number('Margin (points)','margin',16,0,80)+'<div class="setting-note">Add photos or scanned image files, or use Take photo on a supported device. Physical scanner control is not included.</div>';break;
    case 'pdf-jpg': s=selection('Export resolution','dpi',[['96','96 DPI — quick preview'],['150','150 DPI — balanced'],['200','200 DPI — higher detail'],['300','300 DPI — print quality']],'150')+'<div class="setting-note">Every page is exported as a JPG. Multiple images are downloaded together as a ZIP.</div>';break;
    case 'rotate': s=selection('Rotation','angle',[['90','90° clockwise'],['180','180°'],['270','90° counter-clockwise']],'90')+selection('Apply to','scope',[['all','All pages'],['odd','Odd-numbered pages'],['even','Even-numbered pages'],['ranges','Selected pages']],'all')+when('scope','ranges',field('Page numbers','ranges','1, 3-6'));break;
    case 'page-numbers': s=selection('Position','position',[['bottom-center','Bottom center'],['bottom-left','Bottom left'],['bottom-right','Bottom right'],['top-center','Top center'],['top-left','Top left'],['top-right','Top right']],'bottom-center')+selection('Format','style',[['numeric','1, 2, 3…'],['full','Page 1 of 10']],'numeric')+number('Start numbering at','start',1,0,100000000)+number('Font size','fontsize',11,7,36);break;
    case 'watermark': s=field('Watermark text','text','CONFIDENTIAL','CONFIDENTIAL')+selection('Angle','angle',[['-45','Diagonal /'],['0','Horizontal'],['45','Diagonal \\'] ],'-45')+number('Font size','fontsize',48,9,140)+selection('Opacity','opacity',[['0.10','Very light (10%)'],['0.20','Light (20%)'],['0.35','Medium (35%)'],['0.55','Strong (55%)'],['0.80','Dark (80%)']],'0.20');break;
    case 'crop': s='<div class="setting-note">Specify how much to trim from each edge, in millimeters. This changes the visible crop box; it does not permanently erase hidden content.</div>'+number('Left (mm)','left',5,0,500)+number('Top (mm)','top',5,0,500)+number('Right (mm)','right',5,0,500)+number('Bottom (mm)','bottom',5,0,500);break;
    case 'unlock': s=field('Current PDF password','password','Enter your known password','','Only PDFs you are authorized to open can be unlocked.','password');break;
    case 'protect': s=field('New PDF opening password','user_password','Required','','Used to open the protected PDF.','password')+field('Owner password','owner_password','Recommended: different from opening password','','Keep this password to manage permissions later. If blank, the opening password is also used.','password')+check('Allow printing','allow_print',true)+check('Allow copying content','allow_copy',false)+check('Allow editing','allow_edit',false);break;
    default: if(officeTools.has(id)){s='<div class="setting-note">Conversion uses LibreOffice installed on your own computer. Your document will not be sent to an online conversion API.</div>';}break;
  }
  if(pdfTools.has(id) && id!=='unlock'){
    s+='<hr class="setting-divider">'+field('Source PDF password (if needed)','password','Leave empty unless protected','','For password-protected input PDFs. Use the same password for all selected files.','password');
  }
  return s;
}
function applyVisibility(){
  const form=$('settingsForm');
  form.querySelectorAll('[data-when]').forEach(node=>{
    const [name,val]=node.dataset.when.split(':');
    node.hidden=(form.elements[name]?.value !== val);
  });
}
const singleFileTools = new Set(['split','remove','extract']);
const previewTools = new Set(['organize','remove','extract']);
function openTool(id){
  const t=tools[id];if(!t)return;
  state.previewGeneration++;
  state={...state,tool:id,files:[],pages:[],totalPages:0,nextStart:0,previewBusy:false,previewComplete:false,removed:new Set(),dragIndex:null,latestDownload:null};
  $('dashboard').hidden=true;$('workspace').hidden=false;
  $('workspaceCategory').textContent=t.category.toUpperCase();
  $('workspaceTitle').textContent=t.title;$('workspaceDesc').textContent=t.description;
  $('workspaceIcon').className=`active-icon ${t.color}`;$('workspaceIcon').innerHTML=svg(t.icon);
  $('settingsForm').innerHTML=toolOptions(id);
  $('settingsForm').addEventListener('change',applyVisibility);
  applyVisibility();
  const accept=acceptMap[id]||'.pdf';
  $('fileInput').accept=accept;$('folderInput').accept=accept;
  $('fileInput').multiple=!singleFileTools.has(id);
  $('acceptHint').textContent=singleFileTools.has(id)?'Choose exactly one PDF':imageTools.has(id)?'JPG, PNG, WebP, TIFF or BMP images':officeTools.has(id)?accept.replaceAll('.', '').toUpperCase().replaceAll(',',', '):'PDF files';
  $('cameraBtn').hidden=id!=='scan-pdf';
  $('addFolder').hidden=singleFileTools.has(id);
  $('addMore').hidden=singleFileTools.has(id);
  $('pageOrganizer').hidden=!previewTools.has(id);
  $('previewTitle').textContent=id==='organize'?'Arrange pages':id==='remove'?'Select pages to remove':'Preview pages';
  $('previewHint').textContent=id==='organize'?'Drag to reorder; rotate or delete each page. Pages from all PDFs appear together.':id==='remove'?'Click any page to mark or unmark it for removal. The field on the right updates automatically.':'Leave page numbers blank to extract the whole document.';
  $('restorePages').textContent=id==='remove'?'Clear selection':'Reset page changes';
  $('runLabel').textContent=id==='merge'?'Merge PDFs':id==='organize'?'Save organized PDF':id==='pdf-jpg'?'Convert to JPG':id==='remove'?'Remove selected pages':id==='extract'?'Extract pages':'Process files';
  $('officeNote').textContent=officeTools.has(id)?(state.officeAvailable?'LibreOffice detected on this computer.':'LibreOffice desktop installation required.'):'Output saved through your browser.';
  $('alertBox').hidden=true;$('successBox').hidden=true;
  if(id==='extract')$('extractAllBtn').addEventListener('click',()=>{$('settingsForm').elements.ranges.value='';});
  renderFiles();window.scrollTo({top:0,behavior:'instant'});
}
function goHome(){state.previewGeneration++;state.tool=null;location.hash='tools';$('workspace').hidden=true;$('dashboard').hidden=false;window.scrollTo({top:0,behavior:'instant'});}
function allowed(file){
  const ext='.'+(file.name.split('.').pop()||'').toLowerCase();
  const acceptable=imageTools.has(state.tool)?['.jpg','.jpeg','.png','.webp','.bmp','.tif','.tiff']:
    officeTools.has(state.tool)?acceptMap[state.tool].split(','):['.pdf'];
  return acceptable.includes(ext);
}
function addFiles(list){
  if(!state.tool||state.working)return;
  const all=Array.from(list).filter(f=>f instanceof File);
  const good=all.filter(allowed);
  if(good.length!==all.length)showError(`${all.length-good.length} unsupported file(s) were skipped.`);
  else $('alertBox').hidden=true;
  if(singleFileTools.has(state.tool)){
    if(good.length>1){showError('This tool accepts one PDF only. Please select one file.');return;}
    if(!good.length)return;
    state.files=[good[0]];
    state.removed=new Set();
    resetOrganizer();
    loadPreview();
  }else if(state.tool==='organize'){
    const from=state.files.length;
    state.files.push(...good);
    if(good.length){if(state.previewBusy)state.pendingFileStart=state.pendingFileStart===null?from:Math.min(state.pendingFileStart,from);else loadPreview(from);}
  }else state.files.push(...good);
  $('successBox').hidden=true;renderFiles();
}
function formatSize(bytes){if(!bytes)return'0 B';const units=['B','KB','MB','GB','TB'];const i=Math.min(Math.floor(Math.log(bytes)/Math.log(1024)),4);return (bytes/(1024**i)).toFixed(i===0?0:1)+' '+units[i];}
function renderFiles(){
  $('fileCount').textContent=state.files.length;
  $('sizeCount').textContent=state.files.length?formatSize(state.files.reduce((s,f)=>s+f.size,0)):'';
  $('fileList').innerHTML=state.files.length?state.files.map((f,i)=>{
    const kind=imageTools.has(state.tool)?'image':officeTools.has(state.tool)?'office':'';
    const ext=(f.name.split('.').pop()||'PDF').toUpperCase().slice(0,4);
    return `<div class="file-entry"><div class="entry-icon ${kind}">${escapeHtml(ext)}</div><div class="entry-info"><b title="${escapeHtml(f.name)}">${escapeHtml(f.name)}</b><span>${formatSize(f.size)} · File ${i+1}</span></div><div class="entry-controls">${state.files.length>1&&state.tool!=='organize'?`<button type="button" class="icon-button" data-file="up:${i}" aria-label="Move file up" ${i===0?'disabled':''}>↑</button><button type="button" class="icon-button" data-file="down:${i}" aria-label="Move file down" ${i===state.files.length-1?'disabled':''}>↓</button>`:''}<button type="button" class="icon-button remove" data-file="remove:${i}" aria-label="Remove file" title="Remove">×</button></div></div>`;
  }).join(''):'<div class="empty-files">Your files will appear here, in the order you selected them.</div>';
  document.querySelectorAll('[data-file]').forEach(b=>b.addEventListener('click',()=>{
    const [act,idx]=b.dataset.file.split(':');const i=+idx;
    if(state.previewBusy)return showError('Please let the page previews finish loading before changing the file list.');
    if(act==='remove'){
      state.files.splice(i,1);
      if(state.tool==='organize'){
        state.pages=state.pages.filter(p=>p.file!==i).map(p=>({...p,file:p.file>i?p.file-1:p.file}));
        state.totalPages=state.pages.length;state.nextStart=state.pages.length;
        renderPages();
      } else if(previewTools.has(state.tool)){resetOrganizer();}
    }
    if(act==='up'&&i>0)[state.files[i-1],state.files[i]]=[state.files[i],state.files[i-1]];
    if(act==='down'&&i<state.files.length-1)[state.files[i+1],state.files[i]]=[state.files[i],state.files[i+1]];
    renderFiles();
  }));
  $('runButton').disabled=state.working||!state.files.length||(state.tool==='organize'&&(!state.previewComplete||state.previewBusy));
}
function showError(message){$('alertBox').textContent=message;$('alertBox').hidden=false;$('successBox').hidden=true;}
function options(){
  const data={};
  for(const el of $('settingsForm').elements){if(!el.name)continue;data[el.name]=el.type==='checkbox'?el.checked:el.value;}
  return data;
}
function toggleLoading(show,title,subtitle){
  state.working=show;
  $('loadingOverlay').hidden=!show;
  $('loadingTitle').textContent=title||'Processing your files…';
  $('loadingSubtitle').textContent=subtitle||'Working entirely on your computer. Larger documents may take a while.';
  renderFiles();
}
async function run(){
  if(!state.tool||!state.files.length||state.working)return;
  if(singleFileTools.has(state.tool)&&state.files.length!==1){showError('Choose exactly one PDF.');return;}
  if(state.tool==='merge'&&state.files.length<2){showError('Choose at least two PDFs to merge.');return;}
  const data=new FormData();
  for(const file of state.files)data.append('files',file,file.name);
  const opts=options();
  if(state.tool==='organize'){
    if(state.previewBusy||!state.previewComplete){showError('Wait until all page previews have finished loading.');return;}
    opts.pages=state.pages.map(p=>({file:p.file,i:p.i,rot:p.rot}));
    if(!opts.pages.length){showError('Keep at least one page in the document.');return;}
  }
  if(state.tool==='remove'){
    if(!String(opts.ranges||'').trim()){showError('Select at least one page to remove.');return;}
    try{parsePageNumbers(opts.ranges,state.totalPages||Infinity);}catch(ex){showError(ex.message);return;}
  }
  data.append('options',JSON.stringify(opts));
  toggleLoading(true,`Working on ${state.files.length} file${state.files.length===1?'':'s'}…`);
  $('alertBox').hidden=true;$('successBox').hidden=true;
  try{
    const response=await fetch(`/api/run/${state.tool}`,{method:'POST',headers:{'X-Paperlane-Local':'1'},body:data});
    let result={};try{result=await response.json();}catch{}
    if(!response.ok||!result.ok)throw new Error(result.error||`Processing failed (HTTP ${response.status}).`);
    state.latestDownload=result.download_url;
    const a=document.createElement('a');a.href=result.download_url;a.download=result.filename;document.body.append(a);a.click();a.remove();
    $('successBox').hidden=false;
    $('successBox').innerHTML=`Done. <strong>${escapeHtml(result.filename)}</strong> (${formatSize(result.bytes)}) is ready. <a id="againDownload" href="${escapeHtml(result.download_url)}">Download again</a>.`;
  }catch(err){showError(err.message||'Unexpected local processing error.');}
  finally{toggleLoading(false);}
}
function parsePageNumbers(text,n){
  const result=new Set();
  for(const segment of text.split(',')){
    const part=segment.trim();if(!part)throw new Error('Invalid empty page range.');
    const m=part.match(/^(\d+)\s*(?:-\s*(\d+))?$/);
    if(!m)throw new Error(`Invalid page range: ${part}`);
    const a=Number(m[1]),b=Number(m[2]||m[1]);
    if(a<1||b<a||b>n)throw new Error(`Page range ${part} must be between 1 and ${n}.`);
    for(let i=a;i<=b;i++)result.add(i-1);
  }
  return result;
}
function selectedRanges(indices){
  const sorted=[...indices].sort((a,b)=>a-b).map(x=>x+1);if(!sorted.length)return '';
  const ranges=[];let a=sorted[0],b=a;
  for(const value of sorted.slice(1)){
    if(value===b+1)b=value;
    else{ranges.push(a===b?`${a}`:`${a}-${b}`);a=b=value;}
  }
  ranges.push(a===b?`${a}`:`${a}-${b}`);
  return ranges.join(', ');
}
function syncRemoveFromField(){
  if(state.tool!=='remove')return;
  const input=$('settingsForm').elements.ranges;
  try{
    const value=input.value.trim();
    state.removed=value?parsePageNumbers(value,state.totalPages||Infinity):new Set();
    input.setCustomValidity('');$('alertBox').hidden=true;
  }catch(err){input.setCustomValidity(err.message);return;}
  renderPages();
}
function resetOrganizer(){
  state.previewGeneration++;state.pages=[];state.totalPages=0;state.nextStart=0;state.previewBusy=false;state.previewComplete=false;state.pendingFileStart=null;
  $('thumbGrid').innerHTML='';$('pageCount').textContent='';$('loadedPages').textContent='';renderPageFooter();
}
async function loadPreview(fromFile=0){
  if(!previewTools.has(state.tool)||!state.files.length||state.previewBusy)return;
  const gen=++state.previewGeneration;
  const files=state.files.slice();
  const mode=state.tool;
  state.previewBusy=true;state.previewComplete=false;renderFiles();
  try{
    for(let f=fromFile;f<files.length;f++){
      let start=0,total=Infinity;
      while(start<total){
        if(gen!==state.previewGeneration||mode!==state.tool)return;
        $('loadedPages').textContent=`Loading ${escapeHtml(files[f].name)} — ${start} pages…`;
        const form=new FormData();form.append('files',files[f],files[f].name);form.append('start',String(start));form.append('count','36');form.append('password',options().password||'');
        const res=await fetch('/api/inspect',{method:'POST',headers:{'X-Paperlane-Local':'1'},body:form});
        const data=await res.json();if(!res.ok||!data.ok)throw new Error(data.error||'Could not preview PDF pages.');
        if(gen!==state.previewGeneration||mode!==state.tool)return;
        total=data.total;
        if(!data.images.length)break;
        state.pages.push(...data.images.map(item=>({...item,file:f,rot:0})));
        state.nextStart=state.pages.length;
        state.totalPages=mode==='organize'?state.pages.length:total;
        start+=data.images.length;
        renderPages();
        await new Promise(resolve=>setTimeout(resolve,0));
      }
    }
    if(gen===state.previewGeneration){
      state.previewComplete=true;
      state.totalPages=state.pages.length;
      renderPages();$('alertBox').hidden=true;
    }
  }catch(err){if(gen===state.previewGeneration)showError(err.message||'Could not load previews.');}
  finally{if(gen===state.previewGeneration){state.previewBusy=false;renderPageFooter();renderFiles();if(state.pendingFileStart!==null){const next=state.pendingFileStart;state.pendingFileStart=null;loadPreview(next);}}}
}
function renderPageFooter(){
  $('pageCount').textContent=state.totalPages?`(${state.totalPages} pages)`:'';
  $('loadedPages').textContent=state.previewBusy?`Loading previews… ${state.nextStart} pages ready`:state.totalPages?`${state.pages.length} pages ready`:'';
  // Previews are loaded automatically; no silent remainder can bypass user edits.
  $('loadMore').hidden=true;$('loadAll').hidden=true;
}
function renderPages(){
  $('thumbGrid').innerHTML=state.pages.map((p,i)=>{
    const selectable=state.tool==='remove';
    const marked=selectable&&state.removed.has(p.i);
    const name=state.files[p.file]?.name||'PDF';
    const source=state.tool==='organize'?`<span class="page-source" title="${escapeHtml(name)}">${escapeHtml(name)}</span>`:'';
    const actions=state.tool==='organize'?`<div class="tile-actions"><button type="button" data-page-action="rotate:${i}" aria-label="Rotate page ${p.i+1}" title="Rotate clockwise">↻</button><button type="button" data-page-action="delete:${i}" aria-label="Delete page ${p.i+1}" title="Delete page">×</button></div>`:'';
    return `<div class="page-tile ${selectable?'selectable':''} ${marked?'marked':''}" ${state.tool==='organize'?'draggable="true"':''} ${selectable?`tabindex="0" role="checkbox" aria-checked="${marked}" aria-label="Remove page ${p.i+1}"`:''} data-page-tile="${i}"><div class="thumb-body"><img alt="PDF page ${p.i+1}" draggable="false" src="${p.src}" style="transform:rotate(${p.rot}deg)"></div>${source}<div class="thumb-footer"><strong>Page ${p.i+1}</strong>${actions}</div></div>`;
  }).join('');renderPageFooter();
}
function toggleRemove(i){
  const p=state.pages[i];if(!p)return;
  if(state.removed.has(p.i))state.removed.delete(p.i);else state.removed.add(p.i);
  $('settingsForm').elements.ranges.value=selectedRanges(state.removed);
  $('settingsForm').elements.ranges.setCustomValidity('');
  $('alertBox').hidden=true;renderPages();
}
function setupOrganizerEvents(){
  const grid=$('thumbGrid');
  grid.addEventListener('click',e=>{
    const button=e.target.closest('[data-page-action]');
    if(button&&state.tool==='organize'){
      const [action,index]=button.dataset.pageAction.split(':');const i=+index;
      if(action==='rotate')state.pages[i].rot=(state.pages[i].rot+90)%360;
      if(action==='delete')state.pages.splice(i,1);
      renderPages();return;
    }
    if(state.tool==='remove'){
      const tile=e.target.closest('[data-page-tile]');if(tile)toggleRemove(+tile.dataset.pageTile);
    }
  });
  grid.addEventListener('keydown',e=>{if(state.tool==='remove'&&(e.key===' '||e.key==='Enter')){const tile=e.target.closest('[data-page-tile]');if(tile){e.preventDefault();toggleRemove(+tile.dataset.pageTile);}}});
  grid.addEventListener('dragstart',e=>{
    const tile=e.target.closest('[data-page-tile]');if(!tile||state.tool!=='organize')return;
    state.dragIndex=+tile.dataset.pageTile;tile.classList.add('dragging');
    e.dataTransfer.effectAllowed='move';e.dataTransfer.setData('text/plain',String(state.dragIndex));
  });
  grid.addEventListener('dragover',e=>{
    const tile=e.target.closest('[data-page-tile]');if(!tile||state.dragIndex===null)return;
    e.preventDefault();grid.querySelectorAll('.drag-target').forEach(t=>t.classList.remove('drag-target'));tile.classList.add('drag-target');
  });
  grid.addEventListener('drop',e=>{
    const tile=e.target.closest('[data-page-tile]');if(!tile||state.dragIndex===null)return;
    e.preventDefault();const from=state.dragIndex,to=+tile.dataset.pageTile;
    const moved=state.pages.splice(from,1)[0];state.pages.splice(to,0,moved);state.dragIndex=null;renderPages();
  });
  grid.addEventListener('dragend',()=>{state.dragIndex=null;grid.querySelectorAll('.dragging,.drag-target').forEach(t=>t.classList.remove('dragging','drag-target'));});
}
async function loadAllPages(){if(state.files.length){resetOrganizer();loadPreview();}}
function main(){
  renderDashboard();filterTools();setupOrganizerEvents();
  $('toolSearch').addEventListener('input',filterTools);
  $('clearSearch').addEventListener('click',()=>{$('toolSearch').value='';filterTools();$('toolSearch').focus()});
  document.addEventListener('keydown',e=>{if(e.key==='/'&&!state.tool&&!['INPUT','TEXTAREA'].includes(document.activeElement?.tagName)){e.preventDefault();$('toolSearch').focus();}});
  $('backBtn').addEventListener('click',goHome);
  $('chooseBtn').addEventListener('click',e=>{e.stopPropagation();$('fileInput').click();});
  $('dropZone').addEventListener('click',e=>{if(!e.target.closest('button'))$('fileInput').click();});
  $('dropZone').addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();$('fileInput').click()}});
  ['dragover','dragenter'].forEach(name=>$('dropZone').addEventListener(name,e=>{e.preventDefault();$('dropZone').classList.add('drag-over');}));
  ['drop','dragleave'].forEach(name=>$('dropZone').addEventListener(name,e=>{e.preventDefault();$('dropZone').classList.remove('drag-over');if(name==='drop'&&e.dataTransfer?.files)addFiles(e.dataTransfer.files);}));
  $('fileInput').addEventListener('change',e=>{addFiles(e.target.files);e.target.value='';});
  $('folderInput').addEventListener('change',e=>{addFiles(e.target.files);e.target.value='';});
  $('cameraInput').addEventListener('change',e=>{addFiles(e.target.files);e.target.value='';});
  $('addMore').addEventListener('click',()=>$('fileInput').click());
  $('addFolder').addEventListener('click',()=>$('folderInput').click());
  $('cameraBtn').addEventListener('click',()=>$('cameraInput').click());
  $('clearFiles').addEventListener('click',()=>{state.files=[];state.removed.clear();resetOrganizer();renderFiles();$('alertBox').hidden=true;$('successBox').hidden=true;});
  $('restorePages').addEventListener('click',()=>{if(state.tool==='remove'){state.removed.clear();$('settingsForm').elements.ranges.value='';renderPages();}else if(state.files.length){resetOrganizer();loadPreview();}});
  $('loadMore').addEventListener('click',()=>loadPreview(true));
  $('loadAll').addEventListener('click',loadAllPages);
  $('runButton').addEventListener('click',run);
  $('settingsForm').addEventListener('input',e=>{
    if(e.target.name==='ranges'&&state.tool==='remove')syncRemoveFromField();
  });
  window.addEventListener('hashchange',()=>{
    if(location.hash.startsWith('#tool-')){const tool=location.hash.slice(6);if(tools[tool]&&tool!==state.tool)openTool(tool);}
    else if(state.tool)goHome();
  });
  if(location.hash.startsWith('#tool-')&&tools[location.hash.slice(6)])openTool(location.hash.slice(6));
  fetch('/api/health').then(r=>r.json()).then(data=>{
    state.officeAvailable=!!data.office;
    $('engineStatus').textContent=`Local engine ready · ${data.tools} tools`;
    if(state.tool&&officeTools.has(state.tool))$('officeNote').textContent=state.officeAvailable?'LibreOffice detected on this computer.':'LibreOffice desktop installation required.';
  }).catch(()=>{$('engineStatus').textContent='Local engine unavailable';});
}
document.addEventListener('DOMContentLoaded',main);
