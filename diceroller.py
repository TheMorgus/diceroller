import tkinter as tk
import math
from PIL import Image, ImageTk
from threading import Thread
from queue import Queue
import time
import MPU6050 as accelerometer
from tkinter import filedialog
import imagemanipulation
import directions

TITLETEXT = "Group 5\nAutomated Dice Roller"
INTROTEXT = "Group 5 Members: Adrian Bashi, Christian Moriondo,\n"\
	"Jason Mallon, Kelly Castanon, Chris Kenneth Viray,\n"\
	"Nathan Vore, Abigail Yaldo.\n\n"\
	"Instructors: Shadi Alawneh, Steve Bazinski."
MESSAGEACCEL= "The dice roller machine must be placed on a relatively\n "\
	"flat surface. The machine will now sense its orientation and\n"\
	"if machine tilt is beyond specifications, operator must\n"\
	"realign machine using adjustable feet."
ACCELENTRY='Side profile views give an exaggerated perspective of the devices current orientation.\n'\
	'Using the adjustable feet, change orientation until the device can remain in specified\n'\
	'for over 5 seconds.\n\n'\
	'MAXIMUM AXIS ANGLE: 5 DEGREES'
DICEFILE = "dice.png"
PLACEHOLDERDICE = "rollerplaceholder.jpg"
DICEIMAGEDIM = 285
ROOTSTARTDIMX = 1000
ROOTSTARTDIMY = 700
POPUPWIDTH = 400
POPUPHEIGHT = 100
TILTDEGLIMIT = 5
CANVASDIM = 100
CANVASCENTER = CANVASDIM/2
CANVASHYP = 45
CANVASESTIMATEHEIGHT=20
CANVASESTIMATEWIDTH=200
CANVASESTIMATEOFFSET=2
ANGLEAMPLIFIER=9
MAXDEGREE = 45/180*math.pi
MAXY = CANVASHYP*math.sin(MAXDEGREE)
MAXX = CANVASHYP*math.cos(MAXDEGREE)
CORRECTION_HUEHIGH=10 #correction value from automatic background thresholding
CORRECTION_HUELOW=10 #that should more accurately adjust for dice added onto an image
CORRECTION_SATHIGH=50
CORRECTION_SATLOW=50
CORRECTION_VALUEHIGH=50
CORRECTION_VALUELOW=90

class  MenuBase(tk.Tk):
	def __init__(self, accelqueue):
		tk.Tk.__init__(self)
		monitorwidth = self.winfo_screenwidth()
		monitorheight = self.winfo_screenheight()
		self.wm_title("Automated Dice Roller")
		screen_width_center = int((monitorwidth-ROOTSTARTDIMX)/2)
		screen_height_center = int((monitorheight-ROOTSTARTDIMY)/2)
		location = str(ROOTSTARTDIMX) + 'x' + str(ROOTSTARTDIMY) + '+' \
			+ str(screen_width_center) + '+' + str(screen_height_center)
		self.geometry(location)
		self.runqueue = Queue()
		self.accelqueue = accelqueue
		self.x=0
		self.y=0
		
		
		accelerometer.bus = accelerometer.smbus.SMBus(1) 	# or bus = smbus.SMBus(0) for older version boards
		accelerometer.Device_Address = 0x68
		
		accelerometer.MPU_Init()
		
		self.openwindows=[]
		self.currentwindow = IntroWindow(self)
		#self.accelwindow = AccelWindow(self)
		#self.rollingwindow = rollingWindow(self)
		#self.menu =BaseMenu(self)
		
		self.currentwindow.openWindow()
	#def pushIntroFrame(self):
		#self.introwindow.openFrame()
		#self.currentwindow.openFrame()
	#def pushAccelFrame(self):
		#self.introwindow.closeFrame()
		#self.accelwindow.openFrame()
		#self.menu.drawMenu()
	def changeWindow(self,newwindow):
		self.currentwindow.closeWindow()
		self.currentwindow=newwindow
		print(self.currentwindow)
		self.currentwindow.openWindow()
	def addMenu(self):
		self.menu=BaseMenu(self)
		self.menu.drawMenu()
	def closeAll(self):
		for window in self.openwindows:
			window.destroy()
		self.destroy()
	def runAccel(self):
		self.runqueue.put(True)
		def thread_accel(threadname, runqueue, accelqueue):
			while(runqueue.get()):
				runqueue.put(True)
				axes = accelerometer.getAxes(10)
				accelqueue.put(axes)
				while(not accelqueue.empty()):
					time.sleep(0.030)
				time.sleep(0.030)
		self.accelthread=Thread(target=thread_accel,args=("Thread-1",self.runqueue,self.accelqueue))
		self.accelthread.start()
	def getAccelAxes(self):
		axes = self.accelqueue.get()
		self.x=axes[0]
		self.y=axes[1]
	def exit(self):
		self.destroy()
		self.destroythread()
	def loop(self):
		self.mainloop()
	def destroythread(self):
		self.runqueue.get()
		self.runqueue.put(False)
		self.accelqueue.get()
