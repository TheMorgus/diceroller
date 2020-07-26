import cv2
import numpy as np
#import sys

ORANGE = np.uint8([[[0,140,255]]])
HSV_ORANGE = cv2.cvtColor(ORANGE, cv2.COLOR_BGR2HSV)

FONT=cv2.FONT_HERSHEY_SIMPLEX
FONTSCALE=2
FONTCOLOR=(180,50,50)
LINETYPE=2
OFFSET=10
def removeBackground(image, bgcolor,hadjustlow=10,slow=100,vlow=100,\
	hadjusthigh=10,shigh=255,vhigh=255):
	imagehsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
	h = bgcolor[0,0,0]
	#s = bgcolor[0,0,1]
	#v = bgcolor[0,0,2]
	
	low_background = np.array([h-hadjustlow,slow,vlow])
	high_background = np.array([h+hadjusthigh,shigh,vhigh])
	mask = cv2.inRange(imagehsv, low_background, high_background)
	mask = cv2.bitwise_not(mask)
	
	#Basic filtering and noise reduction
	kernel = np.ones((5,5),np.uint8)
	mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN,kernel)
	kernel = np.ones((5,5),np.float32)/25
	mask = cv2.filter2D(mask,-1,kernel)
	#kernel=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(9,9))
	#mask=cv2.dilate(mask,kernel)
	_,mask=cv2.threshold(mask,1,255,cv2.THRESH_BINARY)
	res = cv2.bitwise_and(img,img,mask=mask)
	return res,mask
def showDiceArea(image):
	img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	ret,thresh=cv2.threshold(image,1,255,cv2.THRESH_BINARY)
	return thresh

def clickColor(event, x, y, flags, param):
	global refPt
	global img
	if event == cv2.EVENT_LBUTTONDOWN:
		refPt=[(x,y)]
		print(refPt)
		print(img[y,x])
def clickPoint(event, x, y, flags, param):
	global refPt
	global img
	if event == cv2.EVENT_LBUTTONDOWN:
		refPt=[(x,y)]
		#print(refPt)
def isolateDice(diceimage,mainimg):
	diceimage = cv2.cvtColor(diceimage, cv2.COLOR_BGR2GRAY)
	_,contours,_=cv2.findContours(diceimage,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
	contours2=[]
	for cnt in contours:
		print(cv2.contourArea(cnt))
		if(cv2.contourArea(cnt)>2000)and(cv2.contourArea(cnt)<4000):
			contours2.append(cnt)
	warped=[]
	rects=[]
	for cnt in contours2:
		rect=cv2.minAreaRect(cnt)
		rects.append(rect)
		box=cv2.boxPoints(rect)
		box=np.int0(box)
		cv2.drawContours(img,[box],0,(30,100,100),3)
	
		width=int(rect[1][0])
		height=int(rect[1][1])
	
		src_pts=box.astype("float32")
		dst_pts=np.array([[0,height-1],
			[0,0],
			[width-1,0],
			[width-1,height-1]],dtype="float32")
		M=cv2.getPerspectiveTransform(src_pts,dst_pts)
		warped.append(cv2.warpPerspective(img,M,(width,height)))
	return warped,rects

def rotateImg(img,angle):
	height,width,_ = img.shape
	M=cv2.getRotationMatrix2D((width/2,height/2),angle,1)
	res=cv2.warpAffine(img,M,(width,height))
	return res
def createRotatedTemplates(basetemplate):
	template=[]
	template.append(basetemplate)
	for x in range(1,4):
		template.append(rotateImg(basetemplate,90*x))
	return template
def resizeImage(img):
	img = cv2.pyrDown(img)
	img = cv2.pyrDown(img)
	return img
def getTemplates():
	dicetemplates = []
	template=cv2.imread('dicetest/numbers/templateone.jpg')
	template = resizeImage(template)
	dicetemplates.append(template)
	template=cv2.imread('dicetest/numbers/templatetwo.jpg')
	template = resizeImage(template)
	dicetemplates.append(template)
	template=cv2.imread('dicetest/numbers/templatethree.jpg')
	template = resizeImage(template)
	dicetemplates.append(template)
	template=cv2.imread('dicetest/numbers/templatefour.jpg')
	template = resizeImage(template)
	dicetemplates.append(template)
	template=cv2.imread('dicetest/numbers/templatefive.jpg')
	template = resizeImage(template)
	dicetemplates.append(template)
	template=cv2.imread('dicetest/numbers/templatesix.jpg')
	template = resizeImage(template)
	dicetemplates.append(template)
	return dicetemplates
def completeTemplates(templates):
	completeTemplates =[]
	for x in range(6):
		completeTemplates.append(createRotatedTemplates(templates[x]))
	return completeTemplates
def discernDice(templatearray,dicearray,mainimg):
	dicevals=[]
	for dice in dicearray:
		minarray=[]
		for dicetemplatearray in templatearray:
			minvals=[]
			for dicetemplate in dicetemplatearray:
				search=cv2.matchTemplate(dice,dicetemplate,cv2.TM_SQDIFF)
				minval,_,_,_=cv2.minMaxLoc(search)
				minvals.append(minval)
			minarray.append(min(minvals))
		index=minarray.index(min(minarray))
		dicevals.append(index+1) #aopends the value of dice with the lowest value (which is associated with the highest match between template and image)
	return dicevals
def drawDiceVals(dicevals,rects,mainimg):
	x=0
	for val in dicevals:
		cv2.putText(mainimg,str(val),
		(int(rects[x][0][0])+OFFSET,int(rects[x][0][1])-OFFSET),
		FONT,
		FONTSCALE,
		FONTCOLOR,
		LINETYPE)
		x=x+1
def clickAndCrop(x):
	pass
#Function takes the base image of the dice space
#then provides a GUI that allows the user to calibrate the color thresholding
#by using a visual representation of the mask used in dice recognition
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
	
	res = cv2.bitwise_and(img,img,mask=mask)
	
	cv2.namedWindow('image')
	cv2.namedWindow('trackbars')
	cv2.createTrackbar('H-HIGH','trackbars',0,255,nothing)
	cv2.createTrackbar('H-LOW','trackbars',0,255,nothing)
	cv2.createTrackbar('S-HIGH','trackbars',0,255,nothing)
	cv2.createTrackbar('S-LOW','trackbars',0,255,nothing)
	cv2.createTrackbar('V-HIGH','trackbars',0,255,nothing)
	cv2.createTrackbar('V-LOW','trackbars',0,255,nothing)
	cv2.imshow('trackbars',blankimg)
	
	while(1):
		cv2.imshow('image',mask)

		k=cv2.waitKey(1)&0xFF
		if k==27:
			break
		
		#get current position of trackbars
		h_high=cv2.getTrackbarPos('H-HIGH','trackbars')
		h_low=cv2.getTrackbarPos('H-LOW','trackbars')
		s_high=cv2.getTrackbarPos('S-HIGH','trackbars')
		s_low=cv2.getTrackbarPos('S-LOW','trackbars')
		v_high=cv2.getTrackbarPos('V-HIGH','trackbars')
		v_low=cv2.getTrackbarPos('V-LOW','trackbars')
		threshold = [(h_low,h_high),
					 (s_low,s_high),
					 (v_low,v_high)]
		
		#create mask from trackbar thresholds
		low_background = np.array([h_low,s_low,v_low])
		high_background = np.array([h_high,s_high,v_high])
		mask = cv2.inRange(imagehsv, low_background, high_background)
		mask = cv2.bitwise_not(mask)
		#Filtering for mask
		#Exact same as filtering done in algorithim for mask
		#so result is accurate to alogorithm
		kernel = np.ones((5,5),np.uint8)
		mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN,kernel)
		kernel = np.ones((5,5),np.float32)/25
		mask = cv2.filter2D(mask,-1,kernel)
		
		_,mask=cv2.threshold(mask,1,255,cv2.THRESH_BINARY)		
		res = cv2.bitwise_and(img,img,mask=mask)
		
	cv2.destroyWindow('image')
	cv2.destroyWindow('trackbars')	
	return threshold
def calibrateMask2(img,hhigh=5,hlow=15,shigh=255,slow=40,vhigh=40,vlow=255):
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
	
def selectAndCrop(img):
	img = img.copy()
	cv2.imshow('image',img)
	cv2.namedWindow("image")
	cv2.setMouseCallback("image",clickPoint)
	points=[None,None]
	global refPt
	while(1):
		cv2.imshow('image',img)
		if refPt[0]==(None,None):
			pass
		elif points[0]==None:
			points[0]=refPt[0]
			refPt = [(None,None)]
		else:
			points[1]=refPt[0]
			refPt = [(None,None)]
			width = abs(points[1][0]-points[0][0]) #Width = Height so template is a complete square
			startx=points[0][0]					   #This allows 90* rotations with zero image loss
			starty=points[0][1]
			if startx>points[1][0]:
				startx=points[1][0]
			if starty>points[1][1]:
				starty=points[1][1]
			img=img[starty:starty+width,startx:startx+width]
			break
		k=cv2.waitKey(1)&0xFF
		if k==27:
			break
	return img
def imageSize(img):
	x,y,_=img.shape
	return x,y		
if __name__=="__main__":
	img = cv2.imread('dicetest/numbers/number3cropped.jpg', -1)
	img = resizeImage(img)
	#colorthreshold=calibrateMask(img)
	refPt = [(None,None)]	
	
	#cv2.imshow('image',img)
	im=selectAndCrop(img)
	cv2.imshow('image',im)
	"""
	isodiceimg,mask = removeBackground(img,HSV_ORANGE,hadjustlow=10,hadjusthigh=10)


	dicearray,rects=isolateDice(isodiceimg,img)
	templates = getTemplates()
	templates = completeTemplates(templates)
	#e1=cv2.getTickCount() Measuring performance, for 6 dice takes around 0.12 seconds to analyze an image
	dicevals=discernDice(templates,dicearray,img)
	drawDiceVals(dicevals,rects,img)
	#e2=cv2.getTickCount()
	#time=(e2-e1)/cv2.getTickFrequency()
	#print(time)
	cv2.imshow('image',img)
	"""
	#For debugging purposes (finding colors based on mouseclick on displayed image)
	cv2.namedWindow("image")
	cv2.setMouseCallback("image",clickColor)

	cv2.waitKey(0)
	cv2.destroyAllWindows()
