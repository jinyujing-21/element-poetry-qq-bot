FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 创建数据和输出目录
RUN mkdir -p data output

CMD ["python", "-m", "bot.main"]