class IntroWindow(tk.Frame):
	def __init__(self, master=None):
		tk.Frame.__init__(self, master)
		self.master = master
		
		self.popupopen = 0
		
		self.title = tk.Label(self, text=TITLETEXT)
		self.title.configure(font='times 20 bold italic')
		
		self.canvas = tk.Canvas(self, width=DICEIMAGEDIM, height=DICEIMAGEDIM)
		load = Image.open(DICEFILE)
		self.render = ImageTk.PhotoImage(load)
		self.canvas.create_image(DICEIMAGEDIM/2,DICEIMAGEDIM/2,
								 image=self.render)
		
		
		self.buttonframe = tk.Frame(self)
		
		self.buttonstart = tk.Button(self.buttonframe, text = 'Start', 
									 command=self.nextWindow)
		self.buttonquit = tk.Button(self.buttonframe, text = 'Quit', 
									 command=self.quitprogram)
	def openWindow(self):
		self.pack(fill='none', expand=1)
		self.title.pack(side='top')
		self.canvas.pack(expand=1)
		self.buttonframe.pack(side='top')
		tk.Label(self, text = INTROTEXT).pack(side='top')
		self.buttonstart.pack(side='left')
		self.buttonquit.pack(side='right')
	def quitprogram(self):
		if self.popupopen == 1:
			self.root2.destroy()
		self.master.destroy()
	def closeWindow(self):
			self.destroy()
	def nextWindow(self):
		self.popupopen=1
		self.buttonstart["state"] = 'disabled'
		self.root2 = tk.Tk()
		accel = AccelPopupWindow(self,self.master, self.root2)
		accel.pack(expand=1)
		monitorwidth = self.master.winfo_screenwidth()
		monitorheight = self.master.winfo_screenheight()
		screen_width_center = int((monitorwidth-POPUPWIDTH)/2)
		screen_height_center = int((monitorheight-POPUPHEIGHT)/2)
		location = str(POPUPWIDTH) + 'x' + str(POPUPHEIGHT) + '+' \
			+ str(screen_width_center) + '+' + str(screen_height_center)
		self.root2.geometry(location)
		self.popupopen=1
		
class AccelPopupWindow(tk.Frame):
	def __init__(self, callingframe, rootmaster, framemaster=None, ):
		tk.Frame.__init__(self, framemaster)
		self.framemaster = framemaster
		self.rootmaster = rootmaster
		
		self.framemaster.protocol("WM_DELETE_WINDOW", self.closeWindow)
		self.framemaster.wm_title("Attention")
		self.callingframe = callingframe
		
		self.message = tk.Label(self, text = MESSAGEACCEL)
		self.message.pack(side='top')
		self.button = tk.Button(self, text='Continue', command=self.pushWindow)
		self.button.pack(side='top')
		
	def closeWindow(self):
		self.callingframe.popupopen = 0
		self.callingframe.buttonstart["state"]='normal'
		self.master.destroy()
	def pushWindow(self):
		self.callingframe.popupopen = 0
		accelwindow=AccelWindow(self.rootmaster)
		print(self.rootmaster)
		self.rootmaster.changeWindow(accelwindow)
		self.master.destroy()

