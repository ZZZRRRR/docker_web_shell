import redis
import json

class redis_token:
    pool = redis.ConnectionPool(host='localhost', port=6379, decode_responses=True)

    def __init__(self):
        self.r = redis.Redis(connection_pool=redis_token.pool)

    def add(self,token,info):
        i = json.dumps(info)
        self.r.setex(token,60,i)

    def check(self,token):
        return 0 if self.r.exists(token) and self.r.get(token) != None else 1

    def get(self,token):
        return json.loads(self.r.get(token))

    def remove(self,token):
        self.r.delete(token)

