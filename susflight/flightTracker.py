import pandas as pd

largest_flight_num = float("-inf")
list = [101, 202, 303, 404, 505]

def welcomeMessage():
    print("Welcome to Flight Tracker!")

welcomeMessage()

for flight in list:
    if flight > largest_flight_num:
        largest_flight_num = flight
print ("The largest flight number is: " + str(largest_flight_num))