class AccelWindow(tk.Frame):
	def __init__(self, master=None):
		tk.Frame.__init__(self, master)
		self.master = master
		
		self.upperframe = tk.Frame(self, highlightbackground='black',
			highlightthickness=1, bd=10)
		self.lowerframe = tk.Frame(self, highlightbackground='black',
			highlightthickness=1,pady=10, bd=10)
		self.buttonframe=tk.Frame(self.lowerframe, pady=10)
			
		#self.entry = tk.Entry(self.lowerframe.text=ACCELENTRY)
		
		self.labelfront = tk.Label(self.upperframe, text='FRONT')
		self.labelback = tk.Label(self.upperframe, text='BACK')
		self.labelleft = tk.Label(self.upperframe, text='LEFT')
		self.labelright = tk.Label(self.upperframe, text='RIGHT')
		
		self.x = tk.DoubleVar()
		self.y = tk.DoubleVar()
		self.x.set(0)
		self.y.set(0)
		
		self.x_scale = tk.Scale(self.upperframe, from_=TILTDEGLIMIT,to=-TILTDEGLIMIT,
			state='disabled',variable=self.x, digits = 3, resolution = 0.01)
		self.y_scale = tk.Scale(self.upperframe, from_=TILTDEGLIMIT,to=-TILTDEGLIMIT,
			state='disabled',variable=self.y, digits = 3, resolution = 0.01)
			
		self.labelbot = tk.Label(self.lowerframe, text = ACCELENTRY, relief ='sunken')
		
		self.labelxcanvas = tk.Label(self.upperframe,text="Front-Back\nVertical Plane\n(amplified)")
		self.labelycanvas = tk.Label(self.upperframe,text="Side-by-Side\n Vertical Plane\n(amplified)")
		
		self.xcanvas = tk.Canvas(self.upperframe,width=CANVASDIM,height=CANVASDIM,highlightbackground='black',
			highlightthickness=1)
		self.ycanvas = tk.Canvas(self.upperframe,width=CANVASDIM,height=CANVASDIM,highlightbackground='black',
			highlightthickness=1)
		
		self.buttonnext = tk.Button(self.buttonframe,text='Next(4)',state='disabled')
		self.buttonquit = tk.Button(self.buttonframe,text='Quit')
		self.buttonskip = tk.Button(self.buttonframe,text='Skip',
						  command=self.pushWindow)
	def openWindow(self):
		self.master.runAccel()
		self.master.getAccelAxes()
		
		self.pack(fill='none',expand=1)
		
		self.upperframe.pack(side='top',fill='none',expand=0)
		self.lowerframe.pack(side='bottom',fill='none',expand=1)
		self.buttonframe.pack(side='bottom',fill='none',expand=1)
		
		self.labelfront.grid(row=0,column=1)
		self.x_scale.grid(row=1,column=1)
		self.labelback.grid(row=2,column=1)
		
		self.labelleft.grid(row=0,column=2)
		self.y_scale.grid(row=1,column=2)
		self.labelright.grid(row=2,column=2)
		
		self.xcanvas.grid(row=1,column=0)
		self.ycanvas.grid(row=1,column=3)
		self.labelxcanvas.grid(row=3,column=0,pady=10,padx=10)
		self.labelycanvas.grid(row=3,column=3,pady=10,padx=10)
		
		self.drawFullCanvas(1)
		self.labelbot.pack()
		
		self.buttonnext.pack(side='left',fill='none',expand=1)
		self.buttonquit.pack(side='left',fill='none',expand=1)
		self.buttonskip.pack(side='left',fill='none',expand=1)
		
		self.loopAccel()
	def pushWindow(self):
		window=RollingSetupWindow(self.master)
		self.master.changeWindow(window)
		self.master.addMenu()
	def drawCanvasLimits(self):
		self.xcanvas.create_line(CANVASCENTER-MAXX,CANVASCENTER-MAXY,
			CANVASCENTER+MAXX,CANVASCENTER+MAXY, fill="#f11")
		self.xcanvas.create_line(CANVASCENTER-MAXX,CANVASCENTER+MAXY,
			CANVASCENTER+MAXX,CANVASCENTER-MAXY, fill="#f11")
		self.ycanvas.create_line(CANVASCENTER-MAXX,CANVASCENTER-MAXY,
			CANVASCENTER+MAXX,CANVASCENTER+MAXY, fill="#f11")
		self.ycanvas.create_line(CANVASCENTER-MAXX,CANVASCENTER+MAXY,
			CANVASCENTER+MAXX,CANVASCENTER-MAXY, fill="#f11")
	def clearCanvas(self):
		self.xcanvas.delete('all')
		self.ycanvas.delete('all')
	def drawFullCanvas(self, dummy):
		self.clearCanvas()
		self.drawCanvasLimits()
		
		
		
		xangle = math.asin(self.master.x)
		yangle = math.asin(self.master.y)
		
		self.x.set(xangle/math.pi*180)
		self.y.set(yangle/math.pi*180)
		
		xangle=xangle*ANGLEAMPLIFIER
		yangle=yangle*ANGLEAMPLIFIER
		
		x_vert = CANVASHYP*math.sin(xangle)
		x_horz = CANVASHYP*math.cos(xangle)
		y_vert = CANVASHYP*math.sin(yangle)
		y_horz = CANVASHYP*math.cos(yangle)
		
		
		
		self.xcanvas.create_line(CANVASCENTER-x_horz,CANVASCENTER-x_vert,
			CANVASCENTER+x_horz,CANVASCENTER+x_vert)
		self.ycanvas.create_line(CANVASCENTER-y_horz,CANVASCENTER-y_vert,
			CANVASCENTER+y_horz,CANVASCENTER+y_vert)
	def loopAccel(self):
		self.master.getAccelAxes()
		self.x_scale.set(self.master.x)
		self.y_scale.set(self.master.y)
		self.after(130, self.loopAccel)
		self.drawFullCanvas(1)
	def closeWindow(self):
		self.destroy()
