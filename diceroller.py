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
ROOTSTARTDIMY = 600
SCREENPOSITION_YOFFSET=-65
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
DICETEMPLATESPACE=3
DICECROPS=(250,250,600,600)
TEMPLATEWINDOWSCALE=0.4 #Resize scale for images in dice template window
BASEIMAGESCALE=1

class  MenuBase(tk.Tk):
	def __init__(self, accelqueue):
		tk.Tk.__init__(self)
		monitorwidth = self.winfo_screenwidth()
		monitorheight = self.winfo_screenheight()
		self.wm_title("Automated Dice Roller")
		screen_width_center = int((monitorwidth-ROOTSTARTDIMX)/2)
		screen_height_center = int((monitorheight-ROOTSTARTDIMY)/2)
		location = str(ROOTSTARTDIMX) + 'x' + str(ROOTSTARTDIMY) + '+' \
			+ str(screen_width_center) + '+' + str(screen_height_center+SCREENPOSITION_YOFFSET)
		self.geometry(location)
		self.runqueue = Queue()
		self.accelqueue = accelqueue
		self.x=0
		self.y=0
		
		
		accelerometer.bus = accelerometer.smbus.SMBus(1) 	# or bus = smbus.SMBus(0) for older version boards
		accelerometer.Device_Address = 0x68
		
		accelerometer.MPU_Init()
		
		self.setupdict={
			"thresholdvals":None,
			"dicetemplates":None,
			"trialsetup":None,
			"areasetup":None
			}
		#self.openwindows=[]
		self.currentwindow = IntroWindow(self)
		self.currentwindow.openWindow()
	def changeWindow(self,newwindow):
		self.currentwindow.closeWindow()
		print(self.setupdict)
		self.currentwindow=newwindow
		self.currentwindow.openWindow()
	def addMenu(self):
		self.menu=BaseMenu(self)
		self.menu.drawMenu()
	def closeAll(self):
		for window in self.openwindows:
			window.destroy()
		self.destroy()
	def close(self):
		self.currentwindow.destroy()
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
		self.runqueue.put(False)
		self.runqueue.get()
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
											command=lambda:self.pushWindow('bgthresholding'),
											state='disabled'),
								  tk.Button(self.thresholdingframe,
											text='Load Solution',
											command=self.loadBackgroundThreshold,
											state='disabled')]
		self.dicetemplatebuttons=[tk.Button(self.dicetemplateframe,
											text='New Templates',
											command=lambda:self.pushWindow('dicetemplates'),
											state='disabled'),
								  tk.Button(self.dicetemplateframe,
											text='Load Templates',
											command=self.loadTemplates,
											state='disabled')]
		self.testingsetupbuttons=[tk.Button(self.trialsetupframe,
										   text='Trial Setup',
										   state='disabled',
										   command=lambda:self.pushWindow('trialsetup')),
								 tk.Button(self.trialsetupframe,
										   text='Dice Area Setup',
										   command=lambda:self.pushWindow('areasetup'))]										
		self.movementbuttons=[tk.Button(self.movementbuttonsframe,
										 text='Start',
										 state='disabled'),
							   tk.Button(self.movementbuttonsframe,
										 text='Exit',
										 command=self.exit)]
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
			
		self.auditCheckboxesButtons() #check for complete pre-testing procedures
	def pushWindow(self,window):
		if window=="bgthresholding":
			baseimg=imagemanipulation.getCaptureDUMMY()
			baseimg=imagemanipulation.resizeImage(baseimg)
			img=baseimg.copy()
			img=imagemanipulation.cv2pil(img)
			baseimg=imagemanipulation.convertHSV(baseimg)
			window=BackgroundThresholdBaseWindow(self.master,baseimg,img)
			self.master.changeWindow(window)
		if window=='dicetemplates':
			baseimg=imagemanipulation.getCaptureDUMMY('4')
			baseimg=imagemanipulation.resizeImage(baseimg,TEMPLATEWINDOWSCALE)
			img=baseimg.copy()
			img=imagemanipulation.cv2pil(img)
			window=TemplateCreationWindow(self.master,baseimg,img)
			self.master.changeWindow(window)
		if window=='areasetup':
			baseimg=imagemanipulation.getCaptureDUMMY('4')
			baseimg=imagemanipulation.resizeImage(baseimg,TEMPLATEWINDOWSCALE)
			img=baseimg.copy()
			img=imagemanipulation.cv2pil(img)
			window=AreaSetupWindow(self.master,baseimg,img)
			self.master.changeWindow(window)
		if window=='trialsetup':
			window=TrialSetupWindow(self.master)
			self.master.changeWindow(window)
	def closeWindow(self):
		self.destroy()
	def exit(self):
		self.master.close()
	def auditCheckboxesButtons(self):
		if self.master.setupdict["thresholdvals"]!=None:
			self.checkboxes[0].select()
		if self.master.setupdict["dicetemplates"]!=None:
			self.checkboxes[1].select()
		if self.master.setupdict["trialsetup"]!=None:
			self.checkboxes[2].select()
		if self.master.setupdict["areasetup"]!=None:
			self.checkboxes[3].select()
			self.enableButtons()
	def enableButtons(self):
		for button in self.thresholdingbuttons:
			button.configure(state='normal')
		for button in self.dicetemplatebuttons:
			button.configure(state='normal')
		for button in self.testingsetupbuttons:
			button.configure(state='normal')
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
		mask=imagemanipulation.calibrateMask(baseimg)
		mask=imagemanipulation.cv2pil(mask)
		window=ColorThresholdingWindow(self.master,
									   baseimg,
									   img,
									   mask,
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
		self.maskimg=maskimg
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
									  text='New Capture',
									  command=self.newCapture)
		self.donebutton=tk.Button(self.lowerFrame,
									  text='Use Selected Values',
									  command=self.pushWindow)
		
		self.directiontext.pack(side='top')
		self.retrievebutton.pack(side='left')
		self.donebutton.pack(side='right')
	def closeWindow(self):
		self.destroy()
	#Gets a new mask image based on threshold values set on trackbars.
	#Called every time the trackbar is updated.
	def pushWindow(self):
		window=RollingSetupWindow(self.master)
		self.master.setupdict["thresholdvals"]=self.thresholdvals
		self.master.changeWindow(window)
	def newCapture(self):
		baseimg=imagemanipulation.getCaptureDUMMY('3')
		self.baseimg=imagemanipulation.resizeImage(baseimg)
		self.baseimgpil=imagemanipulation.cv2pil(self.baseimg)
		self.img[0].configure(image=self.baseimgpil)
		self.maskimg=imagemanipulation.calibrateMask(self.baseimg,
											     self.thresholdvals[0],
											     self.thresholdvals[1],
											     self.thresholdvals[2],
											     self.thresholdvals[3],
											     self.thresholdvals[4],
											     self.thresholdvals[5])
		self.maskimg=imagemanipulation.cv2pil(self.maskimg)
		self.img[1].configure(image=self.maskimg)							    
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
class TemplateCreationWindow(tk.Frame):
	def __init__(self,master,baseimg,img):
		tk.Frame.__init__(self,master)
		self.master = master
		self.img=img
		self.baseimg=baseimg
		self.diceimgs=[]
		self.imagesize=imagemanipulation.imageSize(baseimg)
		self.points=[(None,None),(None,None)]
		self.tempbefore=None
		self.tempafter=None
		
		self.sizeadjustment=0
		self.angleadjustment=0
		self.xadjustment=0
		self.yadjustment=0
		
		self.upperframe=tk.Frame(self)
		self.upperframes=[tk.Frame(self.upperframe),#Holds the upper left variable frame, 
						  tk.Frame(self.upperframe)]#and the upper right dice template frame
		self.lowerframe=tk.Frame(self)	#Hold frames for button and directions
		self.lowerframes=[tk.Frame(self.lowerframe),
						  tk.Frame(self.lowerframe)]
		self.canvasframe=tk.Frame(self.upperframes[0]) #One of two variable frames, holds image of dice to be cropped to make template
		self.templateadjustmentframe=tk.Frame(self.upperframes[0])#second variable frame, where user refines dice template to complete version
		
		
		self.templateadjustmentinnerframes=[tk.Frame(self.templateadjustmentframe),
											tk.Frame(self.templateadjustmentframe,
													 padx=5,
													 pady=5,
													 background='grey',
													 relief='sunken',
													 borderwidth=1)]
		self.templateadjustmentimgcontainer=tk.Frame(self.templateadjustmentinnerframes[0],
												   height=self.imagesize[0],
												   width=self.imagesize[1],
												   background='black')
		self.templateadjustmentimgcontainer.pack_propagate(0)
		self.templateadjustmentbuttonframes=[tk.Frame(self.templateadjustmentinnerframes[1],
													  relief='sunken',
													  borderwidth=1),
											 tk.Frame(self.templateadjustmentinnerframes[1],
													  relief='sunken',
													  borderwidth=1),
											 tk.Frame(self.templateadjustmentinnerframes[1],
													  relief='sunken',
													  borderwidth=1),
											 tk.Frame(self.templateadjustmentinnerframes[1],
													  relief='sunken',
													  borderwidth=1)]
		
		self.canvas=tk.Canvas(self.canvasframe,
							  height=self.imagesize[0],
							  width=self.imagesize[1])
		self.canvasimg= self.canvas.create_image(0,
												 0,
												 anchor='nw',
												 image=self.img)
		self.temptemplateimgs=[tk.Label(self.templateadjustmentimgcontainer),
							   tk.Label(self.templateadjustmentimgcontainer)]
		self.turnsbuttons=[tk.Button(self.templateadjustmentbuttonframes[0],
								     text='Rotate\nLeft',
								     command=lambda:self.rotateTemplate('left')),
						   tk.Button(self.templateadjustmentbuttonframes[0],
								     text='Rotate\nRight',
								     command=lambda:self.rotateTemplate('right'))]
		self.resizebuttons=[tk.Button(self.templateadjustmentbuttonframes[2],
									  text='Increase(+)\nSize',
									  command=lambda:self.resizeTemplate('increase')),
						    tk.Button(self.templateadjustmentbuttonframes[2],
									  text='Decrease(-)\nSize',
									  command=lambda:self.resizeTemplate('decrease'))]
		self.movebuttons=[tk.Button(self.templateadjustmentbuttonframes[1],
								    text='^',
								    command=lambda:self.moveTemplate('yup')),
						  tk.Button(self.templateadjustmentbuttonframes[1],
								    text='<',
								    command=lambda:self.moveTemplate('xdown')),
						  tk.Button(self.templateadjustmentbuttonframes[1],
								    text='>',
								    command=lambda:self.moveTemplate('xup')),
						  tk.Button(self.templateadjustmentbuttonframes[1],
								    text='v',
								    command=lambda:self.moveTemplate('ydown'))]
		self.diceimglabels=[]
		for x in range(6): #Creates 6x4 matrix of labels for dice imgs
			temp=[]
			for x in range (4):
				temp.append(tk.Label(self.upperframes[1]))
			self.diceimglabels.append(temp)
		self.dicevalueheaders=[]
		for x in range(6):
			text="Value:"+str(x+1)
			temp=tk.Label(self.upperframes[1],
						  text=text,
						  width=DICETEMPLATESPACE+4,
						  height=DICETEMPLATESPACE,
						  relief='ridge')
			self.dicevalueheaders.append(temp)
		self.templateangleheaders=[]
		for x in range(4):
			degree_sign=u'\N{DEGREE SIGN}'
			text=str(x*90)+degree_sign
			temp=tk.Label(self.upperframes[1],
						  text=text,
						  width=DICETEMPLATESPACE+3,
						  height=DICETEMPLATESPACE,
						  relief='ridge')
			self.templateangleheaders.append(temp)
		self.directionstext=tk.StringVar()
		self.directionstext.set(directions.DIRECTIONSTEMPLATECROP)
		self.directionsbox=tk.Label(self.lowerframes[0],
									textvariable=self.directionstext,
									justify='left')
		self.wrapupbuttons=[tk.Button(self.templateadjustmentbuttonframes[3],
									 text='Accept',
									 command=self.addTemplate),
							tk.Button(self.templateadjustmentbuttonframes[3],
									 text='Reset',
									 command=self.resetTemplate)]		 
		self.lowerbuttons=[tk.Button(self.lowerframes[1],
									 text='New Capture',
									 command=self.newCapture),
						   tk.Button(self.lowerframes[1],
									 text='Crop Next\nTemplate',
									 command=self.enableCropping),
						   tk.Button(self.lowerframes[1],
									 text='Undo Last\nTemplate',
									 command=self.undoTemplate,
									 state='disabled'),
						   tk.Button(self.lowerframes[1],
									 text='Finalize\nTemplates',
									 command=self.finish,
									 state='disabled')]
	def openWindow(self):
		self.pack()
		self.upperframe.pack()
		for frame in self.upperframes:
			frame.pack(side='left')
		self.canvasframe.pack()
		self.canvas.pack()
		self.templateadjustmentimgcontainer.pack()
		for frame in self.templateadjustmentinnerframes:
			frame.pack(side='top')
		for frame in self.templateadjustmentbuttonframes:
			frame.pack(side='left',anchor='s')
		for button in self.turnsbuttons:
			button.pack(side='left')
		for button in self.resizebuttons:
			button.pack(side='left')
		self.movebuttons[0].pack(side='top')
		self.movebuttons[1].pack(side='left')
		self.movebuttons[2].pack(side='right')
		self.movebuttons[3].pack(side='bottom')
		for button in self.wrapupbuttons:
			button.pack(side='top')
		for label in self.temptemplateimgs:
			label.pack(side='left',expand=True)
		self.lowerframe.pack()
		for frame in self.lowerframes:
			frame.pack(pady=2)
		self.directionsbox.pack()
		for x in range(6):
			self.dicevalueheaders[x].grid(row=x+1,column=0,
										  padx=5,pady=1)
		for x in range(4):
			self.templateangleheaders[x].grid(row=0,column=x+1,
										  padx=5,pady=1)
		for x in range(6):
			for y in range(4):
				self.diceimglabels[x][y].grid(row=x+1,column=y+1)
		for button in self.lowerbuttons:
			button.pack(side='left')
	def closeWindow(self):
		self.destroy()
	def newCapture(self):
		self.baseimg=imagemanipulation.getCapture()
		#self.baseimg=imagemanipulation.cropImage(self.baseimg,
		#										 DICECROPS[0],
		#										 DICECROPS[1],
		#										 DICECROPS[2],
		#										 DICECROPS[3])
		self.baseimg=imagemanipulation.resizeByDim(self.baseimg,self.imagesize)
		self.img=imagemanipulation.cv2pil(self.baseimg)
		self.canvasimg= self.canvas.create_image(0,
												 0,
												 anchor='nw',
												 image=self.img)
		#self.baseimg=
	def enableCropping(self):
		self.canvas.bind("<Button-1>",self.callback)
		self.directionstext.set(directions.DIRECTIONSTEMPLATECROP2)
		for button in self.lowerbuttons:
			button.configure(state='disabled')
	def addTemplate(self):
		finishedimgs=[]
		self.lowerbuttons[2].configure(state='normal')
		for x in range(4):
			img=imagemanipulation.adjustImage(self.tempopencv,
										angle=self.angleadjustment+x*90,
										sizechange=self.sizeadjustment,
										xchange=self.xadjustment,
										ychange=self.yadjustment)
			finishedimgs.append(imagemanipulation.cv2pil(img))
		self.diceimgs.append(finishedimgs)
		for x in range(len(self.diceimgs)):
			for y in range(4):
				self.diceimglabels[x][y].configure(image=self.diceimgs[x][y])	
		self.frameSwitch('cropping')
		self.resetAdjustments()
		for x in range(3):
			self.lowerbuttons[x].configure(state='normal')
		if len(self.diceimgs)==6:
			self.lowerbuttons[3].configure(state='normal')
		self.directionstext.set(directions.DIRECTIONSTEMPLATECROP)
	def undoTemplate(self):
		if len(self.diceimgs)>0:
			lastindex=len(self.diceimgs)
			for x in range(4):
				self.diceimglabels[lastindex-1][x].configure(image='')
			self.diceimgs.pop()
			if len(self.diceimgs)>0:
				for x in range(len(self.diceimgs)):
					for y in range(4):
						self.diceimglabels[x][y].configure(image=self.diceimgs[x][y])
		if len(self.diceimgs)==0:
			self.lowerbuttons[2].configure(state='disabled')
		self.lowerbuttons[3].configure(state='disabled')
	def resetTemplate(self):
		self.frameSwitch('cropping')
		self.resetAdjustments()
		for button in self.lowerbuttons:
			button.configure(state='normal')
		self.directionstext.set(directions.DIRECTIONSTEMPLATECROP)
	def resetAdjustments(self):
		self.sizeadjustment=0 #Reset adjustments for next template
		self.angleadjustment=0
		self.xadjustment=0
		self.yadjustment=0
	def frameSwitch(self, frame):
		if frame=='template':
			self.canvasframe.forget()
			self.lowerframe.forget()
			self.templateadjustmentframe.pack(fill='none',expand=False)
			self.lowerframe.pack()
		if frame=='cropping':
			self.templateadjustmentframe.forget()
			self.lowerframe.forget()
			self.canvasframe.pack()
			self.lowerframe.pack()
	def rotateTemplate(self,direction):
		if direction=='left':
			self.angleadjustment=self.angleadjustment+1
		elif direction=='right':
			self.angleadjustment=self.angleadjustment-1
		self.updateTemporaryTemplate()
	def resizeTemplate(self,change):
		if (change=='increase') and (self.sizeadjustment!=0):
			self.sizeadjustment=self.sizeadjustment+2
		elif change=='decrease':
			self.sizeadjustment=self.sizeadjustment-2
			
		self.updateTemporaryTemplate()
	def moveTemplate(self,change):
		
		if change=='xup' and self.xadjustment<abs(self.sizeadjustment):
			self.xadjustment=self.xadjustment+2
		if change=='xdown' and self.xadjustment!=0:
			self.xadjustment=self.xadjustment-2
		if change=='yup' and self.yadjustment!=0:
			self.yadjustment=self.yadjustment-2
		if change=='ydown' and self.yadjustment<abs(self.sizeadjustment):
			self.yadjustment=self.yadjustment+2
		self.updateTemporaryTemplate()
	def updateTemporaryTemplate(self):
		img=imagemanipulation.adjustImage(self.tempopencv,
									 angle=self.angleadjustment,
									 sizechange=self.sizeadjustment,
									 xchange=self.xadjustment,
									 ychange=self.yadjustment)
		self.updateBaseTemplate(img)
		self.tempafter=imagemanipulation.cv2pil(img)
		self.temptemplateimgs[1].configure(image=self.tempafter)
	def updateBaseTemplate(self,img):
		width,height=imagemanipulation.imageSize(img)
		width=width
		height=height
		rect=imagemanipulation.findRectContours(width,
												height,
												startx=self.xadjustment,
												starty=self.yadjustment)
		img=imagemanipulation.drawRect(self.tempopencv,
									   rect,
									   angle=self.angleadjustment)
		self.tempbefore=imagemanipulation.cv2pil(img)
		self.temptemplateimgs[0].configure(image=self.tempbefore)
	def finish(self):
		window=RollingSetupWindow(self.master)
		self.master.setupdict["dicetemplates"]=self.diceimgs
		self.master.changeWindow(window)	
	def callback(self,event):
		temppoint=(event.x,event.y)
		if self.points[0][0]==None:
			self.points[0]=temppoint
		else:
			self.points[1]=temppoint
			width = abs(self.points[1][0]-self.points[0][0]) #Width = Height so template is a complete square
			startx=self.points[0][0]					   #This allows 90* rotations with zero image loss
			starty=self.points[0][1]
			if startx>self.points[1][0]:
				startx=self.points[1][0]
			if starty>self.points[1][1]:
				starty=self.points[1][1]
			self.points=[(None,None),(None,None)]
			img=imagemanipulation.cropImage(self.baseimg,startx,starty,width,width)
			self.tempopencv=img
			self.tempbefore=(imagemanipulation.cv2pil(img))
			self.tempafter=self.tempbefore
			for label in self.temptemplateimgs:
				label.configure(image=self.tempbefore)
			self.directionstext.set(directions.DIRECTIONSTEMPLATECROP3)
			self.frameSwitch(frame='template')
			self.canvas.unbind("<Button-1>")
