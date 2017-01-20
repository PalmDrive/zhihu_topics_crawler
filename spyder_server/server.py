# coding:utf8
import tornado.web
import tornado.ioloop
import uuid
import json
from task import *


class MainHandler(tornado.web.RequestHandler):
    def get(self, act):
        self.write({
            "hello": "world"
        })


class RegisterHandler(tornado.web.RequestHandler):
    def get(self):
        spiderid =  uuid.uuid4().hex
        print 'onlined:%s'%(spiderid)
        self.write({"id":spiderid})


class LogoutHandler(tornado.web.RequestHandler):
    def get(self, id):
        self.write({})


class TaskHandler(tornado.web.RequestHandler):
    def send_cmd(self):
        pending_list = get_pending()
        if pending_list:
            self.write({
                "act": "fetch",
                "target:": map(lambda x: x.get("task_list"), pending_list)
            })
        else:
            self.write({"task":
                            "quit"})


    def get(self, id):
        print 'id:%s is asking task..' % (id)
        self.send_cmd()

    def post(self, id):
        data = self.get_body_argument("data")
        data = json.loads(data)
        id = data["id"]
        result = data["result"]
        print 'id:%s finished task..' % (id)
        complete_task(result)
        self.send_cmd()


app = tornado.web.Application([
    (r"/logout/(.*)", LogoutHandler),
    (r"/register", RegisterHandler),
    (r"/task/(.*)", TaskHandler),
    (r"/(.*)", MainHandler),
])

app.listen(63360, "0.0.0.0")

tornado.ioloop.IOLoop.current().start()

