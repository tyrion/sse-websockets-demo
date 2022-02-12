import asyncio
import random
import itertools
import zlib

from starlette.responses import StreamingResponse
from starlette.applications import Starlette
from websockets.exceptions import WebSocketException


def get_data(stream_id, event_id):
    rnd = random.Random()
    rnd.seed(stream_id * event_id)
    return rnd.randrange(1000)


app = Starlette()


@app.websocket_route("/ws{id:int}")
async def websocket_endpoint(ws):
    id = ws.path_params["id"]
    try:
        await ws.accept()

        for i in itertools.count():
            data = {"id": i, "msg": get_data(id, i)}
            await ws.send_json(data)
            await asyncio.sleep(1)
    except WebSocketException:
        print("client disconnected")


async def sse_generator(req):
    id = req.path_params["id"]
    stream = zlib.compressobj()
    start = int(req.headers.get("last-event-id", 0))
    for i in itertools.count(start):
        data = get_data(id, i)
        data = b"id: %d\ndata: %d\n\n" % (i, data)
        yield stream.compress(data)
        yield stream.flush(zlib.Z_SYNC_FLUSH)
        await asyncio.sleep(1)


@app.route("/sse{id:int}")
async def sse_endpoint(req):
    return StreamingResponse(
        sse_generator(req),
        headers={
            "Content-type": "text/event-stream",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Encoding": "deflate",
        },
    )
