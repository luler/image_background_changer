import base64
import io
import os
from PIL import Image
from flask import Flask, request, render_template, send_file, jsonify
from rembg import remove
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['BACKGROUND_FOLDER'] = 'static/backgrounds'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max-limit

# 确保上传目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['BACKGROUND_FOLDER'], exist_ok=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg'}


@app.route('/')
def index():
    # 获取预设背景图片列表
    backgrounds = [f for f in os.listdir(app.config['BACKGROUND_FOLDER'])
                   if allowed_file(f)]
    return render_template('index.html', backgrounds=backgrounds)


@app.route('/process', methods=['POST'])
def process_image():
    if 'file' not in request.files:
        return jsonify({'error': '没有上传文件'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': '不支持的文件格式'}), 400

    try:
        # 读取原始图片
        input_image = Image.open(file.stream)

        # 移除背景
        output = remove(input_image)

        # 准备背景图片
        if 'background' in request.files and request.files['background'].filename != '':
            background = Image.open(request.files['background'].stream).convert('RGBA')
        elif 'background_choice' in request.form:
            background_path = os.path.join(app.config['BACKGROUND_FOLDER'], request.form['background_choice'])
            background = Image.open(background_path).convert('RGBA')
        else:
            background = Image.new('RGBA', output.size, (255, 255, 255, 255))

        # 调整背景图片大小以匹配原图尺寸
        background = background.resize(output.size, Image.Resampling.LANCZOS)

        # 创建一个新的图像，大小与原图相同
        final_image = Image.new('RGBA', output.size, (0, 0, 0, 0))

        # 首先粘贴调整后的背景
        final_image.paste(background, (0, 0))

        # 然后粘贴前景图
        final_image.paste(output, (0, 0), output)

        # 转换为base64
        buffered = io.BytesIO()
        final_image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()

        return jsonify({'image': img_str})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
