from datetime import datetime, timedelta
import RPi.GPIO as GPIO
import requests, smtplib, atexit, time
import threading

#global vars
gpioPins = [7, 11, 15, 12, 16, 22]
gpioLastPinState = [0,0,0,0,0,0]
looneyPins = [gpioPins[0], gpioPins[1], gpioPins[2]]
vampirePins = [gpioPins[3], gpioPins[4], gpioPins[5]]
foodItemIds = [1111,2222,3333]
foodItems = ["Bicky","PartyMix","Ice Tea"]
timeOut = 0.3
looney = ["looney", "password", datetime.now()-timedelta(seconds=timeOut),0]
vampire = ["VampireKid", "password", datetime.now()-timedelta(seconds=timeOut),0]

#fuctions
def exit_handler():
    GPIO.cleanup()

def executeOrder(person, foodItemIndex):
    print("placing order 1x {0:10} for {1:10} at {2}".format(foodItems[foodItemIndex], person[0], str(datetime.now())))
    thread = threading.Thread(target=sendRequest,args=[person[0],person[1],foodItemIds[foodItemIndex]])
    thread.start()

def sendRequest(loginName,loginPassword,foodItemId):
        #requestsSession = Requests.session()
        #requestsSession.Post("URL", data={'usernameformdata': person[0],
        #                               'usernameformdata': person[1],
        #                               'usernameformdata': "Login"})
        #requestsSession.Post("URL", data={})
        #
        ##Feedback/Logging (email,buzzer,logFile,...)
    print("Order placed  1x {0:10} for {1:10} at {2}".format(foodItems[foodItemIds.index(foodItemId)],loginName,str(datetime.now())))

def pinTriggered(pin):
    person = None
    foodItemIndex = None
    if pin in looneyPins:
        person = looney
        foodItemIndex = looneyPins.index(pin)
    elif pin in vampirePins:
        person = vampire
        foodItemIndex = vampirePins.index(pin)

    if (not(foodItemIndex == person[3])) or (person[2] < datetime.now()-timedelta(seconds=timeOut)):
        person[2] = datetime.now()
        person[3] = foodItemIndex
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
            #print("{0:3} + 1 for pin: {1}".format(str(gpioLastPinState[gpioPins.index(pin)]),str(pin)))
            if gpioLastPinState[gpioPins.index(pin)] == debounceValue:
                pinTriggered(pin)
        else:
            if gpioLastPinState[gpioPins.index(pin)] > debounceValue:
                gpioLastPinState[gpioPins.index(pin)] = -debounceValue
            elif gpioLastPinState[gpioPins.index(pin)] < 0:
                gpioLastPinState[gpioPins.index(pin)] += 1
            else:
                gpioLastPinState[gpioPins.index(pin)] = 0

