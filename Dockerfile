# 使用官方的Python运行时作为父镜像
FROM python:3.10-slim

# 将工作目录设置为 /app
WORKDIR /app

# 复制依赖文件到工作目录
COPY requirements.txt .

# 安装所需的包
# --no-cache-dir 选项可以减小镜像大小
# --trusted-host pypi.python.org 是为了避免潜在的网络问题
RUN pip install --no-cache-dir --trusted-host pypi.python.org -r requirements.txt

# 将当前目录的内容复制到容器的 /app 中
COPY . .

# 告诉Docker容器在运行时监听哪个端口
EXPOSE 8000

# 运行 app.py 当容器启动时
# 使用 --host 0.0.0.0 来让容器外部可以访问服务
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]