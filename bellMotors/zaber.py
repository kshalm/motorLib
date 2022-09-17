import serial
import struct
import time

class zaber_base():
    def __init__(self, port, devices = [1],timeout = 1, chNames = ''):
        self.devices = devices
        self.port = port
        self.struct = struct.Struct('<2Bi')
        self.packet_size = self.struct.size
        self.ser = self.connect(self.port, timeout)
        print(self.ser)

        self.potentiometer = 0
        self.backlash = 1
        self.stiction = 1
        self.LED = 1
#        knob_speed = 0.05 #deg/s

        for i in devices:
            self.backlash_correction(i, self.backlash)
#            self.set_speed_knob(i, knob_speed)
#            self.set_speed_profile_knob(i, 1) # linear response
        count = 0
        while(len(self.ser.read(50))!=0):
            count += 1
            returnMsgCoded = self.ser.read(self.packet_size)
            returnMsg = self.struct.unpack(returnMsgCoded)
            self.ser.flushInput()
            self.ser.flushOutput()
            print(str(count), str(returnMsg))

        
    def connect(self, port, timeout=1):
        port = "/dev/ttyUSB"+str(port)
        port = str(port) 
        try:
            print("Connecting to port: ", port)
            ser = serial.Serial(port, timeout = timeout)
            if ser.isOpen():
                ser.flushInput()
        except:
            print("Could not connect to COM port", port)
            ser = -1
        return ser

    def close(self):
        try:
            self.ser.close()
        except:
            print("Could not close COM port", self.port)

    def home(self, device):
        if device in self.devices:
            action = 1
            self.write(device, action)
            
            replyDevice = -1
            replyAction = -1
            reply = [0,0,0]
            while replyDevice != device and replyAction != action:
                reply = self.read()
                try:
                    replyDevice = reply[0]
                    replyAction = reply[1]
                except:
                    pass
            ans = reply[2]
            return(ans)
            
