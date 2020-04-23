import json
import tornado.web
import docker_commands
import hashlib
import os
import asyncio
from redis_token import redis_token
from websocket_server import docker_websocketHandler


class openHandler(tornado.web.RequestHandler):

    def initialize(self):
        self.set_default_header()

    def set_default_header(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Headers', '*')
        self.set_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, PATCH, OPTIONS')
        self.set_header('Content-Type', 'application/json; charset=UTF-8')
        self.set_header('Access-Control-Allow-Headers', 'Content-Type')

    def options(self):
        self.finish()

    async def post(self):
        r = redis_token()
        post_data = self.request.body.decode('utf-8')
        post_data = json.loads(post_data)
        # print(post_data)
        if post_data["exec"] == "start1":
            send_data = docker_commands.start1(post_data["usrID"],str(post_data["proID"]))
            # print(send_data)
        elif post_data["exec"] == "start2":
            send_data = docker_commands.start2(post_data["usrID"],str(post_data["proID"]))
        elif post_data["exec"] == "restart":
            send_data = docker_commands.restart(post_data["usrID"], str(post_data["proID"]))
        else:
            send_data = {"error": "no such execution"}
        #如果操作执行成功，产生token并返回
        if "error" not in send_data:
            token = hashlib.sha1(os.urandom(24)).hexdigest()
            send_data["token"] = token
            r.add(token,[send_data["containerIP"],post_data["usrID"],str(post_data["proID"])])
        self.write(json.dumps(send_data))


class exitHandler(tornado.web.RequestHandler):
    def initialize(self):
        self.set_default_header()

    def set_default_header(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Headers', '*')
        self.set_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, PATCH, OPTIONS')
        self.set_header('Content-Type', 'application/json; charset=UTF-8')
        self.set_header('Access-Control-Allow-Headers', 'Content-Type')

    def options(self):
        self.finish()

    async def post(self):
        post_data = self.request.body.decode('utf-8')
        post_data = json.loads(post_data)
        # print(post_data)
        if post_data["exec"] == "exit1":
            send_data = docker_commands.exit1(post_data["usrID"],str(post_data["proID"]))
        elif post_data["exec"] == "exit2":
            send_data = docker_commands.exit2(post_data["usrID"], str(post_data["proID"]))
        elif post_data["exec"] == "exit3":
            r = redis_token()
            send_data = docker_commands.exit3(post_data["usrID"], str(post_data["proID"]))
            token = hashlib.sha1(os.urandom(24)).hexdigest()
            send_data["token"] = token
            r.add(token,[send_data["containerIP"],post_data["usrID"],str(post_data["proID"])])
            docker_websocketHandler.clients[post_data["usrID"]].close()
            del docker_websocketHandler.clients[post_data["usrID"]]
            # print(r.get(token))
        else:
            send_data = {"error": "no such execution"}
        self.write(json.dumps(send_data))