class RollingSetupWindow(tk.Frame):
	def __init__(self, master):
		tk.Frame.__init__(self, master)
		self.master = master
		
		self.thresholdingframe=tk.Frame(self)
		self.dicetemplateframe=tk.Frame(self)
		self.trialsetupframe=tk.Frame(self)
		self.checklistframe=tk.Frame(self, 
									 relief='sunken',
									 borderwidth=1)
		self.movementbuttonsframe=tk.Frame(self)
		
		self.headers=[tk.Label(self,text='Background Thresholding'),
					  tk.Label(self,text='Dice Templates'),
					  tk.Label(self,text='Testing Setup'),
					  tk.Label(self,text='Checklist to Begin Testing')]
		for header in self.headers:
			header.configure(font='Impact 9 underline')
		self.thresholdingbuttons=[tk.Button(self.thresholdingframe,
											text='New Solution',
											command=lambda:self.pushWindow('bgthresholding')),
								  tk.Button(self.thresholdingframe,
											text='Load Solution',
											command=self.loadBackgroundThreshold)]
		self.dicetemplatebuttons=[tk.Button(self.dicetemplateframe,
											text='New Templates'),
								  tk.Button(self.dicetemplateframe,
											text='Load Templates',
											command=self.loadTemplates)]
		self.testingsetupbuttons=[tk.Button(self.trialsetupframe,
										   text='Trial Setup',
										   command=self.trialSetup),
								 tk.Button(self.trialsetupframe,
										   text='Dice Area Setup',
										   command=self.areaSetup)]										
		self.movementbuttons=[tk.Button(self.movementbuttonsframe,
										 text='Start',
										 state='disabled'),
							   tk.Button(self.movementbuttonsframe,
										 text='Exit')]
		self.checkboxstate=[tk.IntVar(),tk.IntVar(),tk.IntVar(),tk.IntVar()]								 
		self.checkboxes=[tk.Checkbutton(self.checklistframe,
									    state='disabled',
									    variable=self.checkboxstate[0]),
						 tk.Checkbutton(self.checklistframe,
									    state='disabled',
									    variable=self.checkboxstate[1]),
						 tk.Checkbutton(self.checklistframe,
									    state='disabled',
									    variable=self.checkboxstate[2]),
						 tk.Checkbutton(self.checklistframe,
									    state='disabled',
									    variable=self.checkboxstate[3])]
		self.checkboxlabels=[tk.Label(self.checklistframe,text='Background Thresholding'),
							 tk.Label(self.checklistframe,text='Dice Templates'),
							 tk.Label(self.checklistframe,text='Trial Setup'),
							 tk.Label(self.checklistframe,text='Area Setup')]
	def openWindow(self):
		self.pack(expand=True)
		self.headers[0].pack()
		self.thresholdingframe.pack()
		self.headers[1].pack()
		self.dicetemplateframe.pack()
		self.headers[2].pack()
		self.trialsetupframe.pack()
		self.headers[3].pack()
		self.checklistframe.pack()
		self.movementbuttonsframe.pack()
		
		for button in self.thresholdingbuttons:
			button.pack(side='left')		
		for button in self.dicetemplatebuttons:
			button.pack(side='left')
		for button in self.testingsetupbuttons:
			button.pack(side='left')
		for button in self.movementbuttons:
			button.pack(side='left')
			
		for x in range(4):
			self.checkboxes[x].grid(row=x,column=0)
			self.checkboxlabels[x].grid(row=x,column=1,sticky='w')
	def pushWindow(self,window):
		if window == "bgthresholding":
			baseimg=imagemanipulation.getCaptureDUMMY()
			baseimg = imagemanipulation.resizeImage(baseimg)
			img=baseimg.copy()
			img=imagemanipulation.cv2pil(img)
			baseimg=imagemanipulation.convertHSV(baseimg)
			window=BackgroundThresholdBaseWindow(self.master,baseimg,img)
			self.master.changeWindow(window)
	def closeWindow(self):
		self.destroy()
	def loadBackgroundThreshold(self):
		self.checkboxes[0].select()	
		self.parseClearance()
		path=filedialog.askopenfilename(title='Select File')
	def loadTemplates(self):
		self.checkboxes[1].select()	
		self.parseClearance()
		path=filedialog.askopenfilename(title='Select File')
	def trialSetup(self):
		self.checkboxes[2].select()	
		self.parseClearance()
	def areaSetup(self):
		self.checkboxes[3].select()	
		self.parseClearance()		
	def parseClearance(self):
		clearance=True
		for checkbox in self.checkboxstate:
			if checkbox.get()==0:
				clearance=False
		if(clearance):
			self.movementbuttons[0].configure(state='normal')