class TrialSetupWindow(tk.Frame):
	def __init__(self,master):
		tk.Frame.__init__(self,master)
		self.master = master
		
		self.checkvars=[tk.IntVar(),
						tk.IntVar(),
						tk.IntVar(),
						tk.IntVar()]
		self.entryvars=[tk.StringVar(),
						tk.StringVar(),
						tk.StringVar()]	
		self.trialsframe=tk.Frame(self)
		self.trialsinnerframes=[tk.Frame(self.trialsframe,
										 relief='sunken',
										 borderwidth=2),
								tk.Frame(self.trialsframe,
										 relief='sunken',
										 borderwidth=2)]
		self.diceframe=tk.Frame(self,
								relief='sunken',
								borderwidth=2)
		self.summaryframe=tk.Frame(self,
								   relief='groove',
								   borderwidth=2)
		self.summarytext=tk.Text(self.summaryframe,
								 height=5,
								 width=30,
								 state='disabled')
		self.basebuttonframe=tk.Frame(self)
		self.confidenceframe=tk.Frame(self.trialsinnerframes[0])
		self.button=tk.Button(self.basebuttonframe,
							  text='Finalize',
							  state='disabled',
							  command=self.finalize)
		self.trialentryframe=tk.Frame(self.trialsinnerframes[1])
		self.trialheaders=[tk.Label(self.trialsinnerframes[0],
								   text='Choose Trial Type:'),
						  tk.Label(self.trialsinnerframes[1],
								   text='Choose Trial Iterations:')]
		self.confidencelabel=tk.Label(self.confidenceframe,
									  text='Desired\nConfidence:')
		self.confidencepercent=tk.Label(self.confidenceframe,
									  text='%')							  
		self.confidenceentry=tk.Entry(self.confidenceframe,
									  width=5,
									  state='disabled',
									  command=self.auditSetup(),
									  textvariable=self.entryvars[0])
		self.checkbuttons=[tk.Checkbutton(self.trialsinnerframes[0],
										  text='Stop Trial if Confidence % Reached',
										  variable=self.checkvars[0],
										  command=lambda:self.trialTypeChange(0)),
						   tk.Checkbutton(self.trialsinnerframes[0],
										  text='Run All Trials',
										  justify='left',
										  variable=self.checkvars[1],
										  command=lambda:self.trialTypeChange(1)),
		                   tk.Checkbutton(self.trialsinnerframes[1],
										  text='Run Suggested Trials - 1000',
										  variable=self.checkvars[2],
										  command=lambda:self.trialIterationChange(0)),
						   tk.Checkbutton(self.trialsinnerframes[1],
										  text='Select Trial Iterations',
										  justify='left',
										  variable=self.checkvars[3],
										  command=lambda:self.trialIterationChange(1))]
		self.trialslabel=tk.Label(self.trialentryframe,
								  text='Desired\nTrial Iterations:')
		self.trialsentry=tk.Entry(self.trialentryframe,
								 width=5,
								 state='disabled',
								 command=self.auditSetup(),
								 textvariable=self.entryvars[1])		
		self.diceheader=tk.Label(self.diceframe,
								 text='Enter Number of Dice (1-8)')
		self.diceentry=tk.Entry(self.diceframe,
								width=5,
								command=self.auditSetup(),
								textvariable=self.entryvars[2])
		self.summaryheader=tk.Label(self.summaryframe,
									text='Setup Summary')
		self.textvar=tk.StringVar()
							  
		self.entryvars[0].trace('w',self.auditSetup)
		self.entryvars[1].trace('w',self.auditSetup)
		self.entryvars[2].trace('w',self.auditSetup)
	def openWindow(self):
		self.pack()
		self.trialsframe.pack()
		for frame in self.trialsinnerframes:
			frame.pack(pady=2,
					   fill='both')
		self.diceframe.pack(pady=2,
							fill='both')
		self.summaryframe.pack()
		self.trialheaders[0].pack(pady=15)
		self.checkbuttons[0].pack(anchor='w')
		self.confidenceframe.pack()
		self.confidencelabel.pack(side='left')
		self.confidenceentry.pack(side='left')
		self.confidencepercent.pack(side='left')
		self.trialheaders[1].pack(pady=15)
		self.checkbuttons[1].pack(anchor='w')
		self.checkbuttons[2].pack(anchor='w')
		self.checkbuttons[3].pack(anchor='w')
		self.trialentryframe.pack()
		self.trialslabel.pack(side='left',
							  anchor='e')
		self.trialsentry.pack(side='left',
							  anchor='e')
		self.diceheader.pack()
		self.diceentry.pack()	
		self.summaryheader.pack()
		self.summarytext.pack()
		self.basebuttonframe.pack()
		self.button.pack()
		
	def closeWindow(self):
		self.destroy()
	def finalize(self):
		self.master.setupdict['trialsetup']=self.trialsetup
		window=RollingSetupWindow(self.master)
		self.master.changeWindow(window)						
	def trialTypeChange(self,change):
		trialchecks=[self.checkvars[0].get(),
					 self.checkvars[1].get()]
		if change==0 and trialchecks[0]==1:
			self.checkbuttons[1].deselect()
			self.confidenceentry.configure(state='normal')
		if change==0 and trialchecks[0]==0:
			self.confidenceentry.configure(state='disabled')
		elif change==1 and trialchecks[1]==1:
			self.checkbuttons[0].deselect()
			self.confidenceentry.configure(state='disabled')
		self.auditSetup()
	def trialIterationChange(self,change):
		trialchecks=[self.checkvars[2].get(),
					 self.checkvars[3].get()]
		if change==0 and trialchecks[0]==1:
			self.checkbuttons[3].deselect()
			self.trialsentry.configure(state='disabled')
		elif change==1 and trialchecks[1]==0:
			self.trialsentry.configure(state='disabled')
		elif change==1 and trialchecks[1]==1:
			self.checkbuttons[2].deselect()
			self.trialsentry.configure(state='normal')
		self.auditSetup()
	def auditSetup(self,a=1,b=2,c=3):
		checks=[]
		for check in self.checkvars:
			checks.append(check.get())
		confidence=self.entryvars[0].get()
		trials=self.entryvars[1].get()
		dice=self.entryvars[2].get()
		if checks[0] and confidence=='':
			confidence=None
		elif checks[0]:
			pass
		elif checks[1]:
			confidence='0'
		else:
			confidence=None
		if checks[3] and trials=='':
			trials=None
		elif checks[3]:
			pass
		elif checks[2]:
			trials='1000'
		else:
			trials=None
		if dice=='':
			dice=None
		if None in (confidence,trials,dice):
			self.summarytext.configure(state='normal')
			self.summarytext.delete('0.0','10.10')
			self.summarytext.insert('0.0',"Setup Incomplete")
			self.summarytext.configure(state='disabled')
			self.button.configure(state='disabled')
		elif self.invalidEntryCheck(confidence,trials,dice):
				text='Invalid Entry'
				self.summarytext.configure(state='normal')
				self.summarytext.delete('0.0','10.10')
				self.summarytext.insert('0.0',text)
				self.summarytext.configure(state='disabled')
				self.button.configure(state='disabled')
		else:
			if confidence=='0':
				text='There will be '+trials+' trials run'+\
					 ' on '+dice+' dice.'
				self.summarytext.configure(state='normal')
				self.summarytext.delete('0.0','10.10')
				self.summarytext.insert('0.0',text)
				self.summarytext.configure(state='disabled')
			else:
				text='There will be a max of '+trials+'\ntrials ran, '+\
					 'which will end\nearly if '+confidence+'% confidence\n'+\
					 'is achieved using '+dice+' dice.'
				self.summarytext.configure(state='normal')
				self.summarytext.delete('0.0','10.10')
				self.summarytext.insert('0.0',text)
				self.summarytext.configure(state='disabled')
			self.trialsetup=[confidence,trials,dice]
			self.button.configure(state='normal')
	def invalidEntryCheck(self,confidence,trials,dice):
		def is_int(s):
			try:
				int(s)
				return True
			except ValueError:
				return False
		intpass=False
		confidencepass=False
		trialspass=False
		dicepass=False
		if(is_int(confidence) and is_int(trials) and is_int(dice)):
			intpass=True
			confidence=int(confidence)
			trials=int(trials)
			dice=int(dice)
			if(confidence>=0 and confidence <=100):
				confidencepass=True
			if(trials>0):
				trialspass=True
			if(dice>0 and dice<=8):
				dicepass=True
			if(intpass and confidencepass and trialspass and dicepass):
				return False
		return True
