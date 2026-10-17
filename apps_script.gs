// วางใน Google Sheet > ส่วนขยาย > Apps Script  (ไม่ต้องใช้ Google Cloud Console)
const TOKEN = 'เปลี่ยนเป็นรหัสลับยาวๆ ของคุณเอง';   // ต้องตรงกับ Secret APPS_SCRIPT_TOKEN ใน GitHub
const TAB   = '2025-2026';                          // ชื่อแท็บที่เก็บข้อมูล

function doGet(e) {
  const out = ContentService.createTextOutput().setMimeType(ContentService.MimeType.JSON);
  if (!e.parameter.token || e.parameter.token !== TOKEN) return out.setContent(JSON.stringify({error: 'unauthorized'}));
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sh = ss.getSheetByName(TAB);
  if (!sh) return out.setContent(JSON.stringify({error: 'ไม่พบแท็บ', tabs: ss.getSheets().map(s => s.getName())}));
  const rows = sh.getDataRange().getDisplayValues();
  return out.setContent(JSON.stringify({header: rows[0], rows: rows.slice(1)}));
}

function test() {   // ใช้ทดสอบในหน้า Apps Script (เลือก test แล้วกด Run)
  const t = doGet({parameter: {token: TOKEN}}).getContent();
  console.log(t.length + ' ตัวอักษร | ' + t.slice(0, 400));
}
