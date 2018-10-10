#!/usr/bin/env python
import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import wave
import time
import os

phoneconnections = []
browserconnections = []


HOST = 'example.ngrok.io' #Hostname where this server is running eg blah.ngrok.io
LVN = '415 555 1212' #Your Nexmo NUmber Here
		
class MainHandler(tornado.web.RequestHandler):
  def get(self):
    self.render("static/index.html", lvn=LVN, host=HOST)		
		
class WSHandler(tornado.websocket.WebSocketHandler):
  def open(self):
    print("phone connected")
    #Add the connection to the list of connections
    phoneconnections.append(self)
  def on_message(self, message):
    #Check if message is Binary or Text
    if type(message) != str:
      pass
    else:
      print(message)
      self.write_message('ok')
      for c in browserconnections:
        c.write_message(message)
  def on_close(self):
    #Remove the connection from the list of connections
    phoneconnections.remove(self)
    print("client disconnected")

class NCCOHandler(tornado.web.RequestHandler):
  def initialize(self):
    self._host = HOST
    self._template = tornado.template.Loader(".").load("ncco.json")
  def get(self):
    self.set_header("Content-Type", 'application/json')
    self.write(self._template.generate(
      host=self._host,
    ))
    self.finish()

class EventHandler(tornado.web.RequestHandler):
  def post(self):
    print(self.request.body)
    self.write('ok')
    self.set_header("Content-Type", 'text/plain')
    self.finish()

	
class SnakeHandler(tornado.websocket.WebSocketHandler):
  def open(self):
    print("browser connected")
    #Add the connection to the list of connections
    browserconnections.append(self)
  def on_message(self, message):
    print(message)
    data = message
    fn = 'audio/{}.wav'.format(data)
    f = wave.open(fn)
    lgth = f.getnframes()
    while f.tell() < lgth:
      data = f.readframes(320)
      for c in phoneconnections:
        c.write_message(data, binary=True)
  def on_close(self):
    browserconnections.remove(self)
    print("client disconnected")

static_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/')
application = tornado.web.Application([
                    (r'/s/(.*)', tornado.web.StaticFileHandler, {'path': static_path}),
                    (r'/', MainHandler),
										(r'/socket', WSHandler),
										(r'/event', EventHandler),
										(r'/snake', SnakeHandler),
                    (r'/ncco', NCCOHandler)])
if __name__ == "__main__":
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8000)
    tornado.ioloop.IOLoop.instance().start()

