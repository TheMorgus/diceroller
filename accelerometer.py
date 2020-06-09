import RPi.GPIO as GPIO
from time import sleep
from decimal import *

HALFCYCLE = 0.000001 #10 microsecond half cycle period
SCLK = 5 #GPIO 2; Serial Communications Clock
SDI = 3 #GPIO 3; Serial Data Input
SDO = 7 #GPIO 4; Serial Data Output
CS = 11 #GPIO17; Chip Select
TWOPLACES = Decimal(10) ** -3
RD = 1
WRT = 0
HIGH = 1
LOW = 0


address_DEVID = 0
address_THRESH_TAP = 29
address_OFSX = 30
address_OFSY = 31
address_OFSZ = 32
address_DUR = 33
address_LATENT = 34
address_WINDOW = 35
address_THRESH_ACT = 36
address_THRESH_INACT = 37
address_TIME_INACT = 38
address_ACT_INACT_CTL = 39
address_THRESH_FF = 40
address_TIME_FF = 41
address_TAP_AXES = 42
address_ACT_TAP_STATUS = 43
address_BW_RATE = 44
address_POWER_CTL = 45
address_INT_ENABLE = 46
address_INT_MAP = 47
address_INT_SOURCE = 48
address_DATA_FORMAT = 49
address_DATAX0 = 50
address_DATAX1 = 51
address_DATAY0 = 52
address_DATAY1 = 53
address_DATAZ0 = 54
address_DATAZ1 = 55
address_FIFO_CTL = 56
address_FIFO_STATUS = 57

MEASUREMENTMODE = [0, 0, 0, 0, 1, 0, 0, 0]
NULLREGISTER = [0, 0, 0, 0, 0, 0, 0, 0]
#OFFSETZ = [1, 0, 1, 1, 1, 1, 0, 1]
OFFSETZ = [0, 1, 0, 0, 0, 0, 1, 1]

GPIO.setwarnings(LOW)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(SCLK, GPIO.OUT)
GPIO.setup(SDI, GPIO.OUT)
GPIO.setup(SDO, GPIO.IN)
GPIO.setup(CS, GPIO.OUT)


def set_address(address, rw):
	address = bin(address)
	garb, address = address.split('b')
	difference = 6 - len(address)
	address = '0'*difference + address
	address = '0' + address
	address = str(rw) + address
	GPIO.output(CS, LOW)
	sleep(HALFCYCLE)
	for x in range(0, 8):
		GPIO.output(SCLK, LOW)
		GPIO.output(SDI, int(address[x]))
		sleep(HALFCYCLE)
		GPIO.output(SCLK, HIGH)
		sleep(HALFCYCLE)
	
def set_address_continuous(address, rw):
	address = bin(address)
	garb, address = address.split('b')
	difference = 6 - len(address)
	address = '0'*difference + address
	address = '1' + address
	address = str(rw) + address
	GPIO.output(CS, LOW)
	sleep(HALFCYCLE)
	for x in range(0, 8):
		GPIO.output(SCLK, LOW)
		GPIO.output(SDI, int(address[x]))
		sleep(HALFCYCLE)
		GPIO.output(SCLK, HIGH)
		sleep(HALFCYCLE)
	
def set_data(data):
	GPIO.output(CS, LOW)
	sleep(HALFCYCLE)
	for x in range(0, 8):
		GPIO.output(SCLK, LOW)
		GPIO.output(SDI, data[x])
		sleep(HALFCYCLE)
		GPIO.output(SCLK, HIGH)
		sleep(HALFCYCLE)
	GPIO.output(CS, HIGH)
	
def read_data():
	data = []
	for x in range(0, 8):
		GPIO.output(SCLK, LOW)
		sleep(HALFCYCLE)
		data.append(GPIO.input(SDO))
		GPIO.output(SCLK, HIGH)
		sleep(HALFCYCLE)
	GPIO.output(CS, HIGH)
	return data
def read_data_double():
	data = ''
	for x in range(0, 16):
		GPIO.output(SCLK, LOW)
		sleep(HALFCYCLE)
		data = data + str(GPIO.input(SDO))
		GPIO.output(SCLK, HIGH)
		sleep(HALFCYCLE)
	GPIO.output(CS, HIGH)
	data = data[14:16] + data[0:8]
	return data

def read_data_axes():
	data = ''
	for x in range(0, 48):
		GPIO.output(SCLK, LOW)
		sleep(HALFCYCLE)
		data = data + str(GPIO.input(SDO))
		GPIO.output(SCLK, HIGH)
		sleep(HALFCYCLE)
	GPIO.output(CS, HIGH)
	datax = data[14:16] + data[0:8]
	datay = data[30:32] + data[16:24]
	dataz = data[46:48] + data[32:40]
	return datax,datay,dataz
	
def two_to_binary(data):
	if data[0] == '1':
		coeff = -1
	else:
		coeff = 1
	binary = int(data, 2)
	binary = binary - 1
	binary = bin(binary)
	a,b = binary.split('b')
	a = ''
	for x in range(0, len(b)):
		if b[x] == '1':
			a = a + '0'
		else:
			a = a + '1'
	num = int(a, 2) * coeff
	return(num)

def get_axes(datapoints):
	listx = []
	listy = []
	listz = []
	for x in range(datapoints):
		set_address_continuous(address_DATAX0, RD)
		datax,datay,dataz = read_data_axes()
		listx.append(two_to_binary(datax)/256)
		listy.append(two_to_binary(datay)/256)
		listz.append((two_to_binary(dataz)-256)/256)
		
	datax = sum(listx)/datapoints
	datay = sum(listy)/datapoints
	dataz = sum(listz)/datapoints
	return datax,datay,dataz

def init_accel():
	#initialize accelerometer to measurement mode
	set_address(address_POWER_CTL, WRT)
	set_data(MEASUREMENTMODE)
	#insert offset for z-axis
	set_address(address_OFSZ, RD)
	set_data(OFFSETZ)

"""
init_accel()
while True:
	datax,datay,dataz = get_axes(10)
	datax = Decimal(datax).quantize(TWOPLACES)
	datay = Decimal(datay).quantize(TWOPLACES)
	dataz = Decimal(dataz).quantize(TWOPLACES)
	print('x-axes = %s, y-axes = %s, z-axes = %s'%(datax,datay,dataz))
"""
