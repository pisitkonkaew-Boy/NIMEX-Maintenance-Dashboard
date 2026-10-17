"""ดึงข้อมูลจาก Google Sheet -> ทำความสะอาด -> แทนที่บิลซ้ำด้วยค่าใหม่ -> เข้ารหัส -> site/data.enc
ทดสอบในเครื่อง: APP_USER=Admin APP_PASS=xxx python build_data.py ไฟล์.xlsx"""
import os,sys,json,base64,secrets,shutil,datetime as dt
import pandas as pd
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
COLS=['plate','brand','model','date','km','branch','rcpt','sku','gid','group','name','unit','qty','price','disc','pre','vat','tot','cx','cxd','wo']
HDR={'ทะเบียนรถ':'plate','ยี่ห้อรถ':'brand','รุ่น':'model','วันที่รับบริการ':'date','เลขที่กิโลเมตร':'km','สาขาที่เข้ารับบริการ':'branch','เลขที่ใบเสร็จ':'rcpt','รหัสสินค้า':'sku','รหัสกลุ่ม':'gid','กลุ่มสินค้า':'group','ชื่อสินค้า':'name','หน่วย':'unit','จำนวน':'qty','ราคาต่อหน่วย':'price','ส่วนลด':'disc','ยอดขายก่อนVAT':'pre','VAT':'vat','ยอดขายรวมVAT':'tot','เลขที่ยกเลิกบิล':'cx','วันที่ยกเลิกบิล':'cxd','เลขที่ใบสั่งซ่อม':'wo'}
def from_header(header,rows):
    import re
    names=[HDR.get(re.sub(r'\s+','',str(h))) for h in header]
    if sum(n is not None for n in names)<12: raise SystemExit('หัวตารางใน Sheet ไม่ตรงที่คาด (จับคู่ได้น้อยกว่า 12 คอลัมน์): '+str(header))
    d=pd.DataFrame([(r+['']*len(header))[:len(header)] for r in rows],columns=[n or '_x%d'%i for i,n in enumerate(names)])
    return d.reindex(columns=COLS)   # คอลัมน์ที่ Sheet ไม่มี (เช่น เลขที่ใบเสร็จ) จะว่าง
def load():
    if len(sys.argv)>1: raw=pd.read_excel(sys.argv[1],dtype=object).iloc[:,:21]
    elif os.environ.get('APPS_SCRIPT_URL'):
        import urllib.request,urllib.parse
        b=os.environ['APPS_SCRIPT_URL']; u=b+('&' if '?' in b else '?')+urllib.parse.urlencode({'token':os.environ['APPS_SCRIPT_TOKEN']})
        j=json.load(urllib.request.urlopen(u,timeout=300))
        if 'rows' not in j: raise SystemExit('Apps Script ตอบกลับผิดปกติ: '+str(j)[:200])
        if 'header' not in j: raise SystemExit('ต้องอัปเดตโค้ด Apps Script ให้ส่ง header ด้วย (ดู apps_script.gs)')
        raw=from_header(j['header'],j['rows'])
    else:
        from google.oauth2.service_account import Credentials
        from googleapiclient.discovery import build
        cr=Credentials.from_service_account_info(json.loads(os.environ['GCP_SA_JSON']),scopes=['https://www.googleapis.com/auth/spreadsheets.readonly'])
        v=build('sheets','v4',credentials=cr,cache_discovery=False).spreadsheets().values().get(spreadsheetId=os.environ['SHEET_ID'],range="'%s'"%(os.environ.get('SHEET_TAB') or 'Sheet1'),valueRenderOption='UNFORMATTED_VALUE').execute().get('values',[])[1:]
        raw=pd.DataFrame([(r+['']*21)[:21] for r in v])
    raw.columns=COLS; return raw.replace('',float('nan'))
def pdate(x):
    if isinstance(x,(int,float)) and not pd.isna(x): return pd.to_datetime(x,unit='D',origin='1899-12-30')
    if isinstance(x,(dt.datetime,pd.Timestamp)): return pd.Timestamp(x)
    import re; x=re.sub(r'\d{4}',lambda m:str(int(m.group())-543) if int(m.group())>2400 else m.group(),str(x).strip())  # รองรับปี พ.ศ.
    return pd.to_datetime(x,errors='coerce') if x[:4].isdigit() else pd.to_datetime(x,format='%d/%m/%Y',errors='coerce')