class BackgroundThresholdBaseWindow(tk.Frame):
	def __init__(self, master,baseimg,backgroundimg):
		tk.Frame.__init__(self, master)
		self.master = master
		
		self.baseimg=baseimg
		self.backgroundimg=backgroundimg
		self.thresholdvals=[[None,None],
							[None,None],
							[None,None]]
		
		self.upperframe=tk.Frame(self)
		self.middleframe=tk.Frame(self,
								  highlightbackground='black',
								  highlightthickness=2)
		self.lowerframe=tk.Frame(self)
		
		self.img = tk.Label(self.upperframe,
							image=self.backgroundimg)
		self.thresholdvars=[[tk.StringVar(),tk.StringVar()],
							[tk.StringVar(),tk.StringVar()],
							[tk.StringVar(),tk.StringVar()]]
		for x in range(3):
			for y in range(2):
				self.thresholdvars[x][y].set(str(self.thresholdvals[x][y]))
		self.thresholdheaders=[[tk.Label(self.middleframe,text='HIGH'),
								tk.Label(self.middleframe,text='LOW')],
							   [tk.Label(self.middleframe,text='HUE'),
								tk.Label(self.middleframe,text='SAT'),
								tk.Label(self.middleframe,text='VALUE')]]
		
		self.thresholdlabels=[[None,None],#made because you need to construct an array
							  [None,None],#already populated with values to assign
							  [None,None]]#values by indexes(which happens next)
		for x in range(3):
			for y in range(2):
				self.thresholdlabels[x][y]=tk.Label(self.middleframe,
													textvariable=self.thresholdvars[x][y],
													relief='sunken',
													width=10)
		self.directions=tk.Label(self.upperframe,
								 text=directions.DIRECTIONSBACKGROUNDCROP)
		self.newcapturebutton=tk.Button(self.lowerframe,
										text='New Capture',
										command=self.newCapture)
		self.getbasethresholdbutton=tk.Button(self.lowerframe,
										text='Get Threshold Base',
										command=self.getThresholdValues)
		self.nextbutton=tk.Button(self.lowerframe,
								  text='Calibrate Threshold\n(Next)',
								  state='disabled',
								  command=self.pushWindow)
	def openWindow(self):
		self.pack()
		self.upperframe.pack()
		self.middleframe.pack()
		self.lowerframe.pack()
		self.img.pack()
		self.directions.pack()
		for x in range(2):
			self.thresholdheaders[0][x].grid(row=0,column=x+1)
		for x in range(3):
			self.thresholdheaders[1][x].grid(row=x+1,column=0)	
		for x in range(3):
			for y in range(2):
				self.thresholdlabels[x][y].grid(row=x+1,column=y+1)					
		self.newcapturebutton.pack(side='left')
		self.getbasethresholdbutton.pack(side='left')
		self.nextbutton.pack(side='left')
	def pushWindow(self):
		baseimg = imagemanipulation.getCaptureDUMMY('2')
		baseimg = imagemanipulation.resizeImage(baseimg)
		img=baseimg.copy()
		img=imagemanipulation.cv2pil(img)
		window=ColorThresholdingWindow(self.master,
									   baseimg,
									   img,
									   img,
									   self.thresholdvals)
		self.master.changeWindow(window)
	def closeWindow(self):
		self.destroy()
	def newCapture(self):
		img=imagemanipulation.getCapture()
		img=imagemanipulation.resizeImage(img,scale=1)
		self.baseimg=imagemanipulation.convertHSV(img)
		self.backgroundimg=imagemanipulation.cv2pil(img)
		self.img.configure(image=self.backgroundimg)
	def getThresholdValues(self):
		temps=[[None,None],
			   [None,None],
			   [None,None]]
		for row in self.baseimg:
			for col in row:
				#Parse HUE high/lows
				if temps[0][0]==None:
					temps[0][0]=col[0]
				elif col[0]>temps[0][0]:
					temps[0][0]=col[0]
				if temps[0][1]==None:
					temps[0][1]=col[0]
				elif col[0]<temps[0][1]:
					temps[0][1]=col[0]
				#Parse SAT high/lows
				if temps[1][0]==None:
					temps[1][0]=col[1]
				elif col[1]>temps[1][0]:
					temps[1][0]=col[1]
				if temps[1][1]==None:
					temps[1][1]=col[1]
				elif col[1]<temps[1][1]:
					temps[1][1]=col[1]
				#Parse LIGHT high/lows
				if temps[2][0]==None:
					temps[2][0]=col[2]
				elif col[2]>temps[2][0]:
					temps[2][0]=col[2]
				if temps[2][1]==None:
					temps[2][1]=col[2]
				elif col[2]<temps[2][1]:
					temps[2][1]=col[2]
		for x in range(3):
			for y in range(2):
				self.thresholdvals[x][y]=temps[x][y]
		for x in range(3):
			for y in range(2):
				self.thresholdvars[x][y].set(str(self.thresholdvals[x][y])) #update labels with values	
		self.nextbutton.configure(state='normal') #enables button for next window
