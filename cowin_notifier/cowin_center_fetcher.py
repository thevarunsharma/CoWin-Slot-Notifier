#!/usr/bin/env python3

import re
import requests
from diskcache import FanoutCache

# headers needed to be supplied with requests to avoid 403 error
headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
        'TE': 'Trailers'
        }

cache = FanoutCache(directory=".cached", timeout=1)

def fetch_centers_by_pincode(pincode: str, 
                             date: str) -> dict:
    """
    Returns a dictionary of all available centers and related info based on pincode and date supplied as arguments
    
    Arguments
    -------------
    pincode: area pincode to be searched
    date: start date in DD-MM-YYYY format for search results
    """

    url = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/findByPin"
    params = {
            "pincode" : pincode,
            "date": date
            }

    req = requests.get(url, 
                       params=params,
                       headers=headers)

    req.raise_for_status()
    return req.json().get('sessions')



@cache.memoize()
def fetch_states() -> list:
    """
    Returns a list of all states and union territories along with their state_id's
    """

    url = "https://cdn-api.co-vin.in/api/v2/admin/location/states/"
    
    req = requests.get(url,
                       headers=headers)
    
    req.raise_for_status()
    return req.json().get('states')


@cache.memoize()
def fetch_state_id(state: str) -> int:
    """
    Returns an integer denoting state_id for the state name supplied as argument

    Argument
    -------------
    state: name of state for which state_id is to be fetched
    """
    
    # regex pattern match state name with values in list
    pattern = re.compile(r"^" + r"\s*".join(state.lower().split()) + r".*")
    
    states = fetch_states()
    for entry in states:
        state_id = entry.get("state_id")
        state_name = entry.get("state_name").lower().strip()

        if pattern.match(state_name):
            return state_id

    raise ValueError(f"No match found for state '{state}'")


@cache.memoize()
def fetch_districts(state_id: int) -> list:
    """
    Returns a list of all districts_name's and district_id's for the state_id supplied as argument

    Argument
    -------------
    state_id: integer denoting state_id for state for which districts are to be searched
    """

    url = f"https://cdn-api.co-vin.in/api/v2/admin/location/districts/{state_id}"
    
    req = requests.get(url,
                       headers=headers)
    
    req.raise_for_status()
    return req.json().get("districts")


@cache.memoize()
def fetch_district_id(district: str,
                      state: str) -> int:
    """
    Returns an integer denoting district_id based on district name and state name supplied as arguments

    Arguments
    -------------
    district: name of district whose id is to be fetched
    state: name of state where district is situated
    """

    # regex pattern to match with district names in list
    pattern = re.compile(r"^" + r"\s*".join(district.lower().split()) + r".*")
    
    state_id = fetch_state_id(state)
    districts = fetch_districts(state_id)
    for entry in districts:
        district_id = entry.get("district_id")
        district_name = entry.get("district_name").lower().strip()
        
        if pattern.match(district_name):
            return district_id

    raise ValueError(f"No match found for district '{district}' in state '{state}'")


def fetch_centers_by_district_id(district_id: int,
                                 date:str) ->list:
    """
    Returns a list of all available centers and related info based on district_id and date supplied as arguments

    Arguments
    -------------
    district_id: number denoting district id for the district to be searched
    date: start date in DD-MM-YYYY format for search results
    """

    url = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/findByDistrict"
    params = {
            "district_id": district_id,
            "date": date
            }

    req = requests.get(url,
                       params=params,
                       headers=headers)

    req.raise_for_status()
    return req.json().get('sessions')


def fetch_centers_by_district_state(district: str,
                                    state: str,
                                    date: str) -> list:
    """
    Returns a list of all available centers and related info based on district, state and date supplied as arguments

    Arguments
    -------------
    district: name of district to be searched
    state: name of state where district is situated
    date: start date in DD-MM-YYYY format for search results
    """

    district_id = fetch_district_id(district, state)
    return fetch_centers_by_district_id(district_id, date)

