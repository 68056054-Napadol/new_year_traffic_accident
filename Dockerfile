# ใช้ Python 3.11 slim image
FROM python:3.11-slim

# ตั้งค่า working directory
WORKDIR /app

# ตั้งค่า environment variables
ENV PYTHONUNBUFFERED=1
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# คัดลอกไฟล์ requirements
COPY requirements.txt .

# ติดตั้ง Python packages โดยไม่ต้องติดตั้ง build tools
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# คัดลอกไฟล์แอปพลิเคชัน
COPY . .

# เปิด port 8501
EXPOSE 8501

# คำสั่งรัน Streamlit
CMD ["streamlit", "run", "src/web_local.py", "--server.port=8501", "--server.address=0.0.0.0"]