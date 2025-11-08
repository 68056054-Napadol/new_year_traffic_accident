# คู่มือการติดตั้งและใช้งาน

## ขั้นตอนการรัน Local

### 1. สร้าง Virtual Environment
```bash
# สร้าง virtual environment (ต้องใช้ Python version 3.11 เท่านั้น)
py -3.11 -m venv venv3112
```

### 2. เปิดใช้งาน Virtual Environment
```bash
# Windows
venv3112\Scripts\activate

# macOS/Linux
source venv3112/bin/activate
```

### 3. ติดตั้ง Dependencies
```bash
# ติดตั้ง library ที่จำเป็น
pip install -r requirement.txt
```

### 4. รัน Web Application
```bash
# เข้าไปที่โฟลเดอร์ src
cd src

# รัน Streamlit
streamlit run web_local.py
```

---

## ขั้นตอนการสร้าง Docker Image

### 1. เตรียมความพร้อม
- เปิด **Docker Desktop** ให้ทำงานอยู่

### 2. Build Docker Image
```bash
# Build image (ใช้เวลาประมาณ 2-5 นาทีในครั้งแรก)
docker-compose build
```

### 3. ตรวจสอบ Image
```bash
# ตรวจสอบว่า image ถูกสร้างเรียบร้อยแล้ว
docker images
```

---

## ขั้นตอนการใช้งาน Web ผ่าน Docker

### 1. รัน Container
```bash
# รัน container ในโหมด detached
docker-compose up -d
```

### 2. ตรวจสอบสถานะ
```bash
# ดูสถานะของ container
docker-compose ps
```

### 3. ดู Logs
```bash
# ดู logs แบบ real-time
docker-compose logs -f
```

### 4. หยุดการทำงาน
```bash
# หยุด container
docker-compose down
```

---

## Requirements

- **Python**: Version 3.11
- **Docker Desktop**: สำหรับการรันผ่าน Docker
- **Dependencies**: ระบุใน `requirement.txt`

---

## หมายเหตุ

- ตรวจสอบให้แน่ใจว่าใช้ Python version 3.11 เท่านั้น
- Docker Desktop ต้องเปิดทำงานก่อนรัน Docker commands
- การ build Docker image ครั้งแรกจะใช้เวลานานกว่าปกติ