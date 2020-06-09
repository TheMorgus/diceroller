from tkinter import *
import accelerometer
from decimal import *

TWOPLACES = Decimal(10) ** -3

root = Tk()

FetchingData = False

datax = StringVar()
datay = StringVar()
dataz = StringVar()
buttontext = StringVar()

buttontext.set("Fetch Data")

Label(root, text = 'X-Axis:').grid(row=0,sticky=W)
Label(root, text = 'Y-Axis:').grid(row=1,sticky=W)
Label(root, text = 'Z-Axis:').grid(row=2,sticky=W)
entry1 = Entry(root, textvariable = datax)
entry2 = Entry(root, textvariable = datay)
entry3 = Entry(root, textvariable = dataz)
entry1.grid(row=0, column=1, sticky=E)
entry2.grid(row=1, column=1, sticky=E)
entry3.grid(row=2, column=1, sticky=E)

def button_push():
	global FetchingData
	if FetchingData == False:
		FetchingData = True
		buttontext.set("Halt")
		update_accel_data()
	else:
		FetchingData = False
def update_accel_data():
	global FetchingData
	if FetchingData == True:
		x,y,z = accelerometer.get_axes(10)
		x = Decimal(x).quantize(TWOPLACES)
		y = Decimal(y).quantize(TWOPLACES)
		z = Decimal(z).quantize(TWOPLACES)
		datax.set(x)
		datay.set(y)
		dataz.set(z)
		root.after(250, update_accel_data)

button = Button(root, textvariable = buttontext, command=button_push)
button.grid(row=3,column=1,sticky=EW)

#initialize the accelerometer
accelerometer.init_accel()

root.mainloop()


