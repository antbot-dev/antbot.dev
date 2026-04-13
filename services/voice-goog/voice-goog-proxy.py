#!/usr/bin/env python3
import asyncio
import json
import os
from aiohttp import web, ClientSession, WSMsgType

GOOGLE_API_KEY = (os.environ.get('GOOGLE_API_KEY') or os.environ.get('GOOGLE_AI_API_KEY') or '').strip()
UPSTREAM_MODEL = 'models/gemini-3.1-flash-live-preview'
UPSTREAM_URL = f"wss://generativelanguage.googleapis.com/ws/google.ai.generativelanguage.v1alpha.GenerativeService.BidiGenerateContent?key={GOOGLE_API_KEY}"

async def health(request):
    return web.json_response({"ok": True, "hasKey": bool(GOOGLE_API_KEY)})

async def ws_proxy(request):
    if not GOOGLE_API_KEY:
        return web.json_response({"error": "GOOGLE_API_KEY missing server-side"}, status=500)

    client_ws = web.WebSocketResponse(heartbeat=30)
    await client_ws.prepare(request)

    async with ClientSession() as session:
        try:
            async with session.ws_connect(UPSTREAM_URL, heartbeat=30, autoping=True, max_msg_size=0) as upstream_ws:
                async def client_to_upstream():
                    async for msg in client_ws:
                        if msg.type == WSMsgType.TEXT:
                            await upstream_ws.send_str(msg.data)
                        elif msg.type == WSMsgType.BINARY:
                            await upstream_ws.send_bytes(msg.data)
                        elif msg.type == WSMsgType.ERROR:
                            break
                    await upstream_ws.close()

                async def upstream_to_client():
                    async for msg in upstream_ws:
                        if msg.type == WSMsgType.TEXT:
                            await client_ws.send_str(msg.data)
                        elif msg.type == WSMsgType.BINARY:
                            await client_ws.send_bytes(msg.data)
                        elif msg.type == WSMsgType.ERROR:
                            break
                    await client_ws.close()

                await asyncio.gather(client_to_upstream(), upstream_to_client())
        except Exception as e:
            try:
                await client_ws.send_str(json.dumps({"proxy_error": str(e)}))
            except Exception:
                pass
            await client_ws.close()
    return client_ws

app = web.Application()
app.router.add_get('/health', health)
app.router.add_get('/ws', ws_proxy)

if __name__ == '__main__':
    port = int(os.environ.get('VOICE_GOOG_PROXY_PORT', '8423'))
    web.run_app(app, host='127.0.0.1', port=port)
