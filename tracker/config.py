# Trip being tracked. Edit these and the daily job picks them up.
ADULTS = 2

# (origin, destination, first travel date, last travel date)
ROUTES = [
    ("DEL", "SXR", "2027-01-05", "2027-01-09"),   # outbound around 7 Jan
    ("SXR", "DEL", "2027-01-13", "2027-01-22"),   # return 1-2 weeks later
]

# Alert when the cheapest NON-STOP fare for 2 people (one way) drops to or below this.
TARGET_ONE_WAY_TOTAL_INR = 13000
