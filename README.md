# คู่มือการติดตั้งและใช้งาน

## 1. ขั้นตอนการรัน Local แบบใช้ Streamlit

### 1.1 สร้าง Virtual Environment
```bash
# สร้าง virtual environment (ต้องใช้ Python version 3.11 เท่านั้น)
py -3.11 -m venv venv3112
```

### 1.2 เปิดใช้งาน Virtual Environment
```bash
# Windows
venv3112\Scripts\activate

# macOS/Linux
source venv3112/bin/activate
```

### 1.3 ติดตั้ง Dependencies
```bash
# ติดตั้ง library ที่จำเป็น
pip install -r requirement.txt
```

### 1.4 รัน Web Application
```bash
# เข้าไปที่โฟลเดอร์ src
cd src

# รัน Streamlit
streamlit run web_local.py
```

---

## 2. ขั้นตอนการรัน Local แบบใช้ Docker
### 2.1 ขั้นตอนการสร้าง Docker Image

### 2.1.1 เตรียมความพร้อม
- เปิด **Docker Desktop** ให้ทำงานอยู่

### 2.1.2 Build Docker Image
```bash
# Build image (ใช้เวลาประมาณ 2-5 นาทีในครั้งแรก)
docker-compose build
```

### 2.1.3 ตรวจสอบ Image
```bash
# ตรวจสอบว่า image ถูกสร้างเรียบร้อยแล้ว
docker images
```

---
### 2.2 ขั้นตอนการใช้งาน Web ผ่าน Docker
### 2.2.1 รัน Container
```bash
# รัน container ในโหมด detached
docker-compose up -d
```

### 2.2.2 ตรวจสอบสถานะ
```bash
# ดูสถานะของ container
docker-compose ps
```

### 2.2.3 ดู Logs
```bash
# ดู logs แบบ real-time
docker-compose logs -f
```

### 2.2.4 เปิดหน้าเว็บ
```bash
# เปิด browser และใช้ url นี้
http://localhost:8501/
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
