FROM python:3.11-slim

WORKDIR /app

# 复制代码
COPY . .

# 安装依赖
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# 创建数据和输出目录
RUN mkdir -p data output

# 暴露端口
EXPOSE 8080

CMD ["python", "-m", "bot.main"]