#        if device in self.devices:
#            msg = (device, 1, 0)
#            msgCode = apply(self.struct.pack, msg)
#            self.ser.write(msgCode)
#            returnMsgCoded = self.ser.read(self.packet_size)
##            curPos = self.struct.unpack(returnMsgCoded)[2]
##            return curPos
        else:
            print("No device: ", device)
            return None
            
    def renumber(self):
        msg = (0, 2, 0)
        msgCode = apply(self.struct.pack, msg)
        self.ser.write(msgCode)
        time.sleep(4)
        returnMsgCoded = self.ser.read(self.packet_size)
        
        
            
    def reset(self, device):
        if device in self.devices:
            msg = (device, 0, 0)
            msgCode = apply(self.struct.pack, msg)
            self.ser.write(msgCode)
            #returnMsgCoded = self.ser.read(self.packet_size)
            #curPos = self.struct.unpack(returnMsgCoded)[2]
            #return curPos
        else:
            print("No device: ", device)
            #return None

    def set_speed(self, device, speed):   # Speed is in degrees/second
        if device in self.devices:
            action = 42
            res = 0.000115378 # microstep size.
            maxSpeed = 6
            
            if speed>maxSpeed:
                speed = maxSpeed #Maximum speed in degrees/second
                
            steps = round(speed*1./(res*1.6))
            
            self.write(device, action, steps)
            
            replyDevice = -1
            replyAction = -1
            reply = [0,0,0]
            
            while replyDevice != device and replyAction != action:
                reply = self.read()
                replyDevice = reply[0]
                replyAction = reply[1]
            returnSpeed = reply[2]
            return(returnSpeed) 
            
    def set_speed_knob(self, device, speed):   # Speed is in degrees/second
        if device in self.devices:
            action = 111
            res = 0.000115378 # microstep size.
            maxSpeed = 6
            
            if speed>maxSpeed:
                speed = maxSpeed #Maximum speed in degrees/second
                
            steps = round(speed*1./(res*1.6))
            
            self.write(device, action, steps)
            
            replyDevice = -1
            replyAction = -1
            reply = [0,0,0]
            
            while replyDevice != device and replyAction != action:
                reply = self.read()
                replyDevice = reply[0]
                replyAction = reply[1]
            returnSpeed = reply[2]
            return(returnSpeed)
            
    def set_speed_profile_knob(self, device, profile = 2):
        # profile: 1 = linear, 2 = quadratic, 3= cubic
        if device in self.devices:
            action = 111 #Should this be 112? -Collin (7/10)
            
            self.write(device, action, profile)
            
            replyDevice = -1
            replyAction = -1
            reply = [0,0,0]
            
            while replyDevice != device and replyAction != action:
                reply = self.read()
                replyDevice = reply[0]
                replyAction = reply[1]
            returnSpeed = reply[2]
            return(returnSpeed)
            
    def set_acc(self, device, acc = 111):   # Default is 111
        if device in self.devices:
            action = 43
            maxAcc = 111
            
            if acc>maxAcc:
                acc = maxAcc #Maximum speed in degrees/second
            
            self.write(device, action, acc)
            
            replyDevice = -1
            replyAction = -1
            reply = [0,0,0]
            
            while replyDevice != device and replyAction != action:
                reply = self.read()
                replyDevice = reply[0]
                replyAction = reply[1]
            returnSpeed = reply[2]
            return(returnSpeed)
            
    def set_speed_all(self, speed):   # Speed is in degrees/second
        for device in self.devices:
            self.set_speed(device, speed)
            
    def set_acc_all(self, acc):   # Default is 111
        for device in self.devices:
            self.set_acc(device, acc)
            
    def get_speed(self,device): 
        if device in self.devices:
            action = 53
            cmd = 42
            self.write(device, action, cmd)
            
            replyDevice = -1
            replyAction = -1
            reply = [0,0,0]
            
            while replyDevice != device and replyAction != cmd:
                
                reply = self.read()
                #print(reply)
                replyDevice = reply[0]
                replyAction = reply[1]
            speed = reply[2]
            return(speed)
            
        else:
            print("No device: ", device)
            return None
            
    def get_speed_knob(self,device): 
        if device in self.devices:
            action = 53
            cmd = 111
            self.write(device, action, cmd)
            
            replyDevice = -1
            replyAction = -1
            reply = [0,0,0]
            
            while replyDevice != device and replyAction != cmd:
                reply = self.read()
                replyDevice = reply[0]
                replyAction = reply[1]
            speed = reply[2]
            return(speed)
            
        else:
            print("No device: ", device)
            return None
            
    def get_profile_knob(self,device): 
        if device in self.devices:
            action = 53
            cmd = 112
            self.write(device, action, cmd)
            
            replyDevice = -1
            replyAction = -1
            reply = [0,0,0]
            
            while replyDevice != device and replyAction != cmd:
                reply = self.read()
                replyDevice = reply[0]
                replyAction = reply[1]
            speed = reply[2]
            return(speed)
            
        else:
            print("No device: ", device)
            return None
            
    def get_acc(self,device): 
        if device in self.devices:
            action = 53
            cmd = 43
            self.write(device, action, cmd)
            
            replyDevice = -1
            replyAction = -1
            reply = [0,0,0]
            
            while replyDevice != device and replyAction != cmd:
                reply = self.read()
                replyDevice = reply[0]
                replyAction = reply[1]
            acc = reply[2]
            return(acc)
            
        else:
            print("No device: ", device)
            return None
            
    def get_speed_all(self):   
        speeds = [-1] * len(self.devices)
        for i in range(len(self.devices)):
            print("Device number:", self.devices[i])
            speeds[i] = self.get_speed(self.devices[i])      
        return(speeds)
    
    def get_acc_all(self):   
        accs = [-1] * len(self.devices)
        for i in range(len(self.devices)):
            #print("Device number:", self.devices[i])
            accs[i] = self.get_acc(self.devices[i])      
        return(accs)
        
    def move_relative(self, device, steps):   
        if device in self.devices:
            action = 21
            #print("move : ", steps)
            self.write(device, action, steps)
            
            replyDevice = -1
            replyAction = -1
            reply = [0,0,0]
            
            read_response = True
            while read_response == True:
                reply = self.read()
                if reply == '':
                    replyDevice = -1
                    replyAction = -1
                else:
                    replyDevice = reply[0]
                    replyAction = reply[1]
#                
                if replyDevice == device and replyAction == action:
                  read_response = False  
            position = reply[2]
            return(position)
        else:
            print("No device: ", device)
            return None
            
    def move_absolute(self, device, pos):
        if device in self.devices:
            action = 20
            self.write(device, action, pos)
            
            replyDevice = -1
            replyAction = -1
            reply = [0,0,0]
            
            read_response = True
            while read_response == True:
                reply = self.read()
                
                if reply == '':
                    replyDevice = -1
                    replyAction = -1
                #print("reply", reply)
                else:
                    replyDevice = reply[0]
                    replyAction = reply[1]
                    
#                replyDevice = reply[0]
#                replyAction = reply[1]    
#                
                if replyDevice == device and replyAction == action:
                  read_response = False            
           
#           while replyDevice != device and replyAction != action:
#                reply = self.read()
#                if reply == '':
#                    replyDevice = -1
#                    replyAction = -1
#                #print("reply", reply)
#                else:
#                    replyDevice = reply[0]
#                    replyAction = reply[1]
                    
            position = reply[2]
            return(position)
            
#        if device in self.devices:
#            msg = (device, 20, pos)
#            msgCode = apply(self.struct.pack, msg)
#            self.ser.write(msgCode)
#            self.poll_until_idle(device)
#            while True:
#                returnMsgCoded = self.ser.read(self.packet_size)
#                if len(returnMsgCoded)==6:
#                    break
#            curPos = self.struct.unpack(returnMsgCoded)[2]
#            #print "Current Position: ", curPos
#            return curPos
            
        else:
            print("No device: ", device)
            return None

    def get_position(self, device):
        if device in self.devices:
            action = 60
            self.write(device, action)
            
            replyDevice = -1
            replyAction = -1
            reply = [0,0,0]
#            while replyDevice != device and replyAction != action:
#                reply = self.read()
#                #print(reply)
#                replyDevice = reply[0]
#                replyAction = reply[1]
            read_response = True
            while read_response == True:
                reply = self.read()
                
                if reply == '':
                    replyDevice = -1
                    replyAction = -1
                #print("reply", reply)
                else:
                    replyDevice = reply[0]
                    replyAction = reply[1]
                    
#                replyDevice = reply[0]
#                replyAction = reply[1]    
#                
                if replyDevice == device and replyAction == action:
                  read_response = False        
                
            #print("final reply", reply)
            position = reply[2]
            return(position)
            
        else:
            print("No device: ", device)
            return None


    def get_firmware_cmd(self):
        return(8*self.potentiometer + 2*self.backlash + 4*self.stiction + (2**14 + 2**15)*self.LED)
    
    def backlash_correction(self, device, enabled = False):
        if device in self.devices:
            if enabled:
                self.backlash= 1
            else:
                self.backlash = 0
            cmd = self.get_firmware_cmd()
            msg = (device, 40, cmd)
            msgCode = apply(self.struct.pack, msg)
            self.ser.write(msgCode)
            while True:
                returnMsgCoded = self.ser.read(self.packet_size)
                if len(returnMsgCoded)==6:
                    break
            returnMsg = self.struct.unpack(returnMsgCoded)
            time.sleep(.1)

    def stiction_correction(self, device, enabled = False):
        if device in self.devices:
            if enabled:
                self.stiction = 1
            else:
                self.stiction = 0
            cmd = self.get_firmware_cmd()
            msg = (device, 40, cmd)
            msgCode = apply(self.struct.pack, msg)
            self.ser.write(msgCode)
            returnMsgCoded = self.ser.read(self.packet_size)
            returnMsg = self.struct.unpack(returnMsgCoded)
            time.sleep(0.1)
            
    def potentiometer_enabled(self, device, enabled = True):
        if device in self.devices:
            #print(enabled)
            if enabled:
                self.potentiometer = 0
            else:
                self.potentiometer = 1
            cmd = self.get_firmware_cmd()
            msg = (device, 40, cmd)
            msgCode = apply(self.struct.pack, msg)
            self.ser.write(msgCode)
            returnMsgCoded = self.ser.read(self.packet_size)
            returnMsg = self.struct.unpack(returnMsgCoded)
            time.sleep(0.1)
            
#    def poll_until_idle(self, device):
#        if device in self.devices:
#            status = 1
#            while status > 0:
#                self.write(device, 55)
#                reply = self.read()
#                status = reply[2]
#                time.sleep(0.05)
            
            
    def write(self, device, action, cmd = 0):
        try:
            msg = (device, action, cmd)
            msgCode = apply(self.struct.pack, msg)
            self.ser.write(msgCode)
        except:
            print("Failed to write: ", msg)     
    
    def read(self):
        try:
            returnMsgCoded = self.ser.read(self.packet_size)
            if len(returnMsgCoded)==6:
                returnMsg = self.struct.unpack(returnMsgCoded)
                #print(returnMsg)
                return returnMsg
            else:
                return('')
        except:
            return('')
        


    def LED_enabled(self, device, enabled = True):
        if device in self.devices:
            if enabled:
                self.LED = 0
            else:
                self.LED = 1
            cmd = self.get_firmware_cmd()
            msg = (device, 40, cmd)
            msgCode = apply(self.struct.pack, msg)
            self.ser.write(msgCode)
            returnMsgCoded = self.ser.read(self.packet_size)
            returnMsg = self.struct.unpack(returnMsgCoded)
            time.sleep(0.1)

#
#port = 20 # COM port for the Zaber Motor.
#channels =  [1,2,3,4]
#zb = zaber_base(port, channels)
