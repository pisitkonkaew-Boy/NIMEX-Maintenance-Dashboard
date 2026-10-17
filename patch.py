# สร้าง index.html (หน้าแดชบอร์ดที่มีหน้าล็อกอิน) จาก tpl.html
t=open('tpl.html',encoding='utf-8').read()
def rep(a,b):
    global t
    assert a in t,a[:50]; t=t.replace(a,b,1)
LOGIN=r'''const $l=s=>document.querySelector(s),b64=s=>Uint8Array.from(atob(s),c=>c.charCodeAt(0));
async function unlock(u,pw){const j=await (await fetch('data.enc?'+Date.now())).json();const km=await crypto.subtle.importKey('raw',new TextEncoder().encode(u+':'+pw),'PBKDF2',false,['deriveKey']);const k=await crypto.subtle.deriveKey({name:'PBKDF2',salt:b64(j.s),iterations:j.n,hash:'SHA-256'},km,{name:'AES-GCM',length:256},false,['decrypt']);return JSON.parse(new TextDecoder().decode(await crypto.subtle.decrypt({name:'AES-GCM',iv:b64(j.i)},k,b64(j.c))))}
$l('#lf').addEventListener('submit',async e=>{e.preventDefault();$l('#le').textContent='กำลังตรวจสอบ…';try{const d=await unlock($l('#lu').value.trim(),$l('#lp').value);$l('#lg').remove();boot(d)}catch(x){$l('#le').textContent='เข้าสู่ระบบไม่สำเร็จ: ชื่อผู้ใช้/รหัสผ่านไม่ถูกต้อง หรือยังไม่มีไฟล์ข้อมูล (ต้องเปิดผ่านลิงก์เว็บ ไม่ใช่เปิดไฟล์ตรงๆ)'}});
function boot(D){'''
PART=r'''const PARTS={'น้ำมันเครื่อง':null,'ยาง':i=>/^ยาง/.test(D.g[i[1]])||i[0].includes('ยาง'),'ผ้าเบรก':i=>i[0].includes('ผ้าเบรก'),'แบตเตอรี่':i=>(D.g[i[1]]+i[0]).includes('แบตเตอรี่'),'ไส้กรอง':i=>i[0].includes('ไส้กรอง'),'ช่วงล่าง':i=>/^ช่วงล่าง/.test(D.g[i[1]]),'โช้คอัพ':i=>i[0].includes('โช้ค'),'คลัตช์':i=>/คลัต|คลัท/.test(i[0])};
const OIL='น้ำมันเครื่อง';
function hits(p,t){const fn=PARTS[t],tl=t.toLowerCase();return p.v.filter(x=>t==OIL?(x.o&&!x.x):1).map(x=>({x,it:t==OIL?x.i.filter(i=>/น้ำมันเครื่อง|ชุดน้ำมัน/.test(i[0])):x.i.filter(fn||(i=>i[0].toLowerCase().includes(tl)))})).filter(h=>t==OIL||h.it.length)}
function partDetail(p){if(!part)return'<p class="mut">กดชื่อชิ้นส่วนในตาราง หรือพิมพ์ชื่ออะไหล่ เพื่อดูประวัติ</p>';const h=hits(p,part);if(!h.length)return`<p class="mut">ไม่พบประวัติ “${esc(part)}” ของทะเบียนนี้</p>`;
 return`<h3>ประวัติ: ${esc(part)} (${h.length} ครั้ง)</h3><div class="scroll"><table><tr><th>ครั้งที่</th><th>วันที่</th><th class="n">ไมล์ (กม.)</th><th class="n">ห่างครั้งก่อน (กม.)</th><th class="n">(วัน)</th><th>รายการ</th><th class="n">บาท</th></tr>${h.map((r,i)=>{const b=h[i-1],gk=b&&b.x.k!=null&&r.x.k!=null?r.x.k-b.x.k:null;return`<tr><td>${i+1}</td><td>${th(r.x.d)}</td><td class="n">${r.x.k!=null?f(r.x.k):'-'}</td><td class="n">${gk!=null?f(gk):'-'}</td><td class="n">${b?dd(r.x.d,b.x.d):'-'}</td><td>${esc(r.it.map(i=>i[0]).join(', ').slice(0,90)||'-')}</td><td class="n">${f(r.it.reduce((s,i)=>s+i[3],0))}</td></tr>`}).join('')}</table></div>`}
function partCard(p){const rows=Object.keys(PARTS).map(t=>{const h=hits(p,t);return{t,n:h.length,l:h[h.length-1]}});
 return`<div class="card"><h3>เปลี่ยนล่าสุดแยกตามชิ้นส่วน</h3><input id="pt" type="search" aria-label="ค้นหาอะไหล่" placeholder="พิมพ์ชื่ออะไหล่ เช่น ยาง, ผ้าเบรก" value="${esc(part||'')}" style="width:100%;max-width:360px;margin-bottom:10px;padding:8px 10px;border:1px solid var(--line);border-radius:8px;background:var(--bg);color:var(--ink);font:inherit"><div class="scroll"><table><tr><th>ชิ้นส่วน</th><th class="n">ครั้ง</th><th>ล่าสุด</th><th class="n">ไมล์ (กม.)</th><th class="n">ผ่านมา (วัน)</th><th class="n">(กม.)</th></tr>${rows.map(r=>`<tr><td><button class="pl" data-part="${r.t}">${r.t}</button></td><td class="n">${r.n}</td><td>${r.l?th(r.l.x.d):'-'}</td><td class="n">${r.l&&r.l.x.k!=null?f(r.l.x.k):'-'}</td><td class="n">${r.l?dd(ref,r.l.x.d):'-'}</td><td class="n">${r.l&&r.l.x.k!=null&&p.cur!=null?f(p.cur-r.l.x.k):'-'}</td></tr>`).join('')}</table></div><div id="pd" style="margin-top:14px">${partDetail(p)}</div></div>`}
'''
rep('const D=__DATA__;',LOGIN)
rep('const ref=D.ref,RP=','const ref=new Date(Date.now()+252e5).toISOString().slice(0,10),RP=')
rep("let sel=null,fl='all',q='';","let sel=null,fl='all',q='',part=null;")
rep("const s=q.trim().toLowerCase();","const s=q.replace(/[\\s-]/g,'').toLowerCase();")
rep("(p.id+' '+p.m).toLowerCase().includes(s)","(p.id+p.m).replace(/[\\s-]/g,'').toLowerCase().includes(s)")
rep('ข้อมูลถึง ${th(ref)} · ไม่นับบิลที่ยกเลิก','ข้อมูลถึง ${th(D.ref)} · คิดสถานะ ณ ${th(ref)} · ไม่นับบิลที่ยกเลิก')
rep('ข้อมูลถึง ${th(ref)}`',"ข้อมูลถึง ${th(D.ref)}${D.upd?' · อัปเดต '+D.upd:''}`")
rep('<div class="card"><h3>ไทม์ไลน์การเข้าซ่อม','${partCard(p)}<div class="card"><h3>ไทม์ไลน์การเข้าซ่อม')
rep('function render(){list();',PART+'function render(){list();')
rep("const a=e.target.closest('[data-p]'),c=e.target.closest('[data-f]');if(a){sel=a.dataset.p||null;render();$('#main').scrollTop=0}",
"const pt=e.target.closest('[data-part]'),a=e.target.closest('[data-p]'),c=e.target.closest('[data-f]');if(pt){part=pt.dataset.part;render()}else if(a){sel=a.dataset.p||null;history.replaceState(null,'',sel?'#'+encodeURIComponent(sel):location.pathname);render();$('#main').scrollTop=0}")
rep("$('#q').addEventListener('input',e=>{q=e.target.value;list()});","$('#q').addEventListener('input',e=>{q=e.target.value;list()});document.addEventListener('input',e=>{if(e.target.id=='pt'){part=e.target.value.trim()||null;const p=P.find(x=>x.id==sel);if(p)$('#pd').innerHTML=partDetail(p)}});document.addEventListener('keydown',e=>{if(e.key=='/'&&!/INPUT/.test(document.activeElement.tagName)){e.preventDefault();$('#q').focus()}});")
rep('render();\n</script>',"sel=decodeURIComponent(location.hash.slice(1))||null;if(!P.some(x=>x.id==sel))sel=null;render();}\n</script>")
rep('<div class="app">','<div id="lg"><form id="lf"><h1>ประวัติซ่อมบำรุงรายทะเบียน</h1><input id="lu" autocomplete="username" aria-label="ชื่อผู้ใช้" placeholder="ชื่อผู้ใช้" required><input id="lp" type="password" autocomplete="current-password" aria-label="รหัสผ่าน" placeholder="รหัสผ่าน" required><button type="submit">เข้าสู่ระบบ</button><div id="le" role="alert"></div></form></div><div class="app">')
rep('</style>','#lg{position:fixed;inset:0;z-index:9;background:var(--side);display:grid;place-items:center;padding:20px}#lg form{background:var(--card);border-radius:12px;padding:26px;width:min(360px,100%);display:grid;gap:12px}#lg h1{font:600 20px Prompt,sans-serif;margin:0}#lg input{padding:10px 12px;border:1px solid var(--line);border-radius:8px;background:var(--bg);color:var(--ink);font:inherit}#lg button{padding:10px;border:0;border-radius:8px;background:var(--hi);color:#1a1400;font:600 15px Prompt,sans-serif;cursor:pointer}#le{color:var(--bad);min-height:1.4em;font-size:13px}</style>')
open('index.html','w',encoding='utf-8').write(t)
