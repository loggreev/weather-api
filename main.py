# exiting program
import sys
# checking for existing file path
import os.path
# reading from config file
import configparser
# parsing json files
import json
# http requests
import requests
# pattern search
import re
# utility functions
import utils
# pyowm is a python wrapper for OpenWeatherMap API
import pyowm

# config file to store api key
config_file_name = 'config.ini'

# check for existing config file
# if it does not exist, create it
if not os.path.exists(config_file_name):
    f = open(config_file_name, 'w')
    f.close()

# read api key from config file
# if key does not yet exist, ask user for it and add it to the file
with open(config_file_name, 'r+') as f:
    # conifgparser object for easy reading/writing of configuration files
    config = configparser.ConfigParser()
    
    # config file must be valid
    try:
        if not config.read(config_file_name):
            raise configparser.NoSectionError
    except (configparser.MissingSectionHeaderError, configparser.NoSectionError):
        print(f'Invalid config file. Please delete {config_file_name} and restart the program.')
        sys.exit()
    
    # if api key exists in config, get it
    # otherwise, ask user for key and then write it to the file
    try:
        api_key = config.get('DEFAULT', 'api_key')
    except configparser.NoOptionError:
        api_key = input('Please enter an API key: ')
        config.set('DEFAULT', 'api_key', api_key)
        config.write(f)

# initialize api module
owm = pyowm.OWM(api_key)
# object used to find specific city ids
cities = owm.city_id_registry()
# base url for api requests
api_url = 'https://api.openweathermap.org/data/2.5/'

def main():
    while True:
        options = ['Use PyOWM module','Standard HTTP request','Exit program']
        print('\nHow do you want to use the API?')
        choice = utils.get_choice(options)
        if choice == options[0]:
            use_module = True
        elif choice == options[1]:
            use_module = False
        elif choice == options[2]:
            sys.exit()
        
        # get a module or json response from api
        response = api_call(use_module)
        
        if response == None:
            continue
        
        # using module to parse data
        if use_module:
            print("\nThe current weather at the given coordinates:")
            print('Status: ' + str(response.detailed_status))
            print('Temperature: ' + str(response.temperature('fahrenheit')['temp']) + ' degrees Fahrenheit')
            print('Cloud coverage: ' + str(response.clouds) + '%')
            print('Wind: ' + str(response.wind()['speed']) + 'm/s at ' + str(response.wind()['deg']) + ' degrees')
            print('Humidity: ' + str(response.humidity) + '%')
        # using json to parse data
        else:
            # write json response to a file
            with open('results.json','w') as results_file:
                # converts the response dictionary to a json object
                formatted_json = json.loads(json.JSONEncoder().encode(response))
                json.dump(formatted_json, results_file, indent = 4)
        
# use api call to get specific weather data
# returns data response
def api_call(use_module):
    coords = None
    while coords == None:
        coords = get_coords()
    lat = coords[0]
    lon = coords[1]
    
    exclude = None
    units = None
    lang = None
    # not used for the module
    if not use_module:
        exclude = get_exclude()
        units = get_units()
        lang = get_lang()
    
    if use_module:
        mgr = owm.weather_manager()
        observation = mgr.weather_at_coords(lat,lon)
        return observation.weather
    else:
        # example url:
        # https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&exclude={part}&appid={API key}
        
        # dictionary of parameters to use
        data = {'lat':lat,'lon':lon,'exclude':exclude,'units':units,'lang':lang, 'appid':api_key}
        # request url with given parameters
        request_url = api_url + 'onecall'
        r = requests.get(request_url, params=data)
        # get json from response
        json = r.json()
        return json

# get latitude and longitude from user and returns them
def get_coords():
    options = ['Latitude & Longitude','City Name']
    print('\nChoose a method for entering a location.')
    choice = utils.get_choice(options)
    # latitude/longitude entry
    if choice == options[0]:
        lat = input('Enter latitude: ')
        lon = input('Enter longitude: ')
        try:
            lat = float(lat)
            lon = float(lon)
        except ValueError:
            print('Invalid coordinates.')
            return None
        return [lat,lon]
    # try to obtain latitude/longitude by a unique city name
    elif choice == options[1]:
        city_name = input('Enter city name: ')
        locations = cities.locations_for(city_name)
        # city name is not unique
        if len(locations) > 1:
            # print coordinates of cities with the given name
            print('Too many cities have this name. Choose a different option.')
            print('Here are the locations found:')
            print('id, latitude, longitude')
            for city in locations:
                print(f'{city.id}, {city.lat}, {city.lon}')
            return None
        # city not found
        elif len(locations) == 0:
            print('No cities found by this name. Choose a different option.')
            return None
        # exact city match found
        else:
            city = locations[0]
            return [city.lat, city.lon]
            
# returns a ready-to-use string representing whether or not the api call should exclude certain data
def get_exclude():
    exclude = []
    options = ['current', 'minutely', 'hourly', 'daily', 'alerts', 'Return']
    while options:
        print('\nSelect any types of weather data to exclude from the API call.\n'
              'Choose the Return option once you are done.')
        choice = utils.get_choice(options)
        if choice == 'Return':
            break
        exclude.append(choice)
        options.remove(choice)
        
    # separate choices by comma except last one
    exclude_str = ''
    for data in exclude:
        exclude_str += data + ','
    exclude_str = exclude_str[:-1]
    if exclude_str == '':
        return None
    else:
        return exclude_str
        
# returns a ready-to-use string representing the type of measurement units to use for the api call
def get_units():
    options = ['imperial','metric','standard']
    print('\nChoose the type of measurement units to use.')
    choice = utils.get_choice(options)
    return choice

# returns a ready-to-use string representing the language code to use for the api call
def get_lang():
    lang = input('\nEnter a language code to use. If invalid, English will be used.\n')
    # alphabetic characters and underscores only
    if re.search('[^a-z_]', lang):
        lang = 'en'
    elif lang == '':
        lang = 'en'
    return lang
            
if __name__ == "__main__":
    main()