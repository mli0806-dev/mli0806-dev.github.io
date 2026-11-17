# Imports csv module, path, json, and math modules
import csv
from math import radians, sin, cos, sqrt, atan2
from pathlib import Path
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

# Loops through the list of airports and calculates the distance from Singapore for each airport
for airport in airports:
    lat = float(airport['latitude_deg'])
    lon = float(airport['longitude_deg'])
    distance = haversine(lat, lon)
    airport['distance_from_singapore'] = distance

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
        'distance_from_singapore': round(airport['distance_from_singapore'], 2)
    })

# Writes the finalized routes to a JSON file in the raw folder
DATA = Path(__file__).resolve().parent / 'data'  # Defines the path to the data folder
with open(DATA / 'routes.json', 'w', encoding='utf-8') as json_file:
    json.dump(routes, json_file, ensure_ascii=False, indent=4)