FROM python:3.11-slim

# ติดตั้ง ffmpeg สำหรับตัดและแปลงไฟล์เสียง/วิดีโอ
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg curl && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ติดตั้ง dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# คัดลอกซอร์สโค้ดเข้า container
COPY . .

ENV PYTHONUNBUFFERED=1

CMD ["python", "main.py", "--scan"]
