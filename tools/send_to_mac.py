#!/usr/bin/env python3
"""
TB 端发送脚本 — 向 Mac 的龙虾中继发送消息
用法: python3 send_to_mac.py "你的消息内容"
      或者从 stdin 读: echo "消息" | python3 send_to_mac.py
"""
import json, sys, os
from datetime import datetime
from urllib.request import Request, urlopen
from urllib.error import URLError

# Mac 在局域网内的 IP（学九配好后更新这里）
# 也可以通过环境变量 LOBSTER_MAC_IP 覆盖
MAC_IP = os.environ.get('LOBSTER_MAC_IP', '192.168.10.189')
RELAY_URL = f'http://{MAC_IP}:9527'

def send(message, sender='💻 TB龙虾'):
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    payload = json.dumps({
        'from': sender,
        'message': message
    }).encode('utf-8')
    
    req = Request(RELAY_URL, data=payload, headers={
        'Content-Type': 'application/json'
    })
    
    try:
        resp = urlopen(req, timeout=5)
        result = json.loads(resp.read())
        if result.get('status') == 'ok':
            print(f'✅ 发送成功 → {MAC_IP}:9527')
            return True
    except URLError as e:
        print(f'❌ 发送失败: {e}')
        print(f'   检查 Mac 是否在线、端口 9527 是否开放')
        return False
    except Exception as e:
        print(f'❌ 错误: {e}')
        return False

if __name__ == '__main__':
    if len(sys.argv) > 1:
        msg = ' '.join(sys.argv[1:])
    else:
        msg = sys.stdin.read().strip()
    
    if not msg:
        print('用法: python3 send_to_mac.py "消息内容"')
        sys.exit(1)
    
    send(msg)
