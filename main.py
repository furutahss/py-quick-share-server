import os
import socket
import qrcode
from flask import Flask, request, render_template_string, send_from_directory, redirect
from werkzeug.utils import secure_filename
from pathlib import Path

app = Flask(__name__)

# アップロードされたファイルを保存するディレクトリ
UPLOAD_DIR = Path("uploads")
if not UPLOAD_DIR.exists():
    UPLOAD_DIR.mkdir()

app.config['UPLOAD_FOLDER'] = str(UPLOAD_DIR)

# ブラウザに表示するHTMLテンプレート
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>QuickShare Server</title>
    <style>
        body { font-family: sans-serif; text-align: center; padding: 20px; background: #f8f9fa; }
        .container { max-width: 500px; margin: auto; background: white; padding: 30px; border-radius: 10px; shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .upload-box { border: 2px dashed #007bff; padding: 30px; margin: 20px 0; border-radius: 8px; }
        input[type="file"] { margin-bottom: 20px; width: 100%; }
        input[type="submit"] { background: #007bff; color: white; border: none; padding: 12px 24px; border-radius: 5px; cursor: pointer; font-size: 16px; }
        input[type="submit"]:hover { background: #0056b3; }
        .file-list { text-align: left; margin-top: 30px; }
        a { color: #007bff; text-decoration: none; }
    </style>
</head>
<body>
    <div class="container">
        <h1>QuickShare Server</h1>
        <div class="upload-box">
            <h3>PCにファイルを送る</h3>
            <form method="POST" action="/upload" enctype="multipart/form-data">
                <input type="file" name="file">
                <input type="submit" value="アップロード開始">
            </form>
        </div>
        <div class="file-list">
            <h3>公開中のファイル一覧</h3>
            <ul>
                {% for file in files %}
                <li><a href="/download/{{ file }}">{{ file }}</a></li>
                {% endfor %}
            </ul>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    files = [f.name for f in UPLOAD_DIR.iterdir() if f.is_file()]
    return render_template_string(HTML_TEMPLATE, files=files)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "ファイルがありません", 400
    file = request.files['file']
    if file.filename == '':
        return "ファイルが選択されていません", 400
    
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect('/')

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

if __name__ == "__main__":
    port = 8000
    local_ip = get_local_ip()
    url = f"http://{local_ip}:{port}"

    print(f"🚀 QuickShare Server (Flask版) 起動中...")
    print(f"🔗 URL: {url}")
    print("\nスマホで以下のQRコードをスキャンしてください：")
    
    qr = qrcode.QRCode()
    qr.add_data(url)
    qr.print_ascii(invert=True)

    app.run(host='0.0.0.0', port=port, debug=False)