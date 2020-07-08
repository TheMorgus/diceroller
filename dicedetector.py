import cv2
import numpy as np
import sys

ORANGE = np.uint8([[[0,140,255]]])
HSV_ORANGE = cv2.cvtColor(ORANGE, cv2.COLOR_BGR2HSV)
print(HSV_ORANGE)

img = cv2.imread('dicetestingimage.jpg', -1)

hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

lower_background = np.array([6,50,50])
upper_background = np.array([26,255,255])

mask = cv2.inRange(hsv, lower_background, upper_background)
mask = cv2.bitwise_not(mask)

res = cv2.bitwise_and(img,img,mask=mask)
#cv2.imshow('image',hsv)
#cv2.imshow('image',mask)
#cv2.imshow('image',res)


np.set_printoptions(threshold=sys.maxsize)
print(res[1])

cv2.waitKey(0)
cv2.destroyAllWindows()