#Using the previous thresholding values gathered from the backgroundCropWindow
#as a base, the user is able to further refine the background filtering with
#the dice to be tested on the rolling space. This feature is mandatory to ensure
#a proper dice square is isolated for proper dice recognition algorimth operation
class ColorThresholdingWindow(tk.Frame):
	def __init__(self, master,baseimg,baseimgpil,maskimg,thresholdvals):
		tk.Frame.__init__(self, master)
		self.master = master
		
		self.baseimg=baseimg
		self.baseimgpil=baseimgpil
		maskimg=imagemanipulation.calibrateMask(self.baseimg)
		self.maskimg=imagemanipulation.cv2pil(maskimg)
		thresholdvals[0][0]=thresholdvals[0][0]+CORRECTION_HUEHIGH
		thresholdvals[0][1]=thresholdvals[0][1]-CORRECTION_HUELOW
		thresholdvals[1][0]=thresholdvals[1][0]+CORRECTION_SATHIGH
		thresholdvals[1][1]=thresholdvals[1][1]-CORRECTION_SATLOW
		thresholdvals[2][0]=thresholdvals[2][0]+CORRECTION_VALUEHIGH
		thresholdvals[2][1]=thresholdvals[2][1]-CORRECTION_VALUELOW
		for x in range(3):#enforce color value limits
			for y in range(2):
				if y==0 and thresholdvals[x][y]>255:
					thresholdvals[x][y]=255
				elif thresholdvals[x][y]<0:
					thresholdvals[x][y]=0
		self.thresholdvals= [thresholdvals[0][0],
							 thresholdvals[0][1],
							 thresholdvals[1][0],
							 thresholdvals[1][1],
							 thresholdvals[2][0],
							 thresholdvals[2][1]]
		
		self.upperFrame=tk.Frame(self)
		self.midFrame=tk.Frame(self)
		self.lowerFrame=tk.Frame(self)
		self.upperFrames=[tk.Frame(self.upperFrame),
						  tk.Frame(self.upperFrame),
						  tk.Frame(self.upperFrame)]

		self.headers=[]

		self.headers.append(tk.Label(self.upperFrames[0],
							text='HUE'))
		self.headers.append(tk.Label(self.upperFrames[1],
							text='SATURATION'))
		self.headers.append(tk.Label(self.upperFrames[2],
							text='VALUE'))
		huelabels=[]
		satlabels=[]
		lightlabels=[]
		huelabels.append(tk.Label(self.upperFrames[0],
								  text='HIGH'))
		huelabels.append(tk.Label(self.upperFrames[0],
								  text='LOW'))
		satlabels.append(tk.Label(self.upperFrames[1],
								  text='HIGH'))
		satlabels.append(tk.Label(self.upperFrames[1],
								  text='LOW'))
		lightlabels.append(tk.Label(self.upperFrames[2],
								  text='HIGH'))
		lightlabels.append(tk.Label(self.upperFrames[2],
								  text='LOW'))
		self.labels=[]
		self.labels.append(huelabels)
		self.labels.append(huelabels)
		self.labels.append(huelabels)
		
		self.trackbars=[]
		self.trackbars.append(tk.Scale(self.upperFrames[0],
							           from_=0,
							           to=255,
							           orient='horizontal',
							           command=self.getNewMask))
		self.trackbars.append(tk.Scale(self.upperFrames[0],
									   from_=0,
									   to=255,
									   orient='horizontal',
									   command=self.getNewMask))
		self.trackbars.append(tk.Scale(self.upperFrames[1],
							           from_=0,
							           to=255,
							           orient='horizontal',
							           command=self.getNewMask))
		self.trackbars.append(tk.Scale(self.upperFrames[1],
							           from_=0,
							           to=255,
							           orient='horizontal',
							           command=self.getNewMask))
		self.trackbars.append(tk.Scale(self.upperFrames[2],
									   from_=0,
									   to=255,
									   orient='horizontal',
									   command=self.getNewMask))
		self.trackbars.append(tk.Scale(self.upperFrames[2],
									   from_=0,
									   to=255,
									   orient='horizontal',
									   command=self.getNewMask))
		self.trackbars[0].set(thresholdvals[0][0])
		self.trackbars[1].set(thresholdvals[0][1])
		self.trackbars[2].set(thresholdvals[1][0])
		self.trackbars[3].set(thresholdvals[1][1])
		self.trackbars[4].set(thresholdvals[2][0])
		self.trackbars[5].set(thresholdvals[2][1])
		self.directiontext=tk.Label(self.lowerFrame,
									text=directions.DIRECTIONSCOLORCAILBRATION)

		self.img=[]
		self.img.append(tk.Label(self.midFrame,
								 image=self.baseimgpil))
		self.img.append(tk.Label(self.midFrame,
								 image=self.maskimg))
		
	def openWindow(self):
		self.pack()
		self.upperFrame.pack()
		self.midFrame.pack()
		self.lowerFrame.pack()
		self.upperFrames[0].grid(row=0,column=0)
		self.upperFrames[1].grid(row=0,column=1)
		self.upperFrames[2].grid(row=0,column=2)
		self.headers[0].grid(row=0,column=1)
		self.headers[1].grid(row=0,column=1)
		self.headers[2].grid(row=0,column=1)
		self.labels[0][0].grid(row=1,column=0)
		self.labels[0][1].grid(row=2,column=0)
		self.labels[1][0].grid(row=1,column=0)
		self.labels[1][1].grid(row=2,column=0)
		self.labels[2][0].grid(row=1,column=0)
		self.labels[2][1].grid(row=2,column=0)
		self.trackbars[0].grid(row=1,column=1)
		self.trackbars[1].grid(row=2,column=1)
		self.trackbars[2].grid(row=1,column=1)
		self.trackbars[3].grid(row=2,column=1)
		self.trackbars[4].grid(row=1,column=1)
		self.trackbars[5].grid(row=2,column=1)
		self.img[0].pack(side='left')
		self.img[1].pack(side='right')
		
		self.retrievebutton=tk.Button(self.lowerFrame,
									  text='New Capture')
		self.donebutton=tk.Button(self.lowerFrame,
									  text='Use Selected Values')
		
		self.directiontext.pack(side='top')
		self.retrievebutton.pack(side='left')
		self.donebutton.pack(side='right')
	def closeWindow():
		self.destroy()
	#Gets a new mask image based on threshold values set on trackbars.
	#Called every time the trackbar is updated.	
	def getNewMask(self,_):
		for x in range(6):
			self.thresholdvals[x]=self.trackbars[x].get()
		self.maskimg=imagemanipulation.calibrateMask(self.baseimg,
											     self.thresholdvals[0],
											     self.thresholdvals[1],
											     self.thresholdvals[2],
											     self.thresholdvals[3],
											     self.thresholdvals[4],
											     self.thresholdvals[5])
		self.maskimg=imagemanipulation.cv2pil(self.maskimg)
		self.img[1].configure(image=self.maskimg)
		self.img[1].image=self.maskimg		
