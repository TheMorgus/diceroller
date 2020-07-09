import cv2
import numpy as np
#import sys

ORANGE = np.uint8([[[0,140,255]]])
HSV_ORANGE = cv2.cvtColor(ORANGE, cv2.COLOR_BGR2HSV)
print(HSV_ORANGE[0,0,0])

def removeBackground(image, bgcolor,hadjustlow=10,slow=50,vlow=50,\
	hadjusthigh=10,shigh=255,vhigh=255):
	imagehsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
	h = bgcolor[0,0,0]
	s = bgcolor[0,0,1]
	v = bgcolor[0,0,2]
	
	low_background = np.array([h-hadjustlow,slow,vlow])
	high_background = np.array([h+hadjusthigh,shigh,vhigh])
	mask = cv2.inRange(imagehsv, low_background, high_background)
	mask = cv2.bitwise_not(mask)
	res = cv2.bitwise_and(img,img,mask=mask)
	
	#Basic filtering and noise reduction
	kernel = np.ones((5,5),np.float32)/25
	res = cv2.filter2D(res,-1,kernel)
	kernel = np.ones((5,5),np.uint8)
	res = cv2.morphologyEx(res, cv2.MORPH_OPEN,kernel)
	
	return res

img = cv2.imread('dicetestingimage.jpg', -1)

res = removeBackground(img,HSV_ORANGE,hadjustlow=10,hadjusthigh=10)

res = cv2.pyrDown(res)
cv2.imshow('image',res)

#np.set_printoptions(threshold=sys.maxsize)
#print(res[1])

cv2.waitKey(0)
cv2.destroyAllWindows()