class AreaSetupWindow(tk.Frame):
	def __init__(self,master,baseimg,img):
		tk.Frame.__init__(self,master)
		self.master = master
		self.baseimg=baseimg
		self.img=img
		
		self.hadjustment=0
		self.wadjustment=0
		self.angleadjustment=0
		self.xadjustment=0
		self.yadjustment=0
		
		self.upperframe=tk.Frame(self)
		self.lowerframe=tk.Frame(self)
		self.lowerbuttonframes=[tk.Frame(self.lowerframe),
								tk.Frame(self.lowerframe)]
		self.movementbuttonframe=[tk.Frame(self.lowerbuttonframes[0]),
								  tk.Frame(self.lowerbuttonframes[0]),
								  tk.Frame(self.lowerbuttonframes[0])]
		self.imglabel=tk.Label(self.upperframe,
							   image=self.img)
		self.turnsbuttons=[tk.Button(self.movementbuttonframe[0],
								     text='Rotate\nLeft',
								     command=lambda:self.rotateArea('left')),
						   tk.Button(self.movementbuttonframe[0],
								     text='Rotate\nRight',
								     command=lambda:self.rotateArea('right'))]
		self.resizebuttons=[tk.Button(self.movementbuttonframe[2],
									  text='Height(+)\nSize',
									  command=lambda:self.resizeArea('hup')),
							tk.Button(self.movementbuttonframe[2],
									  text='Height(-)\nSize',
									  command=lambda:self.resizeArea('hdown')),
							tk.Button(self.movementbuttonframe[2],
									  text='Width(+)\nSize',
									  command=lambda:self.resizeArea('wup')),
						    tk.Button(self.movementbuttonframe[2],
									  text='Width(-)\nSize',
									  command=lambda:self.resizeArea('wdown'))]
		self.movebuttons=[tk.Button(self.movementbuttonframe[1],
								    text='^',
								    command=lambda:self.moveArea('yup')),
						  tk.Button(self.movementbuttonframe[1],
								    text='<',
								    command=lambda:self.moveArea('xdown')),
						  tk.Button(self.movementbuttonframe[1],
								    text='>',
								    command=lambda:self.moveArea('xup')),
						  tk.Button(self.movementbuttonframe[1],
								    text='v',
								    command=lambda:self.moveArea('ydown'))]
		self.basebuttons=[tk.Button(self.lowerbuttonframes[1],
								    text='New Capture',
								    command=self.newCapture),
						  tk.Button(self.lowerbuttonframes[1],
								    text='Preview',
								    command=self.preview),
						  tk.Button(self.lowerbuttonframes[1],
								    text='Select and\nFinish',
								    command=self.selectArea,
								    state='disabled')]
	def openWindow(self):
		self.pack()
		self.upperframe.pack()
		self.imglabel.pack()
		self.lowerframe.pack()
		for frame in self.lowerbuttonframes:
			frame.pack()
		for frame in self.movementbuttonframe:
			frame.pack(side='left')	
		for button in self.turnsbuttons:
			button.pack(side='left')
		for button in self.resizebuttons:
			button.pack(side='left')
		for button in self.basebuttons:
			button.pack(side='left')
		self.movebuttons[0].pack(side='top')
		self.movebuttons[1].pack(side='left')
		self.movebuttons[2].pack(side='right')
		self.movebuttons[3].pack(side='bottom')
	def closeWindow(self):
		self.destroy()
	def newCapture(self):
		baseimg=imagemanipulation.getCapture()
		self.baseimg=imagemanipulation.resizeImage(baseimg,
												   scale=BASEIMAGESCALE)
		self.img=imagemanipulation.cv2pil(self.baseimg)
		self.imglabel.configure(image=self.img)
	def updateDiceArea(self):
		width,height=imagemanipulation.imageSize(self.baseimg)
		width=width+self.wadjustment
		height=height+self.hadjustment
		rect=imagemanipulation.findRectContours2(height,
												width,
												startx=self.xadjustment,
												starty=self.yadjustment)
		img=imagemanipulation.drawRect(self.baseimg,
									   rect,
									   angle=self.angleadjustment)

		"""
		img=imagemanipulation.drawRotatedRect(self.baseimg,
											  width,
											  height,
											  startx=self.xadjustment,
											  starty=self.yadjustment)
		"""
		self.img=imagemanipulation.cv2pil(img)
		self.imglabel.configure(image=self.img)
	def rotateArea(self,direction):
		self.basebuttons[2].configure(state='disabled') # No longer preview - Disallow finishing
		if direction=='left':
			self.angleadjustment=self.angleadjustment-0.1
		elif direction=='right':
			self.angleadjustment=self.angleadjustment+0.1
		self.updateDiceArea()
	def resizeArea(self,change):
		self.basebuttons[2].configure(state='disabled')
		if (change=='hup') and (self.hadjustment!=0):
			self.hadjustment=self.hadjustment+2
		elif change=='hdown':
			self.hadjustment=self.hadjustment-2
		if (change=='wup') and (self.wadjustment!=0):
			self.wadjustment=self.wadjustment+2
		elif change=='wdown':
			self.wadjustment=self.wadjustment-2
		self.updateDiceArea()
	def moveArea(self,change):
		self.basebuttons[2].configure(state='disabled')
		if change=='xup' and self.xadjustment<abs(self.hadjustment):
			self.xadjustment=self.xadjustment+2
		if change=='xdown' and self.xadjustment!=0:
			self.xadjustment=self.xadjustment-2
		if change=='yup' and self.yadjustment!=0:
			self.yadjustment=self.yadjustment-2
		if change=='ydown' and self.yadjustment<abs(self.wadjustment):
			self.yadjustment=self.yadjustment+2
		self.updateDiceArea()
	def preview(self):
		img=imagemanipulation.adjustImage2(self.baseimg,
										   angle=self.angleadjustment,
										   hchange=self.hadjustment,
										   wchange=self.wadjustment,
										   xchange=self.xadjustment,
										   ychange=self.yadjustment)
		self.img=imagemanipulation.cv2pil(img)
		self.imglabel.configure(image=self.img)
		self.basebuttons[2].configure(state='normal')
	def selectArea(self):
		areasetup=[self.angleadjustment,
				   self.hadjustment,
				   self.wadjustment,
				   self.xadjustment,
				   self.yadjustment]
		self.master.setupdict['areasetup']=areasetup
		window=RollingSetupWindow(self.master)
		self.master.changeWindow(window)
class RollingWindow(tk.Frame):
	def __init__(self, master=None):
		tk.Frame.__init__(self, master)
		self.master = master
		
		self.upperframe = tk.Frame(self)
		self.lowerframe = tk.Frame(self,highlightbackground='black',
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
		self.pack()
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
