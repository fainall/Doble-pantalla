import argparse
import asyncio
import io
import json
import socket
import sys
import time

import mss
from PIL import Image
from aiohttp import web, WSMsgType

if sys.platform == 'win32':
    from input_win import mouse_move, mouse_down, mouse_up
else:
    def mouse_move(x, y): pass
    def mouse_down(x, y): pass
    def mouse_up(x, y): pass


INDEX_HTML = """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, user-scalable=no">
<title>Doble Pantalla</title>
<style>
  html, body { margin:0; height:100%; background:#000; overflow:hidden;
               touch-action:none; overscroll-behavior:none; }
  #screen { width:100vw; height:100vh; object-fit:contain;
            user-select:none; -webkit-user-select:none; -webkit-touch-callout:none; }
  #status { position:fixed; top:8px; left:8px; padding:4px 8px;
            color:#0f0; background:rgba(0,0,0,.5); font:14px monospace;
            border-radius:4px; pointer-events:none; }
  #status.hidden { display:none; }
</style>
</head>
<body>
<img id="screen" alt="">
<div id="status">conectando...</div>
<script>
const img = document.getElementById('screen');
const status = document.getElementById('status');
const proto = location.protocol === 'https:' ? 'wss' : 'ws';
const ws = new WebSocket(`${proto}://${location.host}/ws`);
ws.binaryType = 'arraybuffer';
let lastUrl = null;

ws.onopen = () => { status.classList.add('hidden'); };
ws.onclose = () => { status.classList.remove('hidden'); status.textContent = 'desconectado'; };
ws.onerror = () => { status.classList.remove('hidden'); status.textContent = 'error'; };
ws.onmessage = (e) => {
  if (typeof e.data === 'string') return;
  const blob = new Blob([e.data], { type: 'image/jpeg' });
  const url = URL.createObjectURL(blob);
  img.onload = () => { if (lastUrl) URL.revokeObjectURL(lastUrl); lastUrl = url; };
  img.src = url;
};

function send(evt) { if (ws.readyState === 1) ws.send(JSON.stringify(evt)); }

function pos(touch) {
  const r = img.getBoundingClientRect();
  return {
    x: Math.max(0, Math.min(1, (touch.clientX - r.left) / r.width)),
    y: Math.max(0, Math.min(1, (touch.clientY - r.top) / r.height)),
  };
}

img.addEventListener('touchstart', (e) => {
  e.preventDefault();
  const p = pos(e.touches[0]);
  send({ type:'down', x:p.x, y:p.y });
}, { passive:false });
img.addEventListener('touchmove', (e) => {
  e.preventDefault();
  const p = pos(e.touches[0]);
  send({ type:'move', x:p.x, y:p.y });
}, { passive:false });
img.addEventListener('touchend', (e) => {
  e.preventDefault();
  const t = e.changedTouches[0];
  const p = pos(t);
  send({ type:'up', x:p.x, y:p.y });
}, { passive:false });

document.addEventListener('gesturestart', e => e.preventDefault());
</script>
</body>
</html>
"""


def get_lan_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()


async def index(request):
    return web.Response(text=INDEX_HTML, content_type='text/html')


def event_to_screen(ev, monitor):
    x = monitor['left'] + ev.get('x', 0) * monitor['width']
    y = monitor['top'] + ev.get('y', 0) * monitor['height']
    return int(x), int(y)


async def websocket_handler(request):
    ws = web.WebSocketResponse(max_msg_size=0)
    await ws.prepare(request)
    request.app['clients'].add(ws)
    try:
        async for msg in ws:
            if msg.type != WSMsgType.TEXT:
                continue
            ev = json.loads(msg.data)
            monitor = request.app['monitor']
            if monitor is None:
                continue
            sx, sy = event_to_screen(ev, monitor)
            t = ev.get('type')
            if t == 'down':
                mouse_down(sx, sy)
            elif t == 'move':
                mouse_move(sx, sy)
            elif t == 'up':
                mouse_up(sx, sy)
    finally:
        request.app['clients'].discard(ws)
    return ws


async def capture_loop(app):
    fps = app['fps']
    interval = 1.0 / fps
    quality = app['quality']
    max_width = app['max_width']

    with mss.mss() as sct:
        monitors = sct.monitors
        idx = app['monitor_index']
        if idx < 1 or idx >= len(monitors):
            print(f'[!] Monitor {idx} no existe. Disponibles: {len(monitors)-1}. Usando 1.')
            idx = 1
        monitor = monitors[idx]
        app['monitor'] = monitor
        print(f'[i] Capturando monitor {idx}: {monitor["width"]}x{monitor["height"]} '
              f'en ({monitor["left"]},{monitor["top"]})')

        loop = asyncio.get_event_loop()
        while True:
            start = loop.time()
            raw = sct.grab(monitor)
            img = Image.frombytes('RGB', raw.size, raw.rgb)
            if img.width > max_width:
                ratio = max_width / img.width
                img = img.resize((max_width, int(img.height * ratio)), Image.BILINEAR)
            buf = io.BytesIO()
            img.save(buf, format='JPEG', quality=quality)
            data = buf.getvalue()
            for client in list(app['clients']):
                if not client.closed:
                    try:
                        await client.send_bytes(data)
                    except (ConnectionResetError, RuntimeError):
                        pass
            elapsed = loop.time() - start
            await asyncio.sleep(max(0, interval - elapsed))


async def on_startup(app):
    app['capture_task'] = asyncio.create_task(capture_loop(app))


async def on_cleanup(app):
    app['capture_task'].cancel()
    try:
        await app['capture_task']
    except asyncio.CancelledError:
        pass


def list_monitors():
    with mss.mss() as sct:
        for i, m in enumerate(sct.monitors):
            tag = ' (all)' if i == 0 else ''
            print(f'  {i}: {m["width"]}x{m["height"]} @ ({m["left"]},{m["top"]}){tag}')


def main():
    parser = argparse.ArgumentParser(description='Doble Pantalla - servidor PC -> tablet')
    parser.add_argument('--port', type=int, default=8080)
    parser.add_argument('--monitor', type=int, default=1,
                        help='Indice del monitor a capturar (1=primario, 2=secundario...)')
    parser.add_argument('--fps', type=int, default=20)
    parser.add_argument('--quality', type=int, default=65, help='Calidad JPEG 1-100')
    parser.add_argument('--max-width', type=int, default=1280,
                        help='Ancho maximo enviado a la tablet (se reduce si el monitor es mayor)')
    parser.add_argument('--list', action='store_true', help='Listar monitores y salir')
    args = parser.parse_args()

    if args.list:
        list_monitors()
        return

    app = web.Application()
    app['clients'] = set()
    app['monitor_index'] = args.monitor
    app['monitor'] = None
    app['fps'] = args.fps
    app['quality'] = args.quality
    app['max_width'] = args.max_width
    app.router.add_get('/', index)
    app.router.add_get('/ws', websocket_handler)
    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)

    ip = get_lan_ip()
    print('=' * 50)
    print('  Doble Pantalla')
    print('=' * 50)
    print(f'  Abre en la tablet: http://{ip}:{args.port}/')
    print(f'  (la tablet debe estar en la misma red WiFi)')
    print('=' * 50)
    web.run_app(app, host='0.0.0.0', port=args.port, print=None)


if __name__ == '__main__':
    main()
