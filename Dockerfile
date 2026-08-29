FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY . .

# 创建数据和输出目录
RUN mkdir -p data output

# 暴露端口（WebSocket模式不需要，但保留兼容）
EXPOSE 8080

CMD ["python", "-m", "bot.main"]
