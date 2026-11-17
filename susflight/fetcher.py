# Imports csv module, path, json, and math modules
import csv
from math import radians, sin, cos, sqrt, atan2
from pathlib import Path
from openap import FuelFlow, prop
import json 
RAW = Path(__file__).resolve().parent / 'raw' # Defines the path to the raw folder

# Initializes a list to store airport data
airports = []
changiflights = {}  # Using a dictionary for quick lookup of IATA codes

# Reads data from CSV file in raw folder for all valid airports flying to and from Changi Airport
with open(RAW / 'changiflights.csv', newline = "", encoding = "utf-8") as file:
    for row in csv.DictReader(file):
        changiflights[row['iata']] = row # Store IATA codes in the dictionary for quick lookup

# Reads data from CSV file in raw folder
with open(RAW / 'airports.csv', newline = "", encoding = "utf-8") as file:
    for row in csv.DictReader(file):
        if row['iata_code'] in changiflights:
            airports.append(row)

# Computes haversine distance between Singapore and an airport
def haversine(lat2, lon2):
    R = 6371.0  # Radius of the Earth in kilometers

    latsg_rad = radians(1.3644)  # Latitude of Singapore
    lonsg_rad = radians(103.9915)  # Longitude of Singapore
    lat2_rad = radians(lat2)
    lon2_rad = radians(lon2)

    dlon = lon2_rad - lonsg_rad
    dlat = lat2_rad - latsg_rad

    a = sin(dlat / 2)**2 + cos(latsg_rad) * cos(lat2_rad) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    return distance

def aircraft_type(distance):
    if distance < 3000:
        return "A320"
    elif distance < 9000:
        return "B789"
    else:
        return "A359"

# Initializes fuel flow data for each aircraft type
seats = {"A320": 180, "B789": 250, "A359": 300}  # Number of seats for each aircraft type
fuels = {"A320": 800, "B789": 2000, "A359": 2000}
persontocargo = {"A320": 0.9, "B789": 0.8, "A359": 0.8}  # Assumes values for passenger share of payload for each aircraft type
cruise = {"A320": (450, 35000), "B789": (488, 39000), "A359": (488, 39000)} # Typical cruise speed in knots and altitude in feet for each aircraft type

# Calculates total fuel consumption for a trip based on aircraft type and distance
def trip(aircraft, distance):
    speed, altitude = cruise[aircraft]
    mass = 0.8 * prop.aircraft(aircraft) ["mtow"]  # Assumes 80% of maximum takeoff weight for every trip
    fuelflow = FuelFlow(aircraft).enroute(mass = mass, tas=speed, alt=altitude)
    hours = distance / (speed * 1.852)  # Convert speed from knots to km/h
    return float(fuelflow) * hours * 3600 + fuels[aircraft]  # Total fuel consumption in kilograms   

# Calculates CO2 emissions per passenger for each aircraft type based on distance and load factor
def co2perguy(aircraft, distance):
    totalemissions = trip(aircraft, distance)  # Total emissions for the trip
    return (totalemissions * 3.16 * persontocargo[aircraft]) / (seats[aircraft] * 0.8)  # Returns CO2 emissions per passenger cuz 1 kg of fuel burned produces 3.16 kg of CO2, and load factor is assumed to be 0.8 for all aircraft

# Loops through the list of airports and calculates the distance from Singapore for each airport
for airport in airports:
    lat = float(airport['latitude_deg'])
    lon = float(airport['longitude_deg'])
    distance = haversine(lat, lon)
    airport['distance_from_singapore'] = distance
    airport['aircraft_type'] = aircraft_type(distance)

# Finalizes routes to and from Changi Airport
routes = []
for airport in airports:
    routes.append({
        'iata_code': airport['iata_code'],
        'airport': airport['name'],
        'city': changiflights[airport['iata_code']]['city'],
        'country': airport['iso_country'],
        'saf_band': changiflights[airport['iata_code']]['saf_band'],  
        'airlines': changiflights[airport['iata_code']]['airlines'],
        'latitude': float(airport['latitude_deg']),
        'longitude': float(airport['longitude_deg']),
        'distance_from_singapore': round(airport['distance_from_singapore'], 2),
        'aircraft': airport['aircraft_type'],
        'co2_per_passenger': round(co2perguy(airport['aircraft_type'], airport['distance_from_singapore']), 2)
    })

# Writes the finalized routes to a JSON file in the raw folder
DATA = Path(__file__).resolve().parent / 'data'  # Defines the path to the data folder
with open(DATA / 'routes.json', 'w', encoding='utf-8') as json_file:
    json.dump(routes, json_file, ensure_ascii=False, indent=4)

