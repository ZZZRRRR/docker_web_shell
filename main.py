import websocket_server
import web_server
from tornado.ioloop import IOLoop
import tornado.options
import logging
import os
from redis_token import redis_token

def make_app(loop):
    return tornado.web.Application([
        (r"/open", web_server.openHandler),
        (r"/exit", web_server.exitHandler),
        (r"/websocket",websocket_server.docker_websocketHandler,dict(loop=loop))
    ])

def main():
    tornado.options.define("port", default=8081, help="run on the given port", type=int)
    tornado.options.define("bind",default="192.168.11.184",help="address")
    tornado.options.parse_command_line()
    loop = tornado.ioloop.IOLoop.current()
    app = make_app(loop)
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.bind(tornado.options.options.port,tornado.options.options.bind)
    # http_server.bind(8081)
    http_server.start()
    print("sever start at port 8081 ...")
    loop.start()


if __name__ == "__main__":
    main()