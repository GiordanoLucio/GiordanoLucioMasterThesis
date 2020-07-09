import sensor,image,lcd,time
import KPU as kpu
import urequests

# modules for the connection
import usocket, network, time
import lcd, image
from Maix import GPIO
from machine import UART
from fpioa_manager import fm, board_info

lcd.init(freq=15000000)
#sensor.reset()
sensor.reset(dual_buff=True)#to double fps in exchange of an increase usage of RAM

sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time = 2000)     # Wait for settings take effect.
sensor.set_windowing((224, 224))
sensor.run(1)

classes = ["person"]

tinyYolo = "/sd/models/tinyYoloMerged.kmodel" #16 fps
mbnet75 = "/sd/models/mbnet75Merged.kmodel" #12 fps
mbnet50 = "/sd/models/mbnet50Merged.kmodel" #15fps
mbnet25 = "/sd/models/mbnet25Merged.kmodel" #16fps

task=kpu.load(mbnet50)

try:
    kpu.netinfo(task)
except:
    print("cannot get net info, kmodel v4 not supported for netinfo!")

lastLayerShape=(len(classes)+5)*5
#from documentation Kmodel V4 need set output shape manually
a = kpu.set_outputs(task, 0, 7,7,lastLayerShape)
anchor = (0.57273, 0.677385, 1.87446, 2.06253, 3.33843, 5.47434, 7.88282, 3.52778, 9.77052, 9.16828) #yolo v2 tiny



# for new MaixGO board, if not, remove it
fm.register(0, fm.fpioa.GPIOHS1, force=True)
wifi_io0_en=GPIO(GPIO.GPIOHS1, GPIO.OUT)
wifi_io0_en.value(0)

# En SEP8285
fm.register(8, fm.fpioa.GPIOHS0, force=True)
wifi_en=GPIO(GPIO.GPIOHS0,GPIO.OUT)
fm.register(board_info.WIFI_RX,fm.fpioa.UART2_TX, force=True)
fm.register(board_info.WIFI_TX,fm.fpioa.UART2_RX, force=True)

def wifi_enable(en):
    global wifi_en
    wifi_en.value(en)

def wifi_reset():
    global uart
    wifi_enable(0)
    time.sleep_ms(200)
    wifi_enable(1)
    time.sleep(2)

    uart = UART(UART.UART2,115200,timeout=1000, read_buf_len=4096)
    tmp = uart.read()
    uart.write("AT+UART_CUR=921600,8,1,0,0\r\n")
    print(uart.read())
    uart = UART(UART.UART2,921600,timeout=1000, read_buf_len=10240) # important! baudrate too low or read_buf_len too small will loose data
    uart.write("AT\r\n")
    tmp = uart.read()
    print(tmp)
    if not tmp.endswith("OK\r\n"):
        print("reset fail")
        return None
    try:
        nic = network.ESP8285(uart)
    except Exception:
        return None
    return nic

nic = wifi_reset()
thingSpeakKey= ""
if not nic:
    raise Exception("WiFi init fail")
try:
    wifi_password=""
    nic.connect("SANBERNARDO",wifi_password)
except:
    print('connection failed')



def doOverlap(boxDict,box1Dict):
    box=boxDict['rect']
    box1=box1Dict['rect']
    print("checking overlapping boxes:", box," ",box1)
    box_x=box[0]
    box_y=box[1]
    box_x2=box[0]+box[2]
    box_y2=box[1]+box[3]

    box1_x=box1[0]
    box1_y=box1[1]
    box1_x2=box1[0]+box1[2]
    box1_y2=box1[1]+box1[3]
    #first box is at the right of the second or the second is at the right of the first
    if(box_x > box1_x2 or box1_x > box_x2):
        return False
    #first box above the second or the second above the first
    if(box_y > box1_y2 or box1_y > box_y2):
        return False
    return True

a = kpu.init_yolo2(task, 0.15, 0.3, 5, anchor)
import random
randomString=(str(random.randint(0,100)))+(str(random.randint(0,100)))

clock = time.clock()
loopCycle=0
totalCollision=0
count=0
personDetected=0
while(True):
    loopCycle += 1
    number_of_person=0
    countCollision=0
    count+=1
    people=[]
    peopleCoordinates={}
    clock.tick()
    img = sensor.snapshot()
    a = img.pix_to_ai()
    code = kpu.run_yolo2(task, img)
    fps=(clock.fps())
    # print(fps) #uncomment to show fps
    boxes = []
    overlappingBoxes=[]
    notOverlapping=[]
    if code:
        #code contains a list of dict with the predictions
        for i in code:
            number_of_person+=1
            box = i.rect()
            element={'rect':box,'collide':False}
            boxes.append(element)
        #check if boxes overlap
        if (len(boxes) > 1):
            print("found ", len(boxes), " boxes")
            for i in range (0,len(boxes)-1):
                #print("checking box: ", i)
                for j in range(i+1,len(boxes)):
                    print("checking box: ", j)
                    if(doOverlap(boxes[i],boxes[j])):
                        print("Collision detected!!")
                        boxes[i]['collide']=True
                        boxes[j]['collide']=True
                        countCollision+=1
                        totalCollision+=1
        for i in boxes:
            #print("box properties: ", i)
            if i['collide'] == True:
                a=img.draw_rectangle(i['rect'],color=(255,0,0))
            else:
                a=img.draw_rectangle(i['rect'],color=(0,255,0))
        if countCollision>0:
            print("saving image!!")
            imgName="collision"+randomString+"_"+str(count)
            imgPath='/sd/img_collisions/mbnet0.5_'+imgName+'.jpg'
            try:
                img.save(imgPath)
            except:
                print("failed to save")
        a = lcd.display(img)
    else:
        a = lcd.display(img)
    personDetected += number_of_person
    """
    if personDetected > maximum:
        #maximum is calculated but not used in this version
        maximum = personDetected
    """
    if loopCycle%100==0:
        print("now sending...")
        mediumValue = personDetected/loopCycle
        personDetected=0
        loopCycle=0
        print("medium value: ",mediumValue, " & totalCollisions: ",totalCollision)
        #print("invio richiesta", x)
        #thingSpeakKey= "ADD_KEY_HERE"
        url = "http://api.thingspeak.com/update?api_key="+thingSpeakKey+"&field1=%.2f&field2=%.2f" %(mediumValue,totalCollision)
        r = urequests.get(url)
        totalCollision=0
        #print(r.content)
        r.close()
a = kpu.deinit(task)
