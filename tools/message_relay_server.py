#!/usr/bin/env python3
"""
龙虾直连消息服务 — Mac 端接收器
运行在 Mac mini 上，监听 9527 端口，接收 TB 发来的消息并写入 chat.md
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import json, os, sys
from datetime import datetime

CHAT_FILE = os.path.expanduser("~/Sync/lobster-comms/chat.md")

class RelayHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(length))
            
            sender = data.get('from', 'unknown')
            message = data.get('message', '')
            now = datetime.now().strftime('%Y-%m-%d %H:%M')
            
            entry = f"\n[{now} {sender}] {message}\n"
            
            with open(CHAT_FILE, 'a', encoding='utf-8') as f:
                f.write(entry)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode())
            print(f"[+] 收到消息并写入 chat.md: {message[:50]}...")
            
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            print(f"[!] 错误: {e}", file=sys.stderr)

    def log_message(self, format, *args):
        pass  # 静默，不打印 access log

if __name__ == '__main__':
    port = 9527
    server = HTTPServer(('0.0.0.0', port), RelayHandler)
    print(f"🦞 龙虾消息中继已启动 → 0.0.0.0:{port}")
    print(f"   写入目标: {CHAT_FILE}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n已停止")
