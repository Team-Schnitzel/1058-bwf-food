from datetime import datetime, timedelta
import RPi.GPIO as GPIO
import requests, smtplib, atexit, time, threading, json, bs4

#global vars
settings = json.load(open('settings.JSON'))
headers = {'content-type': 'application/x-www-form-urlencoded'}
PostUrl = "https://pos.bwf.be/"

#fuctions
def exit_handler():
    GPIO.cleanup()

def getFoodItemsString(foodItemIds):
    returnString = ""
    for foodItemId in foodItemIds:
        if len(returnString) > 0:
            returnString += ", "
        returnString += "1x " + settings["food"][str(foodItemId)]
    return returnString

def logToFile(person,foodItemIds):
    with open("Log.txt", "a") as file:
        file.write("Order placed  1x {0:10} for {1:10} at {2}".format(getFoodItemsString(foodItemIds),person["Username"],str(datetime.now())) + "\n")

def sendRequest(person,foodItemIds):
    requestsSession = requests.session()
    postData = {"username": person["Username"], "password": person["Password"], "login": "Aanmelden"}
    requestsSession.post(PostUrl, headers=headers, data=postData, verify=False)
    for foodItemId in foodItemIds:
        postData = {"order_item": str(foodItemId), "order_item_add": "Voeg Toe"}
        requestsSession.post(PostUrl, headers=headers, data=postData, verify=False)
    postData = {"opmerkingen":person["OrderMessage"] , "user_order_start_print": "Plaats Bestelling"}
    order_response = requestsSession.post(PostUrl, headers=headers, data=postData, verify=False).content
    remaining_credits = bs4.BeautifulSoup(order_response, 'html.parser').find('div', {'id': 'account'}).find('span').text

    logToFile(person,foodItemId)
    print("Order placed {0:10} for {1:10} at {2}".format(getFoodItemsString(foodItemIds),person["Username"],str(datetime.now())))
    print(person[0] + " now has " + remaining_credits + " remaining")

def executeOrder(user, foodItemID):
    print("placing order {0:10} for {1:10} at {2}".format(getFoodItemsString(foodItemIds), user["Username"], str(datetime.now())))
    thread = threading.Thread(target=sendRequest,args=[person,foodItemIDs])
    thread.start()

def pinTriggered(user,pin):
    foodItemIndex = user["gpioPins"].index(pin)
    foodItemIDs = user["foodItemIds"][foodItemIndex]
    executeOrder(user, foodItemIDs)

#start
atexit.register(exit_handler)
GPIO.setmode(GPIO.BOARD)
gpioLastPinState = None
for user in settings["Users"]:
    for pin in user["gpioPins"]:
        GPIO.setup(pin, GPIO.IN)
        gpioLastPinState[pin] = 0
print(str(gpioLastPinState))
debounceValue = 100

print("running")
while True:
    for user in settings["Users"]:
        for pin in user["gpioPins"]:
            if (GPIO.input(pin)):
                if gpioLastPinState[pin] <= debounceValue:
                    gpioLastPinState[pin] += 1
                if gpioLastPinState[pin] == debounceValue:
                    pinTriggered(user,pin)
            else:
                gpioLastPinState[pin] = 0
