# Untitled - By: Utente - mer apr 22 2020

import sensor, image, time
lcd.init(freq=15000000)
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time = 2000)
sensor.set_windowing((224, 224))
import random
sensor.set_vflip(3)
#simply create a random number to name the images
count=1.23*random.randint(0,10000)
import random

randomString=str(random.randint(0,1000))
print(randomString)
while 1:
    img = sensor.snapshot()
    lcd.display(img)
    imgName="rand"+randomString+str(count)
    imgPath='/sd/imgs_validation/dataset_'+imgName+'.jpg'
    img.save(imgPath)
    print(imgPath)
    count+=1
    time.sleep(3)

