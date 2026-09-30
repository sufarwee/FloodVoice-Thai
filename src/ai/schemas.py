from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field

class UrgencyLevel(str, Enum):
    CRITICAL = "CRITICAL"    # วิกฤตด่วนที่สุด (น้ำท่วมมิดหัว/คอ/มีผู้ป่วยติดเตียง/ตัดไฟ/ไร้อาหาร)
    HIGH = "HIGH"            # ด่วนมาก (น้ำระดับเอวถึงอก/ต้องใช้เรือ/เริ่มขาดแคลนเสบียง)
    MEDIUM = "MEDIUM"        # ปานกลาง (น้ำระดับหัวเข่า/สัญจรลำบาก/ต้องการอาหารน้ำดื่ม)
    LOW = "LOW"              # ทั่วไป (น้ำท่วมขังระดับตาตุ่ม/รายงานสถานการณ์ทั่วไป)

class WaterLevelCode(str, Enum):
    LEVEL_1_LOW = "LEVEL_1_LOW"              # ตาตุ่ม / ข้อเท้า / เอ่อล้นถนน
    LEVEL_2_MEDIUM = "LEVEL_2_MEDIUM"        # หัวเข่า / ใต้ถุนบ้าน / ครึ่งล้อรถ
    LEVEL_3_HIGH = "LEVEL_3_HIGH"            # ระดับเอว / มิดล้อรถ / ไฟฟ้าถูกตัด
    LEVEL_4_CRITICAL = "LEVEL_4_CRITICAL"    # ระดับอก / ระดับคอ / น้ำเชี่ยว / ต้องใช้เรือเท่านั้น
    LEVEL_5_EMERGENCY = "LEVEL_5_EMERGENCY"  # มิดหัว / มิดชั้น 1 / บนหลังคา / ติดค้างวิกฤต
    LEVEL_UNKNOWN = "LEVEL_UNKNOWN"          # ไม่ได้ระบุหรือประเมินไม่ได้

class NormalizedLocation(BaseModel):
    is_bangkok: bool = Field(default=False, description="จริงหากเป็นพื้นที่ในกรุงเทพมหานคร")
    province: Optional[str] = Field(None, description="ชื่อจังหวัดเต็ม เช่น 'ปราจีนบุรี', 'กรุงเทพมหานคร' (ไม่มีคำว่า จังหวัด)")
    district: Optional[str] = Field(None, description="ชื่ออำเภอ หรือ เขต (ไม่มีคำว่า อำเภอ หรือ เขต)")
    subdistrict: Optional[str] = Field(None, description="ชื่อตำบล หรือ แขวง (ไม่มีคำว่า ตำบล หรือ แขวง)")
    village_or_community: Optional[str] = Field(None, description="หมู่ที่, ชื่อหมู่บ้าน, หรือชื่อชุมชน เช่น 'หมู่ 3 บ้านท่าลาน', 'ชุมชนริมคลอง'")
    landmark_detail: Optional[str] = Field(None, description="จุดสังเกต ซอย ถนน หรือสถานที่ใกล้เคียง เช่น 'ซอยข้างวัดบางกระเบา', 'สะพานข้ามแม่น้ำ'")
    confidence_score: float = Field(default=0.8, description="ระดับความมั่นใจของพิกัด 0.0 - 1.0")

class DistressReport(BaseModel):
    is_distress: bool = Field(
        description="จริงหากโพสต์/คลิปนี้เป็นการขอความช่วยเหลือ หรือรายงานเหตุน้ำท่วมที่มีผู้เดือดร้อนจริง"
    )
    urgency_level: UrgencyLevel = Field(
        description="ระดับความด่วนในการเข้าช่วยเหลือ: CRITICAL, HIGH, MEDIUM, LOW"
    )
    water_level: str = Field(
        description="ระดับความสูงของน้ำเป็นภาษาไทย เช่น 'ระดับตาตุ่ม', 'หัวเข่า', 'ระดับเอว', 'ระดับอก', 'ระดับคอ', 'มิดหลังคา' หรือ 'ไม่ระบุ'"
    )
    water_level_code: WaterLevelCode = Field(
        description="รหัสมาตรฐานของระดับน้ำ: LEVEL_1_LOW ถึง LEVEL_5_EMERGENCY"
    )
    location: NormalizedLocation = Field(
        description="พิกัดสถานที่ตามโครงสร้างมาตรฐานกรมการปกครอง (DOPA)"
    )
    needs: List[str] = Field(
        default_factory=list,
        description="รายการสิ่งที่ต้องการ เช่น ['ข้าวสาร/อาหารแห้ง', 'น้ำดื่ม', 'ยาประจำตัว', 'นมผงเด็ก', 'เรือพาย/เรือท้องแบน', 'อพยพผู้ป่วยติดเตียง']"
    )
    headcount: Optional[str] = Field(
        None,
        description="จำนวนคนหรือกลุ่มเสี่ยงที่ติดค้าง เช่น 'ผู้ใหญ่ 3 คน เด็ก 1 คน ผู้ป่วยติดเตียง 1 คน'"
    )
    contact_info: Optional[str] = Field(
        None,
        description="เบอร์โทรศัพท์ หรือชื่อผู้แจ้ง/ช่องทางติดต่อ"
    )
    summary: str = Field(
        description="สรุปสถานการณ์สั้นๆ 1-2 ประโยค ระบุความเดือดร้อน พิกัด และสิ่งที่ต้องการเร่งด่วน"
    )
