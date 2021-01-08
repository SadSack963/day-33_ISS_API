import requests
import datetime as dt
import smtplib
from time import sleep
import os


# Milton Keynes - Latitude: 52.040623, Longitude: -0.759417
LOC = "Milton Keynes"
LAT = 52.040623
LNG = -0.759417
LAT_LNG_TOL = 5

YAHOO_SENDER = os.environ.get("SMTP_YAHOO_SENDER")
YAHOO_USERNAME = os.environ.get("SMTP_YAHOO_USERNAME")
YAHOO_EMAIL = os.environ.get("SMTP_YAHOO_EMAIL")
YAHOO_PASSWORD = os.environ.get("SMTP_YAHOO_PASSWORD")
YAHOO_TO_ADDR = os.environ.get("SMTP_YAHOO_TO_ADDR")


def get_iss_data():
    global msg_text
    response = requests.get(url="http://api.open-notify.org/iss-now.json")
    response.raise_for_status()  # Raise an exception for HTTP Errors

    try:
        data = response.json()
    except ValueError:
        print("No data in API response")
        return False
    else:
        # print(data)
        timestamp = int(data["timestamp"])
        iss_datetime = dt.datetime.fromtimestamp(timestamp)
        iss_time = iss_datetime.time()
        iss_latitude = float(data["iss_position"]["latitude"])
        iss_longitude = float(data["iss_position"]["longitude"])
        iss_position = (iss_latitude, iss_longitude)
        msg_text += f"Time: {iss_time}, ISS Position (lat, lng): {iss_position}"
        return iss_overhead(iss_position)


def iss_overhead(iss_pos):
    lat_min = round(LAT - LAT_LNG_TOL, 1)
    lat_max = round(LAT + LAT_LNG_TOL, 1)
    lng_min = round(LNG - LAT_LNG_TOL, 1)
    lng_max = round(LNG + LAT_LNG_TOL, 1)

    print(lat_min, iss_pos[0], lat_max)
    print(lng_min, iss_pos[1], lng_max)

    if lat_min <= iss_pos[0] <= lat_max and lng_min <= iss_pos[1] <= lng_max:
        return True
    else:
        return False


def get_time():
    # https://sunrise-sunset.org/api
    # https://www.latlong.net/

    api_url = "https://api.sunrise-sunset.org/json"

    # url = api_url + f"?lat={lat}&lng={lng}"
    # response = requests.get(url=url, timeout=1)

    parameters = {"lat": LAT, "lng": LNG, "formatted": 0}
    response = requests.get(url=api_url, params=parameters, timeout=1)

    response.raise_for_status()
    try:
        data = response.json()
    except ValueError:
        print("No data in API response")
        return False
    else:
        day_start = data["results"]["astronomical_twilight_begin"]
        #    2021-01-02T06:06:06+00:00
        day_start_hour = int(day_start.split("T")[1].split(":")[0])

        day_end = data["results"]["astronomical_twilight_end"]
        #    2021-01-02T18:08:44+00:00
        day_end_hour = int(day_end.split("T")[1].split(":")[0])

        time_now_hour = dt.datetime.now().hour
        if time_now_hour > day_end_hour or time_now_hour < day_start_hour:
            return True
        else:
            return False


def send_mail(to_addr, msg):
    message = f"From: \"{YAHOO_SENDER}\" <{YAHOO_EMAIL}>\n" \
              f"To: {to_addr}\n" \
              f"Subject: ISS OVERHEAD!\n\n" + msg
    print(message)
    with smtplib.SMTP(host="smtp.mail.yahoo.co.uk", port=587) as connection:
        # Secure the connection
        connection.starttls()
        connection.login(user=YAHOO_USERNAME, password=YAHOO_PASSWORD)
        connection.sendmail(from_addr=YAHOO_EMAIL, to_addrs=to_addr, msg=message.encode("utf-8"))


while True:
    msg_text = f"Go outside and look up to see the ISS pass overhead.\n" \
           f"ISS location over {LOC}: "

    iss_visible = get_iss_data()  # bool
    night_time = get_time()  # bool

    if iss_visible and night_time:
        send_mail(YAHOO_TO_ADDR, msg_text)
    sleep(60)
