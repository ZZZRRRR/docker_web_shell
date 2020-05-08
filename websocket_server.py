import paramiko
import tornado.websocket
import asyncio
import docker_commands
from redis_token import redis_token
from timer import timer,start_timer
from tornado.ioloop import IOLoop


class docker_websocketHandler(tornado.websocket.WebSocketHandler):

    clients = dict()

    def initialize(self,loop):
        super(docker_websocketHandler,self)
        self.loop = loop

    def check_origin(self, origin):
        return True

    #当建立连接时调用open函数
    def open(self):
        # print("websocket opened")
        self.connection = False
        #启动websocket校验计时器，一定时间不发送token验证，自动断开连接
        self.start_timer = start_timer()
        self.ws_loop = asyncio.get_event_loop()
        self.start_timer.start(self.close,self.ws_loop)

     #收到消息时调用on_message函数
    async def on_message(self, message):
        #对第一条消息进行token校验
        if not self.connection:
            r = redis_token()
            if r.check(message):
                self.close(reason="token test failed")
            else:
                self.start_timer.remove()
                id = r.get(message)
                self.id = [id[1],id[2]]
                self.connection = True
                self.action = True
                self.shell = await self.ssh_channel(id[0])
                self.fd = self.shell.fileno()
                await self.start_connecting()
                r.remove(message)
                self.loop.add_handler(self.fd,self.on_read,IOLoop.READ)
                docker_websocketHandler.clients[id[1]] = self
                # print(docker_websocketHandler.clients)
        else:
            self.action = True
            await self.on_write(message)
            # print(message)

    def on_read(self,fd,events):
        if events & IOLoop.READ:
            try:
                data = self.shell.recv(65535).decode('utf8')
                if data == "":
                    # print("may be input exit")
                    self.trans.close()
                    self.close()
                    self.loop.remove_handler(self.fd)
                else:
                    self.write_message(data)
                    self.action = True
            except:
                pass

    async def on_write(self,message):
        try:
            self.shell.send(message)
        except:
            self.close(reason='ssh closed')

    def on_close(self):
        try:
            #关闭连接后删除计时任务
            self.timer.remove()
            self.loop.remove_handler(self.fd)
            self.trans.close()
            # print("websocket closed")
        except:
            # print("token test failed")
            pass
        try:
            if self.id[0] in docker_websocketHandler.clients:
                docker_commands.exit1(self.id[0],self.id[1])
                del docker_websocketHandler.clients[self.id[0]]
        except:
            pass

    async def ssh_channel(self,ip):
        self.trans = paramiko.Transport((ip, 22))
        self.trans.start_client()
        self.trans.auth_password(username="123", password="1")
        channel = self.trans.open_session()
        channel.get_pty(term="xterm",width=100,height=52,width_pixels=0,height_pixels=0)
        channel.invoke_shell()
        return channel

    async def start_connecting(self):
        BUF_SIZE = 65535
        self.shell.send(' ')
        await asyncio.sleep(0.1)
        message = self.shell.recv(BUF_SIZE).decode('utf8')
        await self.write_message(message)
        self.timer_start()

    def timer_start(self):
        self.timer = timer()
        self.timer.start(self.timer_check,self.timer_set,self.close,self.ws_loop)

    def timer_check(self):
        return self.action

    def timer_set(self):
        self.action = False
