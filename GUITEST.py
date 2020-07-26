import tkinter as tk
import math
from PIL import Image, ImageTk
import time
import dicedetector
import cv2

text=DIRECTIONSCOLORCAILBRATION = 'Directions: Place a set of dice in the image capture area,\n'+\
								  'then adjust Hue,Saturation,and Lightness thresholds until:\n'+\
								  '1)Dice Box is uniform white with little to no black holes\n'+\
								  '2)Dice Boxes are as closely approximated to a square as possible'
class colorThresholdingWindow(tk.Frame):
	def __init__(self, master,baseimg,baseimgpil,maskimg):
		tk.Frame.__init__(self, master)
		self.master = master
		
		self.baseimg=baseimg
		self.baseimgpil=baseimgpil
		maskimg=dicedetector.calibrateMask2(self.baseimg)
		self.maskimg=cv2pil(maskimg)
		self.thresholdvals= [0,0,0,0,0,0]
		print(self.thresholdvals)
		
		self.upperFrame=tk.Frame(self)
		self.midFrame=tk.Frame(self)
		self.lowerFrame=tk.Frame(self)
		self.upperFrames=[tk.Frame(self.upperFrame),tk.Frame(self.upperFrame),tk.Frame(self.upperFrame)]

		self.headers=[]

		self.headers.append(tk.Label(self.upperFrames[0],
							text='HUE'))
		self.headers.append(tk.Label(self.upperFrames[1],
							text='SATURATION'))
		self.headers.append(tk.Label(self.upperFrames[2],
							text='LIGHTNESS'))
		huelabels=[]
		satlabels=[]
		lightlabels=[]
		huelabels.append(tk.Label(self.upperFrames[0],text='HIGH'))
		huelabels.append(tk.Label(self.upperFrames[0],text='LOW'))
		satlabels.append(tk.Label(self.upperFrames[1],text='HIGH'))
		satlabels.append(tk.Label(self.upperFrames[1],text='LOW'))
		lightlabels.append(tk.Label(self.upperFrames[2],text='HIGH'))
		lightlabels.append(tk.Label(self.upperFrames[2],text='LOW'))
		self.labels=[]
		self.labels.append(huelabels)
		self.labels.append(huelabels)
		self.labels.append(huelabels)
		
		self.trackbars=[]
		self.trackbars.append(tk.Scale(self.upperFrames[0],
							  from_=0,to=255,orient='horizontal',
							  command=self.getNewMask))
		self.trackbars.append(tk.Scale(self.upperFrames[0],
							  from_=0,to=255,orient='horizontal',
							  command=self.getNewMask))
		self.trackbars.append(tk.Scale(self.upperFrames[1],
							  from_=0,to=255,orient='horizontal',
							  command=self.getNewMask))
		self.trackbars.append(tk.Scale(self.upperFrames[1],
							  from_=0,to=255,orient='horizontal',
							  command=self.getNewMask))
		self.trackbars.append(tk.Scale(self.upperFrames[2],
							  from_=0,to=255,orient='horizontal',
							  command=self.getNewMask))
		self.trackbars.append(tk.Scale(self.upperFrames[2],
							  from_=0,to=255,orient='horizontal',
							  command=self.getNewMask))
		
		self.directiontext=tk.Label(self.lowerFrame,text=DIRECTIONSCOLORCAILBRATION)
		#render=ImageTk.PhotoImage(image=self.baseimg)
		self.img=[]
		self.img.append(tk.Label(self.midFrame,image=self.baseimgpil))
		self.img.append(tk.Label(self.midFrame,image=self.maskimg))
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
		
		self.retrievebutton=tk.Button(self.lowerFrame,text='New Capture')
		self.donebutton=tk.Button(self.lowerFrame,text='Use Selected Values')
		
		self.directiontext.pack(side='top')
		self.retrievebutton.pack(side='left')
		self.donebutton.pack(side='right')
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
def cv2pil(img):
	
	new_img=img.copy()
	if new_img.ndim==2:
		pass
	elif new_img.shape[2]==3:
		new_img=cv2.cvtColor(new_img,cv2.COLOR_BGR2RGB)
	elif new_img.shape[2]==4:
		new_img=cv2.cvtColor(new_img,cv2.COLOR_BGRA2RGBA)
	new_img=Image.fromarray(new_img)
	new_img=ImageTk.PhotoImage(image=new_img)
	"""
	new_img=cv2.flip(img,1)
	new_img=cv2.cvtColor(img,cv2.COLOR_BGR2RGBA)
	new_img=Image.fromarray(new_img)
	cv2.imshow('image',img)
	print(new_img)
	"""
	return new_img
	
top=tk.Tk()	
baseimg = cv2.imread('dicetest/white/white2cropped.jpg', -1)
baseimg = dicedetector.resizeImage(baseimg)
img=baseimg.copy()
img=cv2pil(img)

a=colorThresholdingWindow(top,baseimg,img,img)
a.pack()
top.mainloop()
