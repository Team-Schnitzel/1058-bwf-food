from datetime import datetime, timedelta
import RPi.GPIO as GPIO
import requests, smtplib, atexit, time, threading, json

#global vars
settings = json.load(open('settings.JSON'))
gpioPins = [int(x) for x in settings["gpioPins"]]
gpioLastPinState = [0,0,0,0,0,0]
looneyPins = [gpioPins[0], gpioPins[1], gpioPins[2]]
vampirePins = [gpioPins[3], gpioPins[4], gpioPins[5]]
foodItemIds = [int(x) for x in settings["foodItemIdes"]]
foodItems = settings["foodItemNames"]
looney = [settings["Looney"]["Username"], settings["Looney"]["Password"],settings["Looney"]["Email"]]
vampire = [settings["VampireKid"]["Username"], settings["VampireKid"]["Password"],settings["VampireKid"]["Email"]]
headers = {'content-type': 'application/x-www-form-urlencoded'}
PostUrl = "https://pos.bwf.be/"

#fuctions
def exit_handler():
    GPIO.cleanup()

def executeOrder(person, foodItemIndex):
    print("placing order 1x {0:10} for {1:10} at {2}".format(foodItems[foodItemIndex], person[0], str(datetime.now())))
    #thread = threading.Thread(target=sendRequest,args=[person,foodItemIds[foodItemIndex]])
    #thread.start()

#def sendMail(person,foodItemId):
#    if "@" in person[2]:
#        msg = "Order placed  1x {0:10} for {1:10} at {2}".format(foodItems[foodItemIds.index(foodItemId)],person[0],str(datetime.now()))
#        server = smtplib.SMTP_SSL(settings["smtp"]["Server"],int(settings["smtp"]["Port"]))
#        server.login(settings["smtp"]["Email"],settings["smtp"]["Password"])
#        server.sendmail(settings["smtp"]["Email"], person[2], str(msg))
#        server.quit()
    
def logToFile(person,foodItemId):
    with open("Log.txt", "a") as file:
        file.write("Order placed  1x {0:10} for {1:10} at {2}".format(foodItems[foodItemIds.index(foodItemId)],person[0],str(datetime.now())) + "\n")
    
def sendRequest(person,foodItemId):
    requestsSession = Requests.session()
    postData = {"username": person[0], "password": person[1], "login": "Aanmelden"}
    requestsSession.Post(PostUrl, headers=headers, data=postData)
    time.sleep(1)
    postData = {"order_item":str(foodItemId), "order_item_add": "Voeg Toe"}
    requestsSession.Post(PostUrl, headers=headers, data=postData)
    time.sleep(1)
    PostData = {"opmerkingen":"", "user_order_start_print": "Plaats Bestelling"}
    requestsSession.Post(PostUrl, headers=headers, data=postData)
    
    logToFile(person,foodItemId)
    print("Order placed  1x {0:10} for {1:10} at {2}".format(foodItems[foodItemIds.index(foodItemId)],person[0],str(datetime.now())))

def pinTriggered(pin):
    person = None
    foodItemIndex = None
    if pin in looneyPins:
        person = looney
        foodItemIndex = looneyPins.index(pin)
    elif pin in vampirePins:
        person = vampire
        foodItemIndex = vampirePins.index(pin)
    executeOrder(person, foodItemIndex)

#start
atexit.register(exit_handler)
GPIO.setmode(GPIO.BOARD)
for pin in gpioPins:
    GPIO.setup(pin, GPIO.IN)
debounceValue = 200
while True:
    for pin in gpioPins:
        if (GPIO.input(pin)):
            gpioLastPinState[gpioPins.index(pin)] += 1
            print("{0:3} + 1 for pin: {1}".format(str(gpioLastPinState[gpioPins.index(pin)]),str(pin)))
            if gpioLastPinState[gpioPins.index(pin)] == debounceValue:
                pinTriggered(pin)
        else:
            if gpioLastPinState[gpioPins.index(pin)] > debounceValue:
                gpioLastPinState[gpioPins.index(pin)] = -debounceValue
            elif gpioLastPinState[gpioPins.index(pin)] < 0:
                gpioLastPinState[gpioPins.index(pin)] += 1
            else:
                gpioLastPinState[gpioPins.index(pin)] = 0

