import tkinter as tk
import math
from PIL import Image, ImageTk
from threading import Thread
from queue import Queue
import time
import accelerometer


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
ROOTSTARTDIM = 500
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

class  MenuBase(tk.Tk):
	def __init__(self, accelqueue):
		tk.Tk.__init__(self)
		monitorwidth = self.winfo_screenwidth()
		monitorheight = self.winfo_screenheight()
		self.wm_title("Automated Dice Roller")
		screen_width_center = int((monitorwidth-ROOTSTARTDIM)/2)
		screen_height_center = int((monitorheight-ROOTSTARTDIM)/2)
		location = str(ROOTSTARTDIM) + 'x' + str(ROOTSTARTDIM) + '+' \
			+ str(screen_width_center) + '+' + str(screen_height_center)
		self.geometry(location)
		self.runqueue = Queue()
		self.accelqueue = accelqueue
		self.x=0
		self.y=0
		
		self.introwindow = IntroWindow(self)
		self.accelwindow = AccelWindow(self)
		self.rollingwindow = rollingWindow(self)
		self.menu =BaseMenu(self)
		
		self.pushIntroFrame()
	def pushIntroFrame(self):
		self.introwindow.openFrame()
	def pushAccelFrame(self):
		self.introwindow.closeFrame()
		self.accelwindow.openFrame()
		self.menu.drawMenu()
	def runAccel(self):
		self.runqueue.put(True)
		def thread_accel(threadname, runqueue, accelqueue):
			while(runqueue.get()):
				runqueue.put(True)
				accelerometer.init_accel()
				axes = accelerometer.get_axes(30)
				accelqueue.put(axes)
				while(not accelqueue.empty()):
					time.sleep(0.0001)
				time.sleep(0.00001)
		self.accelthread=Thread(target=thread_accel,args=("Thread-1",self.runqueue,self.accelqueue))
		self.accelthread.start()
	def getAccelAxes(self):
		axes = self.accelqueue.get()
		self.x=axes[0]
		self.y=axes[1]
	def pushRollingFrame(self):
		self.accelwindow.closeFrame()
		self.destroythread()
		self.rollingwindow.openFrame()
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
			command=self.nextframe)
		self.buttonquit = tk.Button(self.buttonframe, text = 'Quit', 
			command=self.quitprogram)
	def openFrame(self):
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
	def closeFrame(self):
			self.destroy()
	def nextframe(self):
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
		
		self.button = tk.Button(self, text='Continue', command=self.pushFrame)
		self.button.pack(side='top')
		
	def closeWindow(self):
		self.callingframe.popupopen = 0
		self.callingframe.buttonstart["state"]='normal'
		self.master.destroy()
	def pushFrame(self):
		self.callingframe.popupopen = 0
		self.framemaster.destroy()
		self.rootmaster.pushAccelFrame()

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
			command=self.master.pushRollingFrame)
	def openFrame(self):
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
		self.after(150, self.loopAccel)
		self.drawFullCanvas(1)
	def closeFrame(self):
		self.destroy()
class rollingWindow(tk.Frame):
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
		self.buttonQuit = tk.Button(self.buttonframe,text='Quit',command=self.master.exit)
	def openFrame(self):
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
