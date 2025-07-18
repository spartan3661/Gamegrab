import easyocr
import cv2
reader = easyocr.Reader(['ja','en']) # this needs to run only once to load the model into memory
result = reader.readtext('image.png')
filtered = [res for res in result if res[2] > 0.9]
image = cv2.imread('image.png')

for test in result:
    print(test)
    #bbox = test[0][1]
    cv2.rectangle(image, (test[0][0][0], test[0][0][1]), 
                  (test[0][2][0], test[0][2][1]), 
                  (0,255,0), 2)
    print("\n")
    
cv2.imwrite("output.png", image)