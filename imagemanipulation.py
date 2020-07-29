import cv2
import numpy as np
import io
import time
import picamera
from PIL import Image, ImageTk

def imageSize(img):
	x,y,_=img.shape
	return x,y
def cropImage(img,startx,starty,width,height):
	img=img.copy()
	img=img[starty:starty+width,startx:startx+width]
	return img
def findRectContours(width,height,startx,starty):
	points=[[startx,starty],
			[startx+width,starty],
			[startx+width,starty+height],
			[startx,starty+height]]
	contours=np.array(points).reshape((-1,1,2)).astype(np.int32)
	rect=cv2.minAreaRect(contours)
	return rect
def drawRect(img,rect,angle):
	img=img.copy()
	a,b,c=rect
	rect=a,b,angle
	box=cv2.boxPoints(rect)
	box=np.int0(box)
	cv2.drawContours(img,[box],0,(0,255,0),2)
	return img
def rotateImg(img,angle):
	height,width,_ = img.shape
	M=cv2.getRotationMatrix2D((width/2,height/2),angle,1)
	res=cv2.warpAffine(img,M,(width,height))
	return res
def rotateImg2(img,angle,centerx,centery):
	height,width,_ = img.shape
	M=cv2.getRotationMatrix2D((centerx,centery),angle,1)
	res=cv2.warpAffine(img,M,(width,height))
	return res
def createRotatedTemplates(basetemplate):
	template=[]
	template.append(basetemplate)
	for x in range(1,4):
		template.append(rotateImg(basetemplate,90*x))
	return template
def adjustImage(img,angle=0,sizechange=0,xchange=0,ychange=0):
	width,height=imageSize(img)
	startx=xchange
	starty=ychange
	endwidth=width+sizechange
	endheight=height+sizechange
	
	centerx = startx+int(endwidth/2)
	centery = starty+int(endheight/2)
	
	img=rotateImg2(img,angle,centerx,centery)
	img=cropImage(img,startx,starty,endwidth,endheight)
	
	return(img)
def getCapture():
	stream=io.BytesIO()
	with picamera.PiCamera() as camera:
		camera.start_preview()
		#time.sleep(0.1)
		camera.capture(stream,format='jpeg')
	data=np.fromstring(stream.getvalue(),dtype=np.uint8)
	image=cv2.imdecode(data,1)
	return(image)
#Converts the OpenCV image types into an a PIL image
#so the image can be displayed in tkinter
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
	return new_img
