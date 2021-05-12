#!/usr/bin/env python3

import datetime
import diskcache
from .cowin_center_fetcher import fetch_centers_by_district_state, fetch_centers_by_pincode

CACHE_EXPIRATION_TIME = 60 * 60 * 6        # 6 hours 

def get_ist_date(offset: int = 12) -> str:
    """
    Return date in Indian Standard timezone
    
    Arguments
    -----------
    offset: number of hours to add to current time, default=12 
    """
    # Indian Standard Timezone UTC +05:30
    ist_timezone = datetime.timezone(
        datetime.timedelta(hours=5, minutes=30)
    )
    # current date
    date = datetime.datetime.now(ist_timezone)
    # offset
    offset_delta = datetime.timedelta(hours=offset)
    date = date + offset_delta
    # return date formatted as DD-MM-YYYY
    return date.strftime("%d-%m-%Y")

def get_available_slots(date: str, 
                        pincode: str = None, 
                        state: str = None, 
                        district: str = None,
                        age_group: int = 45) -> dict:
    if pincode:
        centers = fetch_centers_by_pincode(pincode, date)
        available = {"area" : {
            "Pincode": pincode
            }}
    elif state and district:
        centers = fetch_centers_by_district_state(district, state, date)
        available = {"area" : {
            "District": district,
            "State": state
            }}
    else:
        raise ValueError("Either 'pincode' or both 'state' and 'district' need to be passed")
    
    info = available["centers"] = {}
    for center in centers:
        center_id = center['center_id']
        center_name = center['name']
        center_address = ", ".join([
            center['address'],
            center['district_name'], 
            center['state_name'],
            f"Pincode: {center['pincode']}"
            ])
        fee_mode = center['fee_type']
        available_capacity = center['available_capacity']
        age_limit = center['min_age_limit']
        vaccine = center['vaccine']
        if available_capacity > 0 and age_limit <= age_group:
            if center_id not in info:
                info[center_id] = {
                        "name": center_name,
                        "address": center_address,
                        "fee_mode": fee_mode,
                        "date": center['date'],
                        "available_capacity": available_capacity,
                        "age_limit": age_limit,
                        "vaccine": vaccine,
                        "slots": center['slots']
                    }
    return available

def get_diff_value(available: dict,
                   cache: diskcache.Cache,
                   date: str,
                   pincode: str = None,
                   state: str = None,
                   district: str = None,
                   age_group: int = 45) -> dict:

    """
    Returns the difference in value from cached value if present otherwise the newly fetched value. 
    Also, updates the cache with the newly fetched 
    """
    # use the fetch-arguments as key
    key = (date, pincode, state, district, age_group)
    fetched_centers = available['centers']
    cached_centers = cache.get(key)

    # update cache
    cache.set(key, fetched_centers, expire=CACHE_EXPIRATION_TIME)
    
    if cached_centers is None and fetched_centers:
        return fetched_centers
    
    # difference to be returned to the user
    diff_centers = {}
    for center_id, value in fetched_centers.items():
        if center_id in cached_centers:
            # search difference in similar values
            cached_value = cached_centers[center_id]
            if cached_value['date'] == value['date'] \
            and cached_value['age_limit'] == value['age_limit'] \
            and cached_value['vaccine'] == value['vaccine']:
                # if same slot found but more capacity
                if cached_value['available_capacity'] < value['available_capacity']:
                    diff_centers[center_id] = value
            
            else:
                diff_centers[center_id] = value
        else:
            diff_centers[center_id] = value

    return diff_centers if diff_centers else None
