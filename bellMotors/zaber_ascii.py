from sys import platform
import serial
import struct
import time
import zaber.serial


"""
zaber motor library using zaber.serial:
http://www.zaber.com/support/docs/api/core-python/0.8.1/

NOTE: T-series does not support ASCII. Therefore do not use this library with the T-OMG

Notes:
- Are the replies for data returning the actual data?
- Figure out potentiometer, backlack, stiction (see version)
- Passing device to a command is no longer a number (list of AsciiDevices)
        should self.devices be a dictionary?
-Add windows compatibility in connect
"""

class zaber_base():
    def __init__(self, port, devices = [1],timeout = 1, chNames = ''):
        self.port = port
        self.struct = struct.Struct('<2Bi')
        self.packet_size = self.struct.size
        self.ser = self.connect(self.port, timeout)
        print(self.ser)
        self.devices = self.init_devices(devices) #creates AsciiDevice from each # in devices

        self.potentiometer = 0
        self.backlash = 1
        self.stiction = 1
        self.LED = 1
#        knob_speed = 0.05 #deg/s

        for i in devices:
            self.backlash_correction(i, self.backlash)
#            self.set_speed_knob(i, knob_speed)
#            self.set_speed_profile_knob(i, 1) # linear response
    """
        count = 0
        while(len(self.ser.read(50))!=0):
            count += 1
            returnMsgCoded = self.ser.read(self.packet_size)
            returnMsg = self.struct.unpack(returnMsgCoded)
            self.ser.flushInput()
            self.ser.flushOutput()
            print(str(count), str(returnMsg))
    """

    def init_devices(self, devices):
        asciiDevices = []
        for device in devices:
            device = AsciiDevice(self.ser, device)
            asciiDevices.append(device)
        return asciiDevices
        
    def connect(self, port, timeout=1):
        if platform == "linux" or platform == "linux2":
            port = "/dev/ttyUSB"+str(port)
            port = str(port) 
        elif platform == "win32":
            #ADD WINDOWS COM PORT CONNECTION
        else:
            print("Platform %r not recognized." % platform)
            return -1
        try:
            print("Connecting to port: ", port)
            ser = AsciiSerial(port) #can we add a timeout?
        except:
            print("Could not connect to port", port)
            ser = -1
        return ser

    def close(self):
        try:
            self.ser.close()
        except:
            print("Could not close port", self.port)
            
    # Helper to check that commands succeeded.
    def check_command_succeeded(reply):
        """
        Return true if command succeeded, print reason and return false if command
        rejected
        """
        if reply.reply_flag != "OK": # If command not accepted (received "RJ")
            print ("Danger! Command rejected because: {}".format(reply.data))
            return False
        else: # Command was accepted
            return True

    def home(self, device):
        if device in self.devices:
            reply = device.home()
            result = self.check_command_succeeded(reply)
            return result
        else:
            print("No device: ", device)
            return None
            
    def renumber(self):
        command = AsciiCommand("renumber")
        self.ser.write(command)
        reply = self.ser.read()
        result = self.check_command_succeeded(reply)
        return result
            
    def reset(self, device):
        if device in self.devices:
            command = AsciiCommand("system reset")
            reply = device.send(command)
            result = self.check_command_succeeded(reply)
            return result
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
            command = AsciiCommand("set maxspeed", steps)
            reply = device.send(command)
            result = self.check_command_succeeded(reply)
            if result:
                return(reply.data) #TODO: is this returnSpeed as below?
            else:
                return None
            """
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
            """
            
    def set_speed_knob(self, device, speed):   # Speed is in degrees/second
        if device in self.devices:
            res = 0.000115378 # microstep size.
            maxSpeed = 6
            
            if speed>maxSpeed:
                speed = maxSpeed #Maximum speed in degrees/second
                
            steps = round(speed*1./(res*1.6))
            
            command = AsciiCommand("set knob.maxspeed", steps)
            reply = device.send(command)
            result = self.check_command_succeeded(reply)
            if result:
                return(reply.data) #see set_speed
            else:
                return None
            
    def set_speed_profile_knob(self, device, profile = 2):
        # profile: 1 = linear, 2 = quadratic, 3= cubic
        if device in self.devices:
            command = AsciiCommand("set knob.forceprofile", profile)
            reply = device.send(command)
            result = self.check_command_succeeded(reply)
            if result:
                return(reply.data) #see set_speed
            else:
                return None
            
    def set_acc(self, device, acc = 111):   # Default is 111
        if device in self.devices:
            maxAcc = 111
            
            if acc>maxAcc:
                acc = maxAcc #Maximum speed in degrees/second
            
            command = AsciiCommand("set accel", acc)
            reply = device.send(command)
            result = self.check_command_succeeded(reply)
            if result:
                return(reply.data)
            else:
                return None

            
    def set_speed_all(self, speed):   # Speed is in degrees/second
        for device in self.devices:
            self.set_speed(device, speed)
            
    def set_acc_all(self, acc):   # Default is 111
        for device in self.devices:
            self.set_acc(device, acc)
            
    def get_speed(self,device): 
        if device in self.devices:
            command = AsciiCommand("get maxspeed")
            reply = device.send(command)
            result = self.check_command_succeeded(reply)
            if result:
                return(reply.data)
            else:
                return None
        else:
            print("No device: ", device)
            return None
            
    def get_speed_knob(self,device): 
        if device in self.devices:
            command = AsciiCommand("get knob.maxspeed")
            reply = device.send(command)
            result = self.check_command_succeeded(reply)
            if result:
                return(reply.data)
            else:
                return None
        else:
            print("No device: ", device)
            return None
            
    def get_profile_knob(self,device): 
        if device in self.devices:
            command = AsciiCommand("get knob.forceprofile")
            reply = device.send(command)
            result = self.check_command_succeeded(reply)
            if result:
                return(reply.data)
            else:
                return None
        else:
            print("No device: ", device)
            return None
            
    def get_acc(self,device): 
        if device in self.devices:
            command = AsciiCommand("get accel")
            reply = device.send(command)
            result = self.check_command_succeeded(reply)
            if result:
                return(reply.data)
            else:
                return None
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
            command = AsciiCommand("move rel", steps)
            reply = device.send(command)
            result = self.check_command_succeeded(reply)
            if result:
                return(reply.data)
            else:
                return None
        else:
            print("No device: ", device)
            return None
            
    def move_absolute(self, device, pos):
        if device in self.devices:
            command = AsciiCommand("move abs", pos)
            reply = device.send(command)
            result = self.check_command_succeeded(reply)
            if result:
                return(reply.data)
            else:
                return None
        else:
            print("No device: ", device)
            return None

    def get_position(self, device):
        if device in self.devices:
            command = AsciiCommand("get pos")
            reply = device.send(command)
            result = self.check_command_succeeded(reply)
            if result:
                return(reply.data)
            else:
                return None
            return(position)
        else:
            print("No device: ", device)
            return None

#Firmware stuff not converted to ASCII yet
    def get_firmware_cmd(self, device):
        #return(8*self.potentiometer + 2*self.backlash + 4*self.stiction + (2**14 + 2**15)*self.LED)
        command = AsciiCommand("get version")
        reply = device.send(command)
        result = self.check_command_succeeded(reply)
        if result:
            return(reply.data)
        else:
            return None
    
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

    def poll_until_idle(self, device):
        if device in self.devices:
            device.poll_until_idle()
        else:
            print ("No device, ", device)
            return None
            
            
    def write(self, device, action, parameters=None):
        try:
            command = AsciiCommand(action, parameters)
            reply = device.send(command)
            result = self.check_command_succeeded(reply)
            if result:
                return(reply.data)
            else:
                return None
        except:
            print("Failed to write: ", action, parameters)     
    
    def read(self):
        try:
            reply = self.ser.read()
            result = self.check_command_succeeded(reply)
            if result:
                return(reply.data)
            else:
                return None
        except:
            return('')

    def LED_enabled(self, device, enabled = True):
        if device in self.devices:
            if enabled:
                self.LED = 0
            else:
                self.LED = 1
            command = AsciiCommand("set system.led.enable", self.LED)
            reply = device.send(command)
            result = self.check_command_succeeded(reply)
            if result:
                return(reply.data)
            else:
                return None
            time.sleep(0.1)

#
#port = 20 # COM port for the Zaber Motor.
#channels =  [1,2,3,4]
#zb = zaber_base(port, channels)
