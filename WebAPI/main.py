import logging
import asyncio
import socketio
from aiohttp import web
from aiohttp_index import IndexMiddleware
from radariq import RadarIQ

# Start a SocketIO server and a webserver
sio = socketio.AsyncServer(async_mode='aiohttp')
app = web.Application(middlewares=[IndexMiddleware()])
sio.attach(app)
app.router.add_static('/', path=str('public'), name='static')

async def start_background_tasks(app):
    loop = asyncio.get_event_loop()
    app['data_proxy'] = loop.create_task(process_data())


async def cleanup_background_tasks(app):
    app['data_proxy'].cancel()
    await app['data_proxy']

app.on_startup.append(start_background_tasks)
app.on_cleanup.append(cleanup_background_tasks)


# Connect the RadarIQ logging up to the web socket
logger = logging.getLogger('RadarIQ')
logger.setLevel(logging.INFO)


class SocketIOLoggingHandler(logging.Handler):
    """
    A handler class which writes logging records to a socketIO socket.
    """

    def __init__(self):
        logging.Handler.__init__(self)
        self.loop = asyncio.get_event_loop()

    def emit(self, record):
        """
        Emit a log message.

        create_task is needed to at as the bridge between the sync logging methods and the async socketio
        """
        self.loop.create_task(sio.emit('message', str(record.msg)))


logger.addHandler(SocketIOLoggingHandler())

# Create the RadarIQ instance
try:
    riq = RadarIQ()
except Exception as e:
    logger.error(str(e))


# Setup callbacks

async def process_data():
    """
    Async task which listens for data from the RadarIQ SDK and emits it over the web socket connection
    """
    try:
        while True:
            for data in riq.get_data():
                if data is not None:
                    await sio.emit('data', data)
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        pass

@sio.event
async def connect(sid, environ):
    """
    Respond to a 'connect' event from a socket
    :param sid: socket ID
    :param environ: socket environment
    """
    print('Client Connected')


@sio.event
async def disconnect(sid):
    """
    Respond to a 'disconnect' event from a socket
    :param sid: Socket ID
    """
    print('Client Disconnected')


@sio.event
async def command(sid, data):
    """
    Respond to a 'command' event from a socket.
    The data part of the command event should take the form:

    .. code-block:: json

      {"method": "set_units", "args":["mm", "km/h"]}


    Valid commands are methods which are part of the RadarIQ SDK.

    :param sid: Socket ID
    :param data: Data sent over the socketIO connection
    """

    # Check that the requested method exists
    invert_op = getattr(riq, data['method'], None)
    if callable(invert_op):
        try:
            args = data['args'] if 'args' in data else []  # Set default args if none were supplied
            print("Command", data['method'], args)
            invert_op(*args)  # Call the method
        except Exception as e:
            await sio.emit('message', str(e))
    else:
        await sio.emit('message', f"Method {data['method']} not found")


if __name__ == '__main__':
    web.run_app(app, port=8081)