def num(s): return pd.to_numeric(s.astype(str).str.replace(r'[^0-9.\-]','',regex=True),errors='coerce')
df=load()
df['d']=df.date.map(pdate).dt.strftime('%Y-%m-%d'); df=df[df.plate.notna()&df.d.notna()].copy()
df['km']=num(df.km); df['qty']=num(df.qty).fillna(0); df['tot']=num(df.tot).fillna(0)
df['group']=df.group.fillna('อื่นๆ'); df['branch']=df.branch.fillna('-').astype(str); df['name']=df.name.fillna('').astype(str)
df['key']=df.rcpt.fillna(df.plate+'|'+df.d+'|'+df.branch)
# ซ้ำให้ยึดค่าใหม่: บิลเดียวกันที่ถูกเติมซ้ำภายหลัง (แถวอยู่ต่ำกว่าใน Sheet) จะแทนที่ทั้งบิลเดิม
df['_r']=range(len(df)); has=df.rcpt.notna(); replaced=0; dups=0
a=df[has].copy(); b=df[~has]
if len(a):
    a['_b']=(a.groupby('key')._r.diff()!=1).groupby(a['key']).cumsum()
    replaced=int((a.groupby('key')._b.max()>1).sum()); a=a[a._b==a.groupby('key')._b.transform('max')]
n0=len(b); b=b.copy(); b['_i']=b[['plate','d','km','branch','group','name','qty','tot']].apply(lambda r:'|'.join(map(str,r)),axis=1)
if len(b) and os.environ.get('DEDUPE_NO_RECEIPT')=='1':   # (ปิดไว้เป็นค่าเริ่มต้น เพราะอาจตัดแถวจริงออก) แถวที่ไม่มีเลขบิล: แถวเหมือนกันทุกช่องที่ถูกเติมซ้ำภายหลังจะแทนที่ชุดเดิม (แถวเหมือนกันที่ติดกันถือว่าเป็นรายการจริง เก็บไว้ทั้งหมด)
    b['_b']=(b.groupby('_i')._r.diff()!=1).groupby(b['_i']).cumsum(); b=b[b._b==b.groupby('_i')._b.transform('max')]
dups=n0-len(b)
df=pd.concat([a,b]).sort_values('_r')
df['oil']=df.name.str.contains('น้ำมันเครื่อง')&df.group.isin(['สินค้าชุด / SET','น้ำมัน / LUBE'])&~df.name.str.contains('เกียร์|เฟือง|พาวเวอร์|ฟรี|ค่าบริการ')
G=sorted(df.group.unique()); B=sorted(df.branch.unique()); gi={g:i for i,g in enumerate(G)}; bi={b:i for i,b in enumerate(B)}
P=[]
for pl,a in df.groupby('plate'):
    vs=[]
    for k,r in a.groupby('key'):
        h=r.iloc[0]; paid=r[r.tot>0]; km=r.km.dropna()
        vs.append(dict(d=h.d,k=int(km.iloc[0]) if len(km) else None,b=bi[h.branch],x=int((r.group=='อู่นอก').all()),c=int(r.cx.notna().any()),o=int(r.oil.any()),t=round(float(r.tot.sum())),
          i=[[n,gi[g],q,round(float(t))] for n,g,q,t in zip(paid.name,paid.group,paid.qty,paid.tot)],f=int(len(r)-len(paid))))
    P.append(dict(id=pl,b=str(a.brand.iloc[0]),m=str(a.model.iloc[0]),v=vs))
upd=dt.datetime.now(dt.timezone(dt.timedelta(hours=7))).strftime('%d/%m/%Y %H:%M')
data=dict(ref=df.d.max(),upd=upd,g=[g.split(' /')[0] for g in G],br=B,p=P)
salt,iv,n=secrets.token_bytes(16),secrets.token_bytes(12),200000
key=PBKDF2HMAC(hashes.SHA256(),32,salt,n).derive(f"{os.environ['APP_USER']}:{os.environ['APP_PASS']}".encode())
c=AESGCM(key).encrypt(iv,json.dumps(data,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode(),None)
e=lambda x:base64.b64encode(x).decode()
os.makedirs('site',exist_ok=True); json.dump(dict(s=e(salt),i=e(iv),c=e(c),n=n),open('site/data.enc','w'))
shutil.copy('index.html','site/index.html')
print(f'แถว {len(df)} | บิล/รายการ {df.key.nunique()} | ทะเบียน {len(P)} | บิลที่ถูกแทนที่ด้วยค่าใหม่ {replaced} | แถวซ้ำที่ตัดออก (ไม่มีเลขบิล) {dups} | ข้อมูลถึง {data["ref"]}')