class RollingWindow(tk.Frame):
	def __init__(self, master=None):
		tk.Frame.__init__(self, master)
		self.master = master
		
		self.upperframe = tk.Frame(self.master)
		self.lowerframe = tk.Frame(self.master,highlightbackground='black',
			highlightthickness=1, bd=10)
		
		self.upperleftframe = tk.Frame(self.upperframe,highlightbackground='black',
			highlightthickness=1, bd=10)
		self.uppermiddleframe = tk.Frame(self.upperframe)
		self.upperrightframe = tk.Frame(self.upperframe,highlightbackground='black',
			highlightthickness=1, bd=10)
		self.lowerupperframe=tk.Frame(self.lowerframe)
		self.lowerlowerframe=tk.Frame(self.lowerframe)
		self.timeremainingframe=tk.Frame(self.lowerlowerframe)
		self.buttonframe=tk.Frame(self.lowerframe)
		
		
		self.timeSlider=tk.Canvas(self.timeremainingframe,height=CANVASESTIMATEHEIGHT,
			width=CANVASESTIMATEWIDTH,highlightbackground='black',highlightthickness=1)
		
		self.labelDiceImage = tk.Label(self.uppermiddleframe, text='DICE CAPTURE')
		self.labelListBox = tk.Label(self.upperrightframe, text='Last 10 Rolls')
		self.labelDiceRolled = tk.Label(self.upperleftframe, text='DICE ROLLED: [6,3]')
		self.labelRollNumber = tk.Label(self.upperleftframe, text='CURRENT ROLL #: 50')
		self.labelTotalRolls = tk.Label(self.upperleftframe, text='TOTAL ROLLS:1000')
		self.labelTimeLeft = tk.Label(self.lowerupperframe, text='ESTIMATED TIME REMAINING')
		self.labelTimeClock = tk.Label(self.timeremainingframe, text='58min 23sec')
		
		self.diceList = tk.Listbox(self.upperrightframe, selectmode='single',width=8)
		self.img = ImageTk.PhotoImage(Image.open(PLACEHOLDERDICE))
		self.panel = tk.Label(self.uppermiddleframe, image=self.img)
		
		self.buttonStart = tk.Button(self.buttonframe,text='Start',state='disabled')
		self.buttonPause = tk.Button(self.buttonframe,text='Pause')
		self.buttonStop = tk.Button(self.buttonframe,text='Stop')
		self.buttonQuit = tk.Button(self.buttonframe,text='Quit',command=self.master.closeAll)
	def openWindow(self):
		self.upperframe.pack()
		self.lowerframe.pack()
		
		self.upperleftframe.pack(side='left')
		self.uppermiddleframe.pack(side='left')
		self.upperrightframe.pack(side='left')
		
		self.lowerupperframe.pack(side='top')
		self.lowerlowerframe.pack(side='top')
		self.timeremainingframe.pack(side='top')
		self.buttonframe.pack(side='top')
		
		self.labelDiceImage.pack(side='top')
		self.labelListBox.pack(side='top')
		self.labelDiceRolled.pack(side='top',pady=15)
		self.labelRollNumber.pack(side='top',pady=15)
		self.labelTotalRolls.pack(side='top',pady=15)
		self.labelTimeLeft.pack(side='top')
		self.labelTimeClock.pack(side='right')
		
		self.diceList.pack(side='top')
		self.panel.pack(side='top')
		
		self.timeSlider.pack(side='left')
		
		
		self.diceList.insert(0,'  1:[1,3]')
		self.diceList.insert(1,'  2:[5,3]')
		self.diceList.insert(2,'  3:[1,4]')
		self.diceList.insert(3,'  4:[6,6]')
		self.diceList.insert(4,'  5:[2,6]')
		self.diceList.insert(5,'  6:[1,2]')
		self.diceList.insert(6,'  7:[6,2]')
		self.diceList.insert(7,'  8:[5,5]')
		self.diceList.insert(8,'  9:[2,5]')
		self.diceList.insert(9,' 10:[2,1]')
		
		self.buttonStart.pack(side='left')
		self.buttonPause.pack(side='left')
		self.buttonStop.pack(side='left')
		self.buttonQuit.pack(side='left')
		
		self.timeSlider.create_rectangle(0,CANVASESTIMATEOFFSET,
			CANVASESTIMATEWIDTH/3,CANVASESTIMATEHEIGHT-CANVASESTIMATEOFFSET+1,fill='red')			
class BaseMenu(tk.Menu):
	def __init__(self, master=None):
		tk.Menu.__init__(self, master)
		self.master=master
		self.filemenu = []
	def drawMenu(self):
		self.filemenu.append(tk.Menu(self,tearoff=0))
		self.filemenu.append(tk.Menu(self,tearoff=0))
		self.add_cascade(label='File',menu=self.filemenu[0])
		self.add_cascade(label='About',menu=self.filemenu[1])
		self.filemenu[0].add_command(label="Save", accelerator='(F5)',
			command=self.master.exit)
		self.filemenu[0].add_command(label="Load", accelerator='(F6)',
			command=self.master.exit)
		self.filemenu[0].add_command(label="Exit", accelerator='(Crtl + X)',
			command=self.master.exit)
		self.master.config(menu=self)
	



accelqueue = Queue()
#mainthread=Thread(target=thread_main,args=("Thread-1",accelqueue))
#mainthread.start()
menu = MenuBase(accelqueue)
menu.loop()
