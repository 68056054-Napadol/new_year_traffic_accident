# ใช้ Python 3.10 slim image
FROM python:3.10-slim

# ตั้งค่า working directory
WORKDIR /app

# ติดตั้ง system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# คัดลอก requirements
COPY requirements.txt .

# ติดตั้ง Python packages
RUN pip install --no-cache-dir -r requirements.txt

# คัดลอกโค้ดทั้งหมด
COPY . .

# สร้างโฟลเดอร์ที่จำเป็น
RUN mkdir -p data/sample data/processed models logs

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# รันแอพ
ENTRYPOINT ["streamlit", "run", "src/app.py", "--server.port=8501", "--server.address=0.0.0.0"]