import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
from config import OBSIDIAN_EXPORT_DIR

class ObsidianExporter:
    def __init__(self, export_dir: Path = OBSIDIAN_EXPORT_DIR):
        self.export_dir = Path(export_dir)
        self.export_dir.mkdir(parents=True, exist_ok=True)
        self.cases_dir = self.export_dir / "cases"
        self.cases_dir.mkdir(parents=True, exist_ok=True)

    def export_case_card(self, case: Dict[str, Any]) -> str:
        """สร้างไฟล์ Markdown แยกเป็นรายเคส พร้อม Obsidian Frontmatter (Tags & Dataview)"""
        loc = case.get("location", {})
        province = loc.get("province") or "ไม่ระบุจังหวัด"
        district = loc.get("district") or "ไม่ระบุอำเภอ"
        water_level = case.get("water_level") or "ไม่ระบุ"
        urgency = case.get("urgency_level") or "MEDIUM"
        now_str = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        safe_url_id = abs(hash(case.get("source_url", ""))) % 100000

        filename = f"{province}_{district}_{urgency}_{now_str}_{safe_url_id}.md"
        filepath = self.cases_dir / filename

        urgency_emoji = {
            "CRITICAL": "🚨 วิกฤตด่วนที่สุด",
            "HIGH": "🔴 ด่วนมาก",
            "MEDIUM": "🟡 ปานกลาง",
            "LOW": "🟢 ทั่วไป"
        }.get(urgency, "⚠️ แจ้งเหตุ")

        needs_str = "\n".join([f"- [ ] {item}" for item in case.get("needs", [])]) or "- ไม่ได้ระบุ"

        content = f"""---
title: "เคสน้ำท่วม: {province} {district}"
date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
urgency: {urgency}
water_level: "{water_level}"
water_level_code: {case.get('water_level_code', '')}
province: "{province}"
district: "{district}"
subdistrict: "{loc.get('subdistrict', '')}"
status: {case.get('case_status', 'OPEN')}
platform: {case.get('platform', 'Unknown')}
source_url: "{case.get('source_url', '')}"
tags:
  - flood/incident
  - urgency/{urgency.lower()}
  - water_level/{case.get('water_level_code', 'unknown').lower()}
  - province/{province}
---

# {urgency_emoji} — เคสน้ำท่วม {province} ({district})

> **ระดับความสูงของน้ำ:** `{water_level}` ({case.get('water_level_code')})
> **สถานะเคส:** `{case.get('case_status', 'OPEN')}`

---

### 📍 ข้อมูลพิกัดและสถานที่ (DOPA Standard)
* **จังหวัด:** {province}
* **อำเภอ/เขต:** {district}
* **ตำบล/แขวง:** {loc.get('subdistrict') or 'ไม่ระบุ'}
* **หมู่บ้าน/ชุมชน:** {loc.get('village_or_community') or 'ไม่ระบุ'}
* **จุดสังเกต/รายละเอียด:** {loc.get('landmark_detail') or 'ไม่ระบุ'}

---

### 📦 สิ่งที่ต้องการความช่วยเหลือเร่งด่วน
{needs_str}

* **กลุ่มเสี่ยง/จำนวนคน:** {case.get('headcount') or 'ไม่ระบุ'}
* **เบอร์ติดต่อ:** `{case.get('contact_info') or 'ไม่ระบุ'}`

---

### 📝 สรุปเหตุการณ์
{case.get('summary', 'ไม่มีสรุป')}

---

### 🔗 ข้อมูลต้นทาง
* **แพลตฟอร์ม:** {case.get('platform')}
* **ลิงก์:** [{case.get('source_url')}]({case.get('source_url')})
"""
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content.strip() + "\n")

        # อัปเดตตารางสรุป Dashboard รายวัน
        self.update_daily_dashboard()
        return str(filepath)

    def update_daily_dashboard(self, cases: List[Dict[str, Any]] = None):
        """สร้างหรืออัปเดตไฟล์ตารางสรุปรวมรายวันสำหรับ Obsidian"""
        today_str = datetime.now().strftime("%Y-%m-%d")
        dashboard_path = self.export_dir / f"DASHBOARD_{today_str}.md"

        # โค้ด Dataview สำหรับผู้ใช้ Obsidian และตาราง Markdown มาตรฐาน
        content = f"""# 🌊 สรุปสถานการณ์น้ำท่วมประจำวัน ({today_str})

อัปเดตล่าสุด: `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`

> [!TIP]
> ตารางนี้จัดลำดับตาม **ความเร่งด่วน** และ **ระดับความสูงของน้ำ** เพื่อให้ทีมกู้ภัยเข้าพื้นที่วิกฤตก่อน

| ความด่วน | ระดับน้ำ | จังหวัด | อำเภอ/เขต | ตำบล/แขวง | สิ่งที่ต้องการ | เบอร์ติดต่อ | ลิงก์เคส |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
"""
        # อ่านไฟล์เคสทั้งหมดใน cases_dir มาจัดทำตาราง
        rows = []
        for file in self.cases_dir.glob("*.md"):
            try:
                text = file.read_text(encoding="utf-8")
                # Parse frontmatter สั้นๆ
                lines = text.split("\n")
                urgency = "MEDIUM"
                water = "ไม่ระบุ"
                prov = "ไม่ระบุ"
                dist = "ไม่ระบุ"
                subd = "ไม่ระบุ"
                phone = "ไม่ระบุ"
                needs = "เสบียง"
                for l in lines[:25]:
                    if l.startswith("urgency:"): urgency = l.split(":", 1)[1].strip()
                    elif l.startswith("water_level:"): water = l.split(":", 1)[1].strip().strip('"')
                    elif l.startswith("province:"): prov = l.split(":", 1)[1].strip().strip('"')
                    elif l.startswith("district:"): dist = l.split(":", 1)[1].strip().strip('"')
                    elif l.startswith("subdistrict:"): subd = l.split(":", 1)[1].strip().strip('"')

                urgency_tag = {
                    "CRITICAL": "🚨 CRITICAL",
                    "HIGH": "🔴 HIGH",
                    "MEDIUM": "🟡 MEDIUM",
                    "LOW": "🟢 LOW"
                }.get(urgency, urgency)

                rel_link = f"[[cases/{file.name}|เปิดการ์ด]]"
                rows.append((urgency, f"| {urgency_tag} | {water} | {prov} | {dist} | {subd} | {needs} | {phone} | {rel_link} |\n"))
            except Exception:
                continue

        # จัดเรียง CRITICAL มาก่อน HIGH, MEDIUM, LOW
        priority_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        rows.sort(key=lambda x: priority_order.get(x[0], 99))

        for _, row_str in rows:
            content += row_str

        with open(dashboard_path, "w", encoding="utf-8") as f:
            f.write(content)
