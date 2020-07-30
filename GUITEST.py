import tkinter as tk
from tkinter import filedialog
import math
import time
import dicedetector
import cv2
import imagemanipulation
import cameracontrol

DIRECTIONSCOLORCAILBRATION='Directions: Place a set of dice in the image capture area,\n'+\
								  'then adjust Hue,Saturation,and Lightness thresholds until:\n'+\
								  '1)Dice Box is uniform white with little to no black holes\n'+\
								  '2)Dice Boxes are as closely approximated to a square as possible'
DIRECTIONSBACKGROUNDCROP='DIRECTIONS: Get a capture of the empty board space, then\n'+\
						 'press "Get Threshold Base" button to get new thresholds \n'+\
						 'for background color filtering. When finished, press "Next"\n'+\
						 'button, and calibration of threshold values will be finalized.\n'+\
						 'These values will be used to filter background from dice recognition.'
DIRECTIONSTEMPLATECROP="DIRECTIONS\n'Templates' of each of the dice are required by the device,"+\
					   "including their rotated counterparts.\nTo get the required templates, "+\
					   "the user must:\n"+\
					   "1)Crop the dice into a smaller template\n"+\
					   "2)Further refine the template by rotating,shrinking,and moving the "+\
					   "image until the dice symbol\n has been properly extracted."+\
					   "This must be done in order, starting from the dice valued 1\n"+\
					   "--Press 'Crop Next Template' to begin--"
DIRECTIONSTEMPLATECROP2="DIRECTIONS\nClick on one corner of the dice to crop, then click on the"+\
						" opposite corner.\nNOTE:Only the width is taken into account on the second square"+\
						" to keep\n images square."
DIRECTIONSTEMPLATECROP3="DIRECTIONS\nThe image on the left is the image before modification, while the"+\
						" image on the right is the modified template.\nUse the provided buttons to reduce the"+\
						" space on the modified template so only the symbol and a reasonable\namount of dice"+\
						" surface is visible, with visible rolling surface."
DICETEMPLATESPACE=3
DICECROPS=(250,250,600,600)
BASEIMAGESCALE=1
#Using the previous thresholding values gathered from the backgroundCropWindow
#as a base, the user is able to further refine the background filtering with
#the dice to be tested on the rolling space. This feature is mandatory to ensure
#a proper dice square is isolated for proper dice recognition algorimth operation
class ColorThresholdingWindow(tk.Frame):
	def __init__(self, master,baseimg,baseimgpil,maskimg):
		tk.Frame.__init__(self, master)
		self.master = master
		
		self.baseimg=baseimg
		self.baseimgpil=baseimgpil
		maskimg=dicedetector.calibrateMask2(self.baseimg)
		self.maskimg=cv2pil(maskimg)
		self.thresholdvals= [0,0,0,0,0,0]
		
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
		
		self.directiontext=tk.Label(self.lowerFrame,
									text=DIRECTIONSCOLORCAILBRATION)

		self.img=[]
		self.img.append(tk.Label(self.midFrame,
								 image=self.baseimgpil))
		self.img.append(tk.Label(self.midFrame,
								 image=self.maskimg))
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
	#Gets a new mask image based on threshold values set on trackbars.
	#Called every time the trackbar is updated.
	def getNewMask(self,_):
		for x in range(6):
			self.thresholdvals[x]=self.trackbars[x].get()
		self.maskimg=dicedetector.calibrateMask2(self.baseimg,
											     self.thresholdvals[0],
											     self.thresholdvals[1],
											     self.thresholdvals[2],
											     self.thresholdvals[3],
											     self.thresholdvals[4],
											     self.thresholdvals[5])
		self.maskimg=cv2pil(self.maskimg)
		self.img[1].configure(image=self.maskimg)
		self.img[1].image=self.maskimg
#This window has all the features finding a base thresholding solution
#for background filtering using an image of an empty rolling space.
#These values can be further refined later in the colorThresholdingWindow
#using actual dice to ensure solution works in a realistic rolling setting.
class BackgroundCropWindow(tk.Frame):
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
								 text=DIRECTIONSBACKGROUNDCROP)
		self.newcapturebutton=tk.Button(self.lowerframe,
										text='New Capture')
		self.getbasethresholdbutton=tk.Button(self.lowerframe,
										text='Get Threshold Base',
										command=self.getThresholdValues)
		self.nextbutton=tk.Button(self.lowerframe,
								  text='Calibrate Threshold\n(Next)',
								  state='disabled')
		
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
											text='New Solution'),
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
class TemplateCreationWindow(tk.Frame):
	def __init__(self,master,baseimg,img):
		tk.Frame.__init__(self,master)
		self.master = master
		self.img=img
		self.baseimg=baseimg
		self.diceimgs=[]
		self.imagesize=dicedetector.imageSize(baseimg)
		print(self.imagesize)
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
		self.directionstext.set(DIRECTIONSTEMPLATECROP)
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
	def newCapture(self):
		self.baseimg=imagemanipulation.getCapture()
		self.baseimg=imagemanipulation.cropImage(self.baseimg,
												 DICECROPS[0],
												 DICECROPS[1],
												 DICECROPS[2],
												 DICECROPS[3])
		self.img=imagemanipulation.cv2pil(self.baseimg)
		self.canvasimg= self.canvas.create_image(0,
												 0,
												 anchor='nw',
												 image=self.img)
		#self.baseimg=
	def enableCropping(self):
		self.canvas.bind("<Button-1>",self.callback)
		self.directionstext.set(DIRECTIONSTEMPLATECROP2)
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
		width,height=dicedetector.imageSize(img)
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
		pass	
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
			img=dicedetector.cropImage(self.baseimg,startx,starty,width,width)
			self.tempopencv=img
			self.tempbefore=(imagemanipulation.cv2pil(img))
			self.tempafter=self.tempbefore
			for label in self.temptemplateimgs:
				label.configure(image=self.tempbefore)
			self.directionstext.set(DIRECTIONSTEMPLATECROP3)
			self.frameSwitch(frame='template')
			self.canvas.unbind("<Button-1>")
class AreaSetupWindow(tk.Frame):
	def __init__(self,master,baseimg,img):
		tk.Frame.__init__(self,master)
		self.master = master
		self.baseimg=baseimg
		self.img=img
		
		self.sizeadjustment=0
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
									  text='Increase(+)\nSize',
									  command=lambda:self.resizeArea('increase')),
						    tk.Button(self.movementbuttonframe[2],
									  text='Decrease(-)\nSize',
									  command=lambda:self.resizeArea('decrease'))]
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
	def newCapture(self):
		baseimg=imagemanipulation.getCapture()
		self.baseimg=imagemanipulation.resizeImage(baseimg,
												   scale=BASEIMAGESCALE)
		self.img=imagemanipulation.cv2pil(self.baseimg)
		self.imglabel.configure(image=self.img)
	def updateDiceArea(self):
		width,height=imagemanipulation.imageSize(self.baseimg)
		print((width,height))
		width=width+self.sizeadjustment
		height=height+self.sizeadjustment
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
		if (change=='increase') and (self.sizeadjustment!=0):
			self.sizeadjustment=self.sizeadjustment+2
		elif change=='decrease':
			self.sizeadjustment=self.sizeadjustment-2
		self.updateDiceArea()
	def moveArea(self,change):
		self.basebuttons[2].configure(state='disabled')
		if change=='xup' and self.xadjustment<abs(self.sizeadjustment):
			self.xadjustment=self.xadjustment+2
		if change=='xdown' and self.xadjustment!=0:
			self.xadjustment=self.xadjustment-2
		if change=='yup' and self.yadjustment!=0:
			self.yadjustment=self.yadjustment-2
		if change=='ydown' and self.yadjustment<abs(self.sizeadjustment):
			self.yadjustment=self.yadjustment+2
		self.updateDiceArea()
	def preview(self):
		img=imagemanipulation.adjustImage2(self.baseimg,
										   angle=self.angleadjustment,
										   sizechange=self.sizeadjustment,
										   xchange=self.xadjustment,
										   ychange=self.yadjustment)
		self.img=imagemanipulation.cv2pil(img)
		self.imglabel.configure(image=self.img)
		self.basebuttons[2].configure(state='normal')
	def selectArea(self):
		#Send image cropping information to root
		pass
top=tk.Tk()	
baseimg = cv2.imread('dicetest/white/baselinecropped.jpg', -1)
#baseimg = cv2.imread('dicetest/white/white1cropped.jpg', -1)
#baseimg = cv2.imread('dicetest/white/backgroundcrop.jpg', -1)
baseimg = dicedetector.resizeImage(baseimg)
img=baseimg.copy()
img=imagemanipulation.cv2pil(img)

#baseimg=cv2.cvtColor(baseimg,cv2.COLOR_BGR2HSV)

#a=ColorThresholdingWindow(top,baseimg,img,img)
#a.pack()

#a=BackgroundCropWindow(top,baseimg,img)
#a.pack()

#a=RollingSetupWindow(top)
#a.pack()

#a=TemplateCreationWindow(top,baseimg,img)
#a.pack()

a=AreaSetupWindow(top,baseimg,img)
a.openWindow()

top.mainloop()
