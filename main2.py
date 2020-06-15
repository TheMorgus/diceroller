import tkinter as tk
from PIL import Image, ImageTk

TITLETEXT = "Group 5\nAutomated Dice Roller"
INTROTEXT = "Group 5 Members: Adrian Bashi, Christian Moriondo,\n"\
	"Jason Mallon, Kelly Castanon, Chris Kenneth Viray,\n"\
	"Nathan Vore, Abigail Yaldo.\n\n"\
	"Instructors: Shadi Alawneh, Steve Bazinski."
MESSAGEACCEL= "The dice roller machine must be placed on a relatively\n "\
	"flat surface. The machine will now sense its orientation and\n"\
	"if machine tilt is beyond specifications, operator must\n"\
	"realign machine using adjustable feet."
DICEFILE = "dice.png"
DICEIMAGEDIM = 285
ROOTSTARTDIM = 500
POPUPWIDTH = 400
POPUPHEIGHT = 100

class  MenuBase(tk.Tk):
	def __init__(self):
		tk.Tk.__init__(self)
		monitorwidth = self.winfo_screenwidth()
		monitorheight = self.winfo_screenheight()
		self.wm_title("Automated Dice Roller")
		screen_width_center = int((monitorwidth-ROOTSTARTDIM)/2)
		screen_height_center = int((monitorheight-ROOTSTARTDIM)/2)
		location = str(ROOTSTARTDIM) + 'x' + str(ROOTSTARTDIM) + '+' \
			+ str(screen_width_center) + '+' + str(screen_height_center)
		self.geometry(location)
		
		self.introwindow = IntroWindow(self)
		self.accelwindow = AccelWindow(self)
		self.menu =BaseMenu(self)
		
		self.pushIntroFrame()
	def pushIntroFrame(self):
		self.introwindow.openFrame()
	def pushAccelFrame(self):
		self.introwindow.closeFrame()
		self.accelwindow.openFrame()
		self.menu.drawMenu()
	def exit(self):
		self.destroy()
	def loop(self):
		self.mainloop()
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
		#self.destroy()
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
	def openFrame(self):
		self.pack(fill='none',expand=1)
		
		tk.Label(self, text ='HELLO').pack()
		
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
		self.filemenu[0].add_command(label="Exit", accelerator='(Crtl + X)',
			command=self.master.exit)
		self.master.config(menu=self)
	
		
menu = MenuBase()
menu.loop()

