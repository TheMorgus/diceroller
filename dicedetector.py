import cv2
import numpy as np
#import sys

ORANGE = np.uint8([[[0,140,255]]])
HSV_ORANGE = cv2.cvtColor(ORANGE, cv2.COLOR_BGR2HSV)

def removeBackground(image, bgcolor,hadjustlow=10,slow=50,vlow=50,\
	hadjusthigh=10,shigh=255,vhigh=255):
	imagehsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
	h = bgcolor[0,0,0]
	#s = bgcolor[0,0,1]
	#v = bgcolor[0,0,2]
	
	low_background = np.array([h-hadjustlow,slow,vlow])
	high_background = np.array([h+hadjusthigh,shigh,vhigh])
	mask = cv2.inRange(imagehsv, low_background, high_background)
	mask = cv2.bitwise_not(mask)
	res = cv2.bitwise_and(img,img,mask=mask)
	_,res22=cv2.threshold(res,5,255,cv2.THRESH_BINARY)
	#Basic filtering and noise reduction
	#kernel = np.ones((5,5),np.float32)/25
	#res = cv2.filter2D(res,-1,kernel)
	#kernel = np.ones((5,5),np.uint8)
	#res = cv2.morphologyEx(res, cv2.MORPH_OPEN,kernel)
	return res22
def showDiceArea(image):
	img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	ret,thresh=cv2.threshold(image,1,255,cv2.THRESH_BINARY)
	return thresh
def revealSymbols(image, symbolcolor,hadjustlow=10,slow=50,vlow=50,\
	hadjusthigh=10,shigh=255,vhigh=255):
	imagehsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
	h = symbolcolor[0,0,0]
	#s = bgcolor[0,0,1]
	#v = bgcolor[0,0,2]
	
	low_background = np.array([100,10,110])
	high_background = np.array([135,55,185])
	mask = cv2.inRange(imagehsv, low_background, high_background)
	#mask = cv2.bitwise_not(mask)
	res = cv2.bitwise_and(image,image,mask=mask)
	#Basic filtering and noise reduction
	#kernel = np.ones((5,5),np.float32)/25
	#res = cv2.filter2D(res,-1,kernel)
	#kernel = np.ones((5,5),np.uint8)
	#res = cv2.morphologyEx(res, cv2.MORPH_OPEN,kernel)
	
	return res
refPt = []
def filterImage(img):
	kernel = np.ones((5,5),np.float32)/25
	res = cv2.filter2D(img,-1,kernel)
	kernel = np.ones((5,5),np.uint8)
	res = cv2.morphologyEx(img, cv2.MORPH_OPEN,kernel)
	return res
	
def clickColor(event, x, y, flags, param):
	global refPt
	global img
	if event == cv2.EVENT_LBUTTONDOWN:
		refPt=[(x,y)]
		print(refPt)
		print(res[y,x])
		
img = cv2.imread('dicetestingimage.jpg', -1)
template=cv2.imread('dicetemplatefive.jpg')
#img = filterImage(img)

res = removeBackground(img,HSV_ORANGE,hadjustlow=10,hadjusthigh=10)

#res = revealSymbols(img,HSV_ORANGE)
#res=filterImage(res)
#res = showDiceArea(res)
#res=filterImage(res)

gray = cv2.cvtColor(res,cv2.COLOR_BGR2GRAY)
res = cv2.Canny(gray,500,1000,apertureSize=3) #EDGES
kernel=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(9,9))
res=cv2.dilate(res,kernel)
ret,thresh=cv2.threshold(res,5,255,cv2.THRESH_BINARY)
_,contours,_=cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
contours2=[]
for cnt in contours:
	#print(cv2.contourArea(cnt))
	if(cv2.contourArea(cnt)>7800)and(cv2.contourArea(cnt)<8700):
		contours2.append(cnt)
warped=[]
for cnt in contours2:
	print(cv2.contourArea(cnt))	
	rect=cv2.minAreaRect(cnt)
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
#cv2.drawContours(img,contours2,-1,(30,100,100),3)

"""


w,h,_=template.shape
increment=5

min_val=[]
max_val=[]
min_loc=[]
max_loc=[]

for x in range(int(360/increment)):
	print(x)
	m=cv2.getRotationMatrix2D((h/2,w/2),x*increment,1)
	templatetemp=cv2.warpAffine(template,m,(h,w))
	im=cv2.matchTemplate(res,templatetemp,cv2.TM_SQDIFF)
	minval,maxval,minloc,maxloc=cv2.minMaxLoc(im)
	min_val.append(minval)
	max_val.append(maxval)
	min_loc.append(minloc)
	max_loc.append(maxloc)
#m=cv2.getRotationMatrix2D((h/2,w/2),35,1)
#template=cv2.warpAffine(template,m,(h,w))
#res=cv2.matchTemplate(res,template,cv2.TM_SQDIFF)
#min_val,max_val,min_loc,max_loc=cv2.minMaxLoc(res)

minimum=min(min_val)
index=min_val.index(minimum)
print(index)
top_left=min_loc
bottom_right=(top_left[0]+w,top_left[1]+h)
cv2.rectangle(img,top_left,bottom_right,255,2)
"""
#img = cv2.pyrDown(img)
a=revealSymbols(warped[4],HSV_ORANGE)
res=cv2.cvtColor(a,cv2.COLOR_BGR2GRAY)
ret,thresh=cv2.threshold(res,5,255,cv2.THRESH_BINARY)
cv2.imshow('image',thresh)

cv2.namedWindow("image")
cv2.setMouseCallback("image",clickColor)

#np.set_printoptions(threshold=sys.maxsize)
#print(res[1])

cv2.waitKey(0)
cv2.destroyAllWindows()
