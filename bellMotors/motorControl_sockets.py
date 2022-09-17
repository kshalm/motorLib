# -*- coding: utf-8 -*-
"""
Created on Wed Aug 19 13:08:38 2015

@author: qittlab

Porting to python3:

print statements and s.send need to be in bytes (hence .encode())
"""
import socket, select

class MotorController():
    def __init__(self, ip='127.0.0.1', timeout=None):
        port = 55000
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if timeout:
            self.s.settimeout(timeout)
        self.s.connect((ip, port))

        #msg = self.msgResponse()
        #print("connected")
        self.id_dict = {}
        self.get_name()
        print(self.id_dict)
#        self.s.send("Apt")
#        print("sent message")
#
#        motor_names = msg.split(',')[:-1]
#
#        for count, n in enumerate(motor_names):
#            self.id_dict[n] = count
#        print( self.id_dict

    def msgResponse(self):
        inputs = [self.s]
        outputs = []
        response = ''
        while inputs:
            readable, writable, exceptional = select.select(inputs, outputs, inputs)
            for s in readable:
                response += s.recv(1024).decode()
                #print( 'respone:',repr(response))
            if len(response)==0:
                break
            if response.lower().endswith('ack\n'):
                break
        return response[:-4]

    def _response(self):
        inputs = [self.s]
        outputs = []
        msg = True
        while inputs:
            #outMessage = []
            readable, writable, exceptional = select.select(inputs, outputs, inputs)
            for s in readable:
                response = s.recv(1024).decode()
                print('respone:',repr(response))
                #outMessage.append(repr(response))
            if len(response)==0:
                break
            if response.lower().startswith('error'):
                print("outputting error")
                msg = False
                outMessage = False
            if response.lower().endswith('ack\n'):
                break
        return msg

    def get_name(self):
        self.s.send("apt\n".encode())
        msg = self.msgResponse()
        motor_names = msg.split(',')[:-1]
        self.id_dict = {}
        for count, n in enumerate(motor_names):
            self.id_dict[n] = count
        return(self.id_dict)


    def forward(self, name, distance):
        print("%s forward %i" %(name, distance))
        outMessage = "for %s %i\n" % (distance, self.id_dict[name])
        self.s.send(outMessage.encode())
        self._response()


    def backward(self, name, distance):
        print("%s backward %i" %(name, distance))
        outMessage = "back %s %i\n" % (distance, self.id_dict[name])
        self.s.send(outMessage.encode())
        self._response()


    def goto(self, name, pos):
        print("Motor goto position %s" %pos)
        outMessage = "goto %s %i\n" % (pos, self.id_dict[name])
        self.s.send(outMessage.encode())
        self._response()

    def home(self, name):
        print("Homing %s" %name)
        outMessage = "home %i \n" %self.id_dict[name]
        self.s.send(outMessage.encode())
        self._response()

    def getAPos(self, name):
        """Get absolute position"""
        outMessage = 'getapos %i \n' %self.id_dict[name]
        self.s.send(outMessage.encode())
        pos = self.s.recv(1024).decode()
        print("%s absolute position: %s" %(name,pos))
        self._response()

    def getPos(self, name):
        #print("getpos %s" %name)
        outMessage = 'getpos %i \n' %self.id_dict[name]
        self.s.send(outMessage.encode())
        pos = self.s.recv(1024).decode()
        print("%s position: %s" %(name,pos))
        self._response()
        return pos

    def getAllPos(self):
        positions = {}
        for motorName in self.id_dict.keys():
            pos = (self.getPos(motorName))
            pos = float(pos)
            positions[motorName] = pos
        return positions

    def close(self):
        self.s.close()
        print("Closed socket.")

if __name__ == '__main__':
#    mc = MotorController('localhost')
#    mc.forward('Desk Motor',10)
#    mc.backward('Desk Motor', 20)
#    mc.forward('Linear Motor',1)
#    mc.home('Desk Motor')
#    mc.getPos('Desk Motor')
#    mc.goto('Linear Motor',1)
#    mc.getPos('Linear Motor')
#    mc_bob = MotorController('132.163.53.126')
#    mc_alice = MotorController('132.163.53.83')
#    mc_source = MotorController('132.163.53.83')
    localhost = '127.0.0.1'
    mc = MotorController(localhost)
#    mc_bob.getPos('BobHWP1')
#    mc_bob.goto('BobHWP1',301.63)
#    mc_bob.getPos('BobHWP1')
#    mc_alice.getPos('AliceHWP1')
#    mc_alice.goto('AliceHWP1',301.63)
#    mc_alice.getPos('AliceHWP1')
#    mc_source.getPos('AliceHWP2')
