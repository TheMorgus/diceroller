import cv2
import numpy as np
import io
import time
import picamera
from PIL import Image, ImageTk

RESIZESCALE=0.3
def showImage(img):#for testing purposes
	cv2.imshow('image',img)
	cv2.namedWindow("image")

	cv2.waitKey(0)
	cv2.destroyAllWindows()
def resizeImage(img,scale=RESIZESCALE):
	img = cv2.pyrDown(img)
	#img = cv2.pyrDown(img)
	#img = cv2.pyrDown(img)
	width,height=imageSize(img)
	width=int(scale*width)
	height=int(scale*height)
	img = cv2.resize(img,(height,width),interpolation=cv2.INTER_AREA)
	return img
def resizeByDim(img,size):
	img=cv2.resize(img,size,interpolation=cv2.INTER_AREA)
	return img
def imageSize(img):
	x,y,_=img.shape
	return x,y
def cropImage(img,startx,starty,width,height):
	img=img.copy()
	img=img[starty:starty+width,startx:startx+width]
	return img
def cropImage2(img,startx,starty,width,height):
	img=img.copy()
	img=img[starty:starty+height,startx:startx+width]
	return img	
def findRectContours(width,height,startx,starty):
	points=[[startx,starty],
			[startx+width,starty],
			[startx+width,starty+height],
			[startx,starty+height]]
	contours=np.array(points).reshape((-1,1,2)).astype(np.int32)
	rect=cv2.minAreaRect(contours)
	return rect
def findRectContours2(width,height,startx,starty):
	cnts=np.array([
			[[startx,starty]],
			[[startx+width,starty]],
			[[startx+width,starty+height]],
			[[startx,starty+height]]
			])
	rect=cv2.minAreaRect(cnts)
	return rect
def drawRect(img,rect,angle):
	img=img.copy()
	a,b,c=rect
	angle=c+angle
	rect=a,b,angle
	box=cv2.boxPoints(rect)
	box=np.int0(box)
	cv2.drawContours(img,[box],0,(0,255,0),2)
	return img
def drawRotatedRect(baseimg,height,width,startx,starty):
	img=baseimg.copy()
	
	cnt=np.array([
			[[startx,starty]],
			[[startx+width,starty]],
			[[startx+width,starty+height]],
			[[startx,starty+height]]
			])
	rect=cv2.minAreaRect(cnt)
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
def adjustImage2(img,angle=0,hchange=0,wchange=0,xchange=0,ychange=0):
	height,width=imageSize(img)
	startx=xchange
	starty=ychange
	endwidth=width+hchange
	endheight=height+wchange
	
	centerx = startx+int(endwidth/2)
	centery = starty+int(endheight/2)
	
	img=rotateImg2(img,angle,centerx,centery)
	img=cropImage2(img,startx,starty,endwidth,endheight)
	
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
def getCaptureTest(num):
	if num==0:
		path = 'dicetest/white/white0cropped.jpg'
	else:
		path = 'dicetest/white/white'+str(num)+'cropped.jpg'
	img = cv2.imread(path, -1)
	return img
def convertHSV(img):
	img=cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
	return img
def getCaptureDUMMY(option='1'):
	if option=='1':
		baseimg = cv2.imread('dicetest/white/backgroundcrop.jpg', -1)
	if option=='2':
		baseimg = cv2.imread('dicetest/white/white1cropped.jpg',-1)
	if option=='3':
		baseimg = cv2.imread('dicetest/numbers/number1cropped.jpg',-1)
	if option=='4':
		baseimg=cv2.imread('dicetest/white/baselinecropped.jpg', -1)
	return(baseimg)
#Converts the OpenCV image types into an a PIL image
#so the image can be displayed in tkinter
def calibrateMask(img,hhigh=5,hlow=15,shigh=255,slow=40,vhigh=40,vlow=255):
	#HSV color is ideal for masking, as it is resistance to shadow and lighting
	#effects for filter colors. As a result, image converted to HSV color space
	#for filtering background colors from dice colors
	imagehsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
	
	#Creates a blank image (all black)
	#Size of this image determines the length of the trackbars in trackbar
	#window
	blankimg = np.array([0,0,0])
	row=1
	col=400
	blankimg=np.full((row,col,3),blankimg)
	
	low_background = np.array([hlow,slow,vlow])
	high_background = np.array([hhigh,shigh,vhigh])
	mask = cv2.inRange(imagehsv, low_background, high_background)
	mask = cv2.bitwise_not(mask)
	kernel = np.ones((5,5),np.uint8)
	mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN,kernel)
	kernel = np.ones((5,5),np.float32)/25
	mask = cv2.filter2D(mask,-1,kernel)
	
	res = cv2.bitwise_and(img,img,mask=mask)

	return(mask)
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
