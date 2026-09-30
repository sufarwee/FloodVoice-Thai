-- ==============================================================================
-- FloodVoice Supabase / PostgreSQL Schema
-- ==============================================================================

-- 1. ตารางเก็บข้อมูลฟีดดิบจาก Social Media (ป้องกันการดึงซ้ำด้วย source_url UNIQUE)
CREATE TABLE IF NOT EXISTS raw_social_feeds (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ DEFAULT now(),
    source_platform TEXT NOT NULL,         -- 'YouTube', 'TikTok', 'Facebook', 'Instagram'
    source_url TEXT UNIQUE NOT NULL,       -- ลิงก์ต้นทาง
    title TEXT,                            -- ชื่อคลิปหรือหัวข้อโพสต์
    caption TEXT,                          -- ข้อความประกอบโพสต์
    is_live BOOLEAN DEFAULT false,         -- คลิปถ่ายทอดสดหรือไม่
    status TEXT DEFAULT 'PENDING'          -- 'PENDING', 'PROCESSED', 'FAILED'
);

CREATE INDEX IF NOT EXISTS idx_raw_status ON raw_social_feeds(status);

-- 2. ตารางเก็บข้อมูลเคสผู้ประสบภัยที่ผ่านการวิเคราะห์ AI แล้ว (Verified Distress Cases)
CREATE TABLE IF NOT EXISTS verified_distress_cases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ DEFAULT now(),
    source_url TEXT UNIQUE NOT NULL,
    source_platform TEXT,
    
    -- ข้อมูลระดับความรุนแรง
    is_distress BOOLEAN NOT NULL DEFAULT true,
    urgency_level TEXT NOT NULL,           -- 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'
    water_level TEXT,                      -- 'ตาตุ่ม', 'หัวเข่า', 'ระดับเอว', 'ระดับอก', 'ระดับคอ', 'มิดหลังคา'
    water_level_code TEXT,                 -- 'LEVEL_1' ถึง 'LEVEL_5'
    
    -- พิกัดตามมาตรฐานกรมการปกครอง (DOPA)
    is_bangkok BOOLEAN DEFAULT false,
    province TEXT,                         -- เช่น 'ปราจีนบุรี' หรือ 'กรุงเทพมหานคร'
    district TEXT,                         -- เช่น 'กบินทร์บุรี' หรือ 'สายไหม'
    subdistrict TEXT,                      -- เช่น 'กบินทร์' หรือ 'คลองถนน'
    village_or_community TEXT,             -- หมู่ที่ / ชื่อหมู่บ้าน / ชุมชน
    landmark_detail TEXT,                  -- จุดสังเกต ซอย ถนน ใกล้วัด
    
    -- ความต้องการและความช่วยเหลือ
    needs TEXT[],                          -- ['อาหาร', 'น้ำดื่ม', 'ยาประจำตัว', 'นมเด็ก', 'เรือ']
    headcount TEXT,                        -- เช่น 'คนแก่ 2 คน ติดเตียง 1 คน เด็ก 1 คน'
    contact_info TEXT,                     -- เบอร์โทร หรือชื่อผู้ติดต่อ
    summary TEXT,                          -- สรุปสถานการณ์ 1-2 ประโยค
    
    -- สถานะการดำเนินงานของทีมกู้ภัย
    case_status TEXT DEFAULT 'OPEN',       -- 'OPEN', 'IN_PROGRESS', 'RESOLVED'
    assigned_team TEXT,                    -- ชื่อทีมกู้ภัยที่รับเคส
    notes TEXT                             -- บันทึกเพิ่มเติมของหน้างาน
);

-- สร้าง Indexes เพื่อการค้นหาของทีมกู้ภัยที่รวดเร็ว
CREATE INDEX IF NOT EXISTS idx_cases_location ON verified_distress_cases(province, district, subdistrict);
CREATE INDEX IF NOT EXISTS idx_cases_urgency ON verified_distress_cases(urgency_level, case_status);
CREATE INDEX IF NOT EXISTS idx_cases_water_level ON verified_distress_cases(water_level_code);
