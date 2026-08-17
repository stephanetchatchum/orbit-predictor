from skyfield.api import load
import reverse_geocoder as rg
from haversine import haversine
from datetime import datetime, timezone
import matplotlib.pyplot as plt
from skyfield.api import wgs84
from datetime import timedelta
import requests

def get_location():
    try:
        response = requests.get('https://ipinfo.io/json')
        data = response.json()
        lat, lon = map(float, data['loc'].split(','))
        return lat, lon, data.get('city', 'unknown')
    except Exception:
        return 3.8480, 11.5021, 'Yaoundé (default, location lookup failed)'

if __name__ == "__main__":
    satellites = load.tle_file('https://celestrak.org/NORAD/elements/gp.php?GROUP=stations&FORMAT=tle')
    by_name = {sat.name: sat for sat in satellites}
    iss = by_name['ISS (ZARYA)']

    ts = load.timescale()
    t = ts.now()

    subpoint = iss.at(t).subpoint()
    lat = subpoint.latitude.degrees
    lon = subpoint.longitude.degrees

    result = rg.search((lat, lon))
    place = result[0]

    distance = haversine((lat, lon), (float(place['lat']), float(place['lon'])))

    if distance < 500:
        print(f"The ISS is currently above {place['name']}, {place['cc']}")
    else:
        print(f"The ISS is currently over open ocean or remote territory (nearest place: {place['name']}, {place['cc']}, {distance:.0f} km away)")

    print(f"Coordinates: {lat:.2f}, {lon:.2f}")

    now = datetime.now(timezone.utc)
    times = ts.utc(now.year, now.month, now.day, now.hour, range(now.minute, now.minute + 100))

    track = iss.at(times).subpoint()
    lats = track.latitude.degrees
    lons = track.longitude.degrees

    plt.plot(lons, lats)
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.title("ISS Ground Track: Next 100 Minutes")
    plt.grid(True)
    plt.show()

    user_lat, user_lon, user_city = get_location()
    print(f"Detected location: {user_city} ({user_lat:.2f}, {user_lon:.2f})")
    observer = wgs84.latlon(user_lat, user_lon)

    t0 = ts.now()
    t1 = ts.utc(now + timedelta(days=7))

    times, events = iss.find_events(observer, t0, t1, altitude_degrees=10)
    event_names = ['rises', 'culminates', 'sets']

    for ti, event in zip(times, events):
        print(ti.utc_strftime('%Y-%m-%d %H:%M UTC'), event_names[event])