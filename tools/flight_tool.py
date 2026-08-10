import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("AVIATIONSTACK_API_KEY")


# format date and time from api response 
def format_datetime(dt_str):
    if not dt_str or dt_str == "Unknown":
        return "Unknown"
    try:
        dt = datetime.fromisoformat(str(dt_str).replace("Z", "+00:00"))
        hour_12 = dt.hour % 12 or 12
        month_year = dt.strftime("%b %Y")
        if "T" in str(dt_str):
            time_part = dt.strftime("%M %p")
            return f"{dt.day} {month_year}, {hour_12}:{time_part}"
        else:
            return f"{dt.day} {month_year}"
    except Exception:
        return str(dt_str)


def search_flights(query):

    url = "http://api.aviationstack.com/v1/flights"

    params = {
        "access_key": API_KEY,
        "limit": 5,
        # "dep_iata": "SYD", 
        # "arr_iata": "MEL", 
        # "flight_status": "active"
        
    }
   
    # api call using requests
    response = requests.get(url, params=params)
    data = response.json()

    # store flight details in empty list
    flights = []

    #check if response has data key
    if "data" in data:

        # loop through first 5 flights
        for flight in data["data"][:5]:

            # get flight date
            raw_date = flight.get("flight_date", "Unknown")
            flight_date = format_datetime(raw_date)

            # get airline name
            airline = flight.get("airline", {}).get("name", "Unknown")

            # get departure details
            departure_info = flight.get("departure", {})
            departure = departure_info.get("airport", "Unknown")
            raw_dep_time = departure_info.get("scheduled") or departure_info.get("estimated") or "Unknown"
            departure_time = format_datetime(raw_dep_time)

            # get arrival details
            arrival_info = flight.get("arrival", {})
            arrival = arrival_info.get("airport", "Unknown")
            raw_arr_time = arrival_info.get("scheduled") or arrival_info.get("estimated") or "Unknown"
            arrival_time = format_datetime(raw_arr_time)

            # get flight status
            status = flight.get("flight_status", "Unknown")
            
            # add flight details to list
            flights.append(
                f"""
Airline: {airline}
Date: {flight_date}
Departure: {departure}
Departure Time: {departure_time}
Arrival: {arrival}
Arrival Time: {arrival_time}
Status: {status}
"""
            )

    return "\n".join(flights)


# test this tool
# print(search_flights("flights from Sydney to Melbourne"))

