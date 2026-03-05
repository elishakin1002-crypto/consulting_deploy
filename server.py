import http.server
import socketserver
import os
import sys
import socket

# 启动前加载本地 .env，避免每次手动 export
def load_local_env():
    env_path = os.path.join(os.getcwd(), ".env")
    if not os.path.exists(env_path):
        return
    try:
        with open(env_path, "r", encoding="utf-8") as f:
            for raw in f:
                line = raw.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip("'").strip('"')
                if key and key not in os.environ:
                    os.environ[key] = value
    except Exception as e:
        print(f"Warning: failed to load .env: {e}")

load_local_env()

# 确保能找到 api 模块
sys.path.append(os.getcwd())

# 导入 API Handler
try:
    from api.index import handler as APIHandler
except ImportError:
    print("Error: Could not import API handler from api.index")
    sys.exit(1)

DIRECTORY = "public"

class DevHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # 强制指定静态文件目录为 public
        # 注意：directory 参数在 Python 3.7+ 中可用
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_POST(self):
        if self.path == '/api/chat':
            # 这里是关键：借用 APIHandler 的逻辑来处理 POST 请求
            # 因为 DevHandler 也是 BaseHTTPRequestHandler 的子类，
            # 所以拥有 self.headers, self.rfile, self.wfile 等必要属性
            try:
                APIHandler.do_POST(self)
            except Exception as e:
                print(f"Error in API handler: {e}")
                self.send_error(500, str(e))
        else:
            self.send_error(404, "Not Found")

def find_free_port(start_port=3000):
    port = start_port
    while port < 65535:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("", port))
                return port
            except OSError:
                port += 1
    return None

if __name__ == "__main__":
    # 自动寻找可用端口
    PORT = find_free_port(3000)
    if not PORT:
        print("Error: No free port available.")
        sys.exit(1)

    print(f"Starting server at http://localhost:{PORT}")
    print(f"Serving static files from ./{DIRECTORY}")
    print(f"API endpoint at /api/chat")

    # 允许地址重用，避免端口占用错误
    socketserver.TCPServer.allow_reuse_address = True

    with socketserver.TCPServer(("", PORT), DevHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")
