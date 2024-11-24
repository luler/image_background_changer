# 基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 复制当前目录中的文件到工作目录中
COPY . .

# 安装依赖
RUN pip install -r requirements.txt

# 加载模型
RUN python -c 'from rembg import remove; from PIL import Image; input_image=Image.open("static/backgrounds/1-white.png"); output=remove(input_image);'

# 暴露端口
EXPOSE 5000

# 设置启动命令
CMD ["python", "app.py"]