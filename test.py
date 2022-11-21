import serial
import time
import logging
import pandas as pd
import datetime
#from influxdb import DataFrameClient
from crc16pure import crc16xmodem


def crc16(data, bts = 2):
    return crc16xmodem(data).to_bytes(bts, 'big')


QID    = b'QID\x18\x0b\r'
QPIGS  = b'QPIGS\xb7\xa9\r'
QPIGS2 = b'QPIGS2h-\r'
QPIRI  = b'QPIRI\xf8T\r'


class Invertor:

    def __init__(self, connect = True):
        self.debug = False

        if connect:
            self._open()



    def _open(self):
        self.serial = serial.Serial(
            port     = '/dev/ttyUSB0',
            baudrate = 2400,
            parity   = serial.PARITY_NONE,
            stopbits = serial.STOPBITS_ONE,
            bytesize = serial.EIGHTBITS
        )
        self.serial.flushInput()
        self.serial.flushOutput()
        if self.debug:
            logging.debug("Open serial port: <%s>" % self.serial)


    def reconnect(self):
        if self.serial.isOpen():
            self.serial.close()
            time.sleep(2)
        self._open()


    def readData(self, length):
        data = list()
        while 1:
            line = self.serial.read(1)
            data.append(line.decode('utf-8', 'ignore'))
            if ord(line) == 13:
                data = "".join(data)
                data = data[1:length].split(" ")
                print(data)
                if not data[0]:
                    if self.debug:
                        logging.debug("No data in 0 position call reconnect.")
                    self.reconnect()
                break
        return data


    def sendData(self, data):
        self.serial.write(data)


    def refreshData(self):
        self.serial.write(QID)
        data = self.readData(16)
        print (data)

        self.serial.write(QPIGS)
        data = self.readData(200)
        print (data)


    def set(self, command, value):
        crc = crc16(("%s%s" % (command, value)).encode(encoding = 'UTF-8'))
        com = ('%s%s' % (command, value)).encode(encoding = 'UTF-8')
        data = com + crc + b'\r'
        print (data)
        ret = self.serial.write(data)

        print ("Ret: %s" % ret)
        return self.readData(ret)


    def setChargeCurrent(self, value):
        value = "%s".zfill(4) % value
        return self.set("MNCHGC", value)


    def getGeneralStatus(self):
        self.serial.write(QPIRI)
        data = self.readData(100)

        print (data)


    def crc(self, value, bts = 2):
        crc = crc16(value.encode(encoding = 'UTF-8'))
        data = crc + b'\r'
        print (value, data)


inv = Invertor(False)
#inv = Invertor()

# set utiliti charge
#print (inv.setChargeCurrent(10))

while 1:
    #inv.refreshData()

    inv.sendData(QPIGS2)
    inv.readData(120)
    time.sleep(3)
