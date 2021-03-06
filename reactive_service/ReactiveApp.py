# from flask import Flask, render_template
# from flask_sse import sse
#
# app = Flask(__name__)
#
# @app.route('/')
# def index():
#     return "hi"
#
#
# @app.route("/stream")
# def stream():
#     def eventStream():
#         while True:
#             # Poll data from the database
#             # and see if there's a new message
#             if len(messages) > len(previous_messages):
#                 yield "data: {}\n\n".format(messages[len(messages)-1])
#     return Response(eventStream(), mimetype="text/event-stream")
#
#
# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5000,threaded=True)  # Start a development server

import pathlib

from sanic import Sanic
from sanic.response import json
from sanic import response
import asyncio
from kafka import KafkaConsumer
import threading


app = Sanic("hello_example")

base_path = pathlib.Path(__file__).parent.absolute()
print(base_path.joinpath("kafka_auth/ca.pem"))
consumer = KafkaConsumer(
    "activity",
    bootstrap_servers="kafka-34f1d98c-sean98goldfarb-28b7.aivencloud.com:10402",
    client_id="demo-client-1",
    group_id=None,
    security_protocol="SSL",
    ssl_cafile=base_path.joinpath("kafka_auth/ca.pem"),
    ssl_certfile=base_path.joinpath("kafka_auth/service.cert"),
    ssl_keyfile=base_path.joinpath("kafka_auth/service.key"),
)


@app.route("/")
async def test(request):
    return json({"hello": "world"})


@app.route("/register/<user_id>/<type>")
async def register(request, user_id, type):
    async def streaming_fn(response):
        print(f'{user_id}-{type}-thread_id={threading.current_thread().ident}')  # DEBUG
        for message in consumer:
            # TODO distributed filtering (Kafka-Stream-Api / Spark...)
            if message['user_id'] == user_id and message['type'] == type:
                message = message.value
                print(message)
                await response.write(message)
    return response.stream(streaming_fn, content_type='text/plain')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, workers=4)
