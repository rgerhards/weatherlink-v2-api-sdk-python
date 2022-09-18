import os
import sys
import time
import requests
import json
from datetime import datetime
sys.path.insert(0, "../src/weatherlink_v2_api_sdk/signature")
from signature_calculator import SignatureCalculator
api = SignatureCalculator()


def convert_f_to_c_str(farenheit):
    return str(round(((float(farenheit) - 32) / 1.8), 1))


api_endpoint = "https://api.weatherlink.com/v2/"
api_key = os.environ.get("DAVIS_API_KEY")
api_secret = os.environ.get("DAVIS_API_SECRET")


# get station IDs
timestamp = int(datetime.timestamp(datetime.now()))
api_sig_string = api.calculate_stations_signature(api_key, api_secret, timestamp)

query_params = {
            'api-key': api_key,
            'api-signature': api_sig_string,
            't': str(timestamp)
        }
r = requests.get(api_endpoint + 'stations', params=query_params)
jso = r.json()
# debug output: print(json.dumps(jso, indent=2))
for x in jso["stations"]:
        print(f"station id: {x['station_id']}, Name: {x['station_name']}")
        station_id = int(x['station_id'])

# get history data
from_date = int(datetime.timestamp(datetime.strptime("2022-09-16 00:00:00", "%Y-%m-%d %H:%M:%S")))
to_date = int(datetime.timestamp(datetime.strptime("2022-09-16 18:35:00", "%Y-%m-%d %H:%M:%S")))
timestamp = int(datetime.timestamp(datetime.now()))
 
print(f"Query historic for station {station_id}")
api_sig_string = api.calculate_historic_signature(api_key, api_secret, timestamp,
        station_id, from_date, to_date)

query_params = {
            'api-key': api_key,
            'api-signature': api_sig_string,
            't': str(timestamp),
            'start-timestamp': str(from_date),
            'end-timestamp': str(to_date)
        }
r = requests.get(api_endpoint + 'historic/' + str(station_id), params=query_params)
jso = r.json()
#print(json.dumps(jso, indent=2))


for sensor in jso["sensors"]:
    print(f"sensor id: {sensor['lsid']}, data structure type {sensor['data_structure_type']}")
    if sensor['data_structure_type'] == 4:
        for hist_rec in sensor['data']:
            hist_time = datetime.fromtimestamp(hist_rec['ts']).strftime('%Y-%m-%d %H:%M:%S')
            print(f"insert into readings(time_taken, temp, evapotrans) values ('{hist_time}',{convert_f_to_c_str(hist_rec['temp_out'])}, {hist_rec['et']});")
