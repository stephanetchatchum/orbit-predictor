import streamlit as st
from skyfield.api import load, wgs84
import reverse_geocoder as rg
from haversine import haversine
from datetime import datetime, timezone, timedelta
import matplotlib.pyplot as plt
import requests


st.title("ISS Live Tracker")

satellites = load.tle_file('https://celestrak.org/NORAD/elements/gp.php?GROUP=stations&FORMAT=tle')
by_name = {sat.name: sat for sat in satellites}
iss = by_name['ISS (ZARYA)']

ts = load.timescale()
t = ts.now()

subpoint = iss.at(t).subpoint()
lat = subpoint.latitude.degrees
lon = subpoint.longitude.degrees

result = rg.search((lat, lon), mode=1)
place = result[0]
distance = haversine((lat, lon), (float(place['lat']), float(place['lon'])))

if distance < 500:
    st.write(f"The ISS is currently above **{place['name']}, {place['cc']}**")
else:
    st.write(f"The ISS is currently over **open ocean or remote territory** (nearest place: {place['name']}, {place['cc']}, {distance:.0f} km away)")

st.write(f"Coordinates: {lat:.2f}, {lon:.2f}")
st.subheader("Ground Track (Next 100 Minutes)")

now = datetime.now(timezone.utc)
times = ts.utc(now.year, now.month, now.day, now.hour, range(now.minute, now.minute + 100))

track = iss.at(times).subpoint()
lats = track.latitude.degrees
lons = track.longitude.degrees

lons_fixed = [lons[0]]
lats_fixed = [lats[0]]

for i in range(1, len(lons)):
    if abs(lons[i] - lons[i-1]) > 180:
        lons_fixed.append(None)
        lats_fixed.append(None)
    lons_fixed.append(lons[i])
    lats_fixed.append(lats[i])

fig, ax = plt.subplots()
ax.plot(lons_fixed, lats_fixed)
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")
ax.grid(True)
st.pyplot(fig)

def get_location():
    try:
        response = requests.get('http://ip-api.com/json/', timeout=5)
        data = response.json()
        return data['lat'], data['lon'], data.get('city', 'unknown')
    except Exception as e:
        print(f"Location lookup failed: {e}")
        return 3.8480, 11.5021, 'Yaoundé (default, location lookup failed)'

st.subheader("Upcoming Passes Over Your Location")

user_lat, user_lon, user_city = get_location()
st.write(f"Detected location: **{user_city}** ({user_lat:.2f}, {user_lon:.2f})")

observer = wgs84.latlon(user_lat, user_lon)
t1 = ts.utc(now.replace(tzinfo=timezone.utc) + timedelta(days=7))

times, events = iss.find_events(observer, t, t1, altitude_degrees=10)
event_names = ['Rises', 'Culminates', 'Sets']

rows = []
for ti, event in zip(times, events):
    rows.append({"Time (UTC)": ti.utc_strftime('%Y-%m-%d %H:%M'), "Event": event_names[event]})

st.dataframe(rows)

