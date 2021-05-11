#!/usr/bin/env python3

import datetime
import diskcache
from .cowin_center_fetcher import fetch_centers_by_district_state, fetch_centers_by_pincode

CACHE_EXPIRATION_TIME = 60 * 60 * 6        # 6 hours 

def get_ist_date() -> str:
    # Indian Standard Timezone UTC +05:30
    ist_timezone = datetime.timezone(
        datetime.timedelta(hours=5, minutes=30)
    )
    # current date
    date = datetime.datetime.now(ist_timezone)
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
        center_address = center['address']
        for session in center.get('sessions'):
            if session['available_capacity'] > 0 and session['min_age_limit'] <= age_group:
                if center_id not in info:
                    info[center_id] = {
                            "name": center_name,
                            "address": center_address,
                            "sessions": []
                            }
                info[center_id]['sessions'].append({
                    "date": session['date'],
                    "available_capacity": session['available_capacity'],
                    "age_limit": session['min_age_limit'],
                    "vaccine": session['vaccine'],
                    "slots": session['slots']
                    })
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
    cache.add(key, fetched_centers, expire=CACHE_EXPIRATION_TIME)
    
    if cached_centers is None and fetched_centers:
        return fetched_centers
    
    # difference to be returned to the user
    diff_centers = {}
    for center_id, value in fetched_centers.items():
        if center_id in cached_centers:
            # search differing sessions
            for fsession in value['sessions']:
                date_match = [csession for csession in cached_centers[center_id]['sessions'] 
                                       if csession['date'] == fsession['date']
                                          and fsession['age_limit'] == csession['age_limit']
                                          and fsession['vaccine'] == csession['vaccine']
                            ]
                if date_match:
                    for csession in date_match:
                        if fsession['available_capacity'] > csession['available_capacity']:
                            if center_id not in diff_centers:
                               center = diff_centers[center_id] = value
                               center['sessions'] = []
                            diff_centers[center_id]['sessions'].append(fsession)
                else:
                    if center_id not in diff_centers:
                        center = diff_centers[center_id] = value
                        center['sessions'] = []
                    diff_centers[center_id]['sessions'].append(fsession)
        else:
            diff_centers[center_id] = value

    return diff_centers if diff_centers else None
