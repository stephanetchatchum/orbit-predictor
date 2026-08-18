# Real-Time ISS Tracker & Orbital Mechanics

A tool that calculates a satellite's real position using orbital physics,
not machine learning, then predicts when it will be visible from anywhere
on Earth.

**[Live demo not yet deployed, see Running It below]**

## How This Differs From the Exoplanet Project

The classifier learned patterns from thousands of labelled examples. This
project uses no training data at all. Given a satellite's current orbital
state, Newton's laws (via the SGP4 algorithm) determine its position
directly. Deterministic physics, not statistics.

## What It Does

1. **Live position:** fetches real, current orbital data for the ISS from
   Celestrak and computes its exact latitude, longitude, and altitude.
2. **Location awareness:** converts coordinates into a place name, with an
   honest fallback over open ocean (see below).
3. **Ground track visualisation:** plots the ISS's path over the next 100
   minutes.
4. **Personal pass predictions:** detects the user's approximate location
   via IP geolocation, then calculates every time the ISS will be visible
   overhead for the next 7 days: rise, peak, and set times.

## Example Output

The ISS is currently above Manta, EC
Coordinates: -8.09, -76.34
Detected location: Douala (4.05, 9.70)
2026-08-19 00:23 UTC rises
2026-08-19 00:26 UTC culminates
2026-08-19 00:29 UTC sets


## A Decision Worth Explaining

Reverse-geocoding always returns the *nearest* named place, even when that
place is thousands of kilometres away. Early testing showed the ISS
reported as "above Kigali" while it was actually over the Pacific, the
nearest labelled dot on the map, but a misleading answer.

Fixed by calculating real distance (the haversine formula, which accounts
for Earth's curvature) between the satellite and the nearest named place,
trusting the name only within 500 km. Beyond that, it honestly reports
"over open ocean or remote territory" instead of guessing with false
confidence.

## Known Limitation

When the ground track crosses the 180°/-180° longitude line, the plot
currently draws a stray connecting line across the chart, a common
plotting artifact, not a physics error. Fix: detect large jumps in
longitude between consecutive points and split the line there. Not yet
implemented.

## Running It

```bash
git clone https://github.com/stephanetchatchum/orbit-predictor.git
cd orbit-predictor

python -m venv venv
source venv/Scripts/activate    # Windows
# source venv/bin/activate      # Mac/Linux

pip install -r requirements.txt
python predict.py
```

No dataset download needed, satellite data is fetched live from Celestrak
on every run.

## Built With

Python, Skyfield (SGP4 orbital mechanics), matplotlib, reverse_geocoder,
haversine, requests

## Author

Tchatchum Chassem Stephane, https://github.com/stephanetchatchum/