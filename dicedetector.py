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
	kernel = np.ones((5,5),np.uint8)
	mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN,kernel)
	#Basic filtering and noise reduction
	kernel = np.ones((5,5),np.float32)/25
	mask = cv2.filter2D(mask,-1,kernel)
	kernel=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(9,9))
	mask=cv2.dilate(mask,kernel)
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
		print(res[y,x])

def isolateDice(diceimage,mainimg):
	diceimage = cv2.cvtColor(diceimage, cv2.COLOR_BGR2GRAY)
	_,contours,_=cv2.findContours(diceimage,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
	contours2=[]
	for cnt in contours:
		#print(cv2.contourArea(cnt))
		if(cv2.contourArea(cnt)>3000)and(cv2.contourArea(cnt)<4000):
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
def getTemplates():
	dicetemplates = []
	template=cv2.imread('dicetest/white/templateone.jpg')
	template = cv2.pyrDown(template)
	template = cv2.pyrDown(template)
	dicetemplates.append(template)
	template=cv2.imread('dicetest/white/templatetwo.jpg')
	template = cv2.pyrDown(template)
	template = cv2.pyrDown(template)
	dicetemplates.append(template)
	template=cv2.imread('dicetest/white/templatethree.jpg')
	template = cv2.pyrDown(template)
	template = cv2.pyrDown(template)
	dicetemplates.append(template)
	template=cv2.imread('dicetest/white/templatefour.jpg')
	template = cv2.pyrDown(template)
	template = cv2.pyrDown(template)
	dicetemplates.append(template)
	template=cv2.imread('dicetest/white/templatefive.jpg')
	template = cv2.pyrDown(template)
	template = cv2.pyrDown(template)
	dicetemplates.append(template)
	template=cv2.imread('dicetest/white/templatesix.jpg')
	template = cv2.pyrDown(template)
	template = cv2.pyrDown(template)
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
img = cv2.imread('dicetest/white/white2cropped.jpg', -1)
img = cv2.pyrDown(img)
img = cv2.pyrDown(img)

refPt = []	

isodiceimg,mask = removeBackground(img,HSV_ORANGE,hadjustlow=10,hadjusthigh=10)

dicearray,rects=isolateDice(isodiceimg,img)
templates = getTemplates()
templates = completeTemplates(templates)
dicevals=discernDice(templates,dicearray,img)
drawDiceVals(dicevals,rects,img)
cv2.imshow('image',img)

cv2.namedWindow("image")
cv2.setMouseCallback("image",clickColor)

cv2.waitKey(0)
cv2.destroyAllWindows()
