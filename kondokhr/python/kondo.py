from flask import Flask, render_template, request
import time
import sys
import json
# encoding=utf8

from pykondo import *
from twisted.python import log
from twisted.internet import reactor
from twisted.web.server import Site
from twisted.web.wsgi import WSGIResource
from autobahn.twisted.websocket import WebSocketServerFactory, \
    WebSocketServerProtocol
app = Flask(__name__)
from autobahn.twisted.resource import WebSocketResource, WSGIRootResource


class EchoServerProtocol(WebSocketServerProtocol):

    def onMessage(self, payload):
        message = payload.decode('utf8')
        message = json.loads(message)
		komut = message["komut"]
		if komut == "tek_motor_kontrol":
			servo_id = message["servo_id"]
			frame = message["frame"]
			print servo_id + frame
			realKondo.setServoPos(servo_id, frame)
		elif komut == "hareket_oynat":
			print "Henuz Eklenmedi"
	
		self.sendMessage(payload)
	

@app.route('/', methods=['POST', 'GET'])
def hello_world():
    if request.method == "POST":
        try:          
            hareket_adi = request.json['hareket_adi']
            realKondo.playMotion(motions[hareket_adi])
        except Exception as e:
            print (e.message)
    
    return render_template('tasarim.html')

def deneme():
	
	servo_ids = [0, 2, 3,4,5,8,9,12,13,14,15,16,17,18,19,20,21]
	pos1 = [7500, 7500, 7500,7500,7500,7500,7500,7500,7500 ,10000, 5000, 8000, 7000, 8200, 6800, 7500, 7500]
	pos2 = [7500, 7500, 7500,7500,7500,7500,7500,7500,7500 ,7500, 7500, 7500, 7500, 7500, 7500, 7500, 7500]
	durum = False
	for k in range(17):
		if pos1[k] < 11500 and pos1[k] > 3500:
			print servo_ids[k]
			print pos1[k]
			realKondo.setServoPos(servo_ids[k], pos1[k])
	for s in range(17):
		if pos2[s] < 11500 and pos2[s] > 3500:
			print servo_ids[s]
			print pos2[s]
			realKondo.setServoPos(servo_ids[s], pos2[s])
class DummyKondo(object):
    def __init__(self):
        print("DummyCondo olusturuldu")

    def readBatteryLevel(self):
        return ("Batarya Leveli Super")

    def playMotion(self, motion_id):
        time.sleep(60)
        print ("Playing Kondo Motion %", motion_id)

    def close(self):
        print ("DummyKondo yorgun....kapandi.......")

class RealKondo(object):
    def __init__(self):
        self.max_wait = 50 * 1000000
        self.ki = KondoInstance()
        ret = kondo_init(self.ki)
        print(self.ki.error)
        
    def setServoPos(self, id, frame):
		ret = kondo_set_servo_pos(self.ki, int(id), int(frame))

    def playMotion(self, motion_id):
        print ("Playing Kondo Motion %", motion_id)
        ret = kondo_play_motion(self.ki, motion_id, self.max_wait)
    def hareketEt(self, pos):
    	#Calismiyor
		ret = kondo_hareket(self.ki, pos)
        if ret < 0:
            sys.exit(self.ki.error)
    def close(self):
        ret = kondo_close(self.ki)
        if ret < 0:
            sys.exit(self.ki.error)
            
if __name__ == '__main__':
    motions = {
        "Greeting": 0,
        "Home Position": 1,
        "Wave": 2,
        "HipHipHipHurray": 3,
        "Chagrined": 4,
        "Headstand": 5,
        "Clap": 6,
        "10 Claps": 7,
        "Rythm Claps": 8,
        "Push-Ups": 9,
        "One Legged Bend": 10,
        "Bunny Hop A": 11,
        "Bunny Hop B": 12,
        "Stand-Up Stomach": 13,
        "Stand-Up Back": 14,
        "Safewalk Forward": 15,
        "Safewalk Backward": 16,
        "Safewalk Left": 17,
        "Safewalk Right": 18,
        "Quickturn Left": 19,
        "Quickturn Right": 20,
        "Regular Walk Forward": 21,
        "Regular Walk Back": 22,
        "Regular Walk Left": 23,
        "Regular Walk Right": 24,
        "Kick Ball Fwd Left": 25,
        "Kick Ball Fwd Right": 26,
        "Kick Ball Side Left": 27,
        "Kick Ball Side Right": 28,
        "Kick Ball Backwd Left": 29,
        "Kick Ball Backwd Right": 30
    }


    try:

	realKondo = RealKondo()
	
    except Exception as e:
        e.message
    

    
    log.startLogging(sys.stdout)  # create a Twisted Web resource for our WebSocket server
    wsFactory = WebSocketServerFactory(u"ws://0.0.0.0:8080")
    wsFactory.protocol = EchoServerProtocol
    wsResource = WebSocketResource(wsFactory)

    # create a Twisted Web WSGI resource for our Flask server
    wsgiResource = WSGIResource(reactor, reactor.getThreadPool(), app)

    # create a root resource serving everything via WSGI/Flask, but
    # the path "/ws" served by our WebSocket stuff
    rootResource = WSGIRootResource(wsgiResource, {b'ws': wsResource})

    # create a Twisted Web Site and run everything
    site = Site(rootResource)

    reactor.listenTCP(8080, site)
    reactor.run()



