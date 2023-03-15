import json
import time
import requests
from datetime import datetime, timedelta


url = "https://tools.usps.com/UspsToolsRestServices/rest/v2/facilityScheduleSearch"


def search(date, city, num_adults = "0", num_kids = "1"):
    """Check if something +-1 day around a particular date and near an office is available"""
    payload = json.dumps({
      "poScheduleType": "PASSPORT",
      "date": date,
      "numberOfAdults": num_adults,
      "numberOfMinors": num_kids,
      "radius": "20",
      "zip5": "",
      "city": city,
      "state": " ca"
    })
    # they send you into an infinite redirect loop if you use the default agents of curl or requests
    headers = {
      'User-Agent': "Mozilla/5.0 (X11; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/81.0",
      'Content-Type': 'application/json',
      # cookie from chrome.  no idea how long it is good for but prolly forever
      'Cookie': 'TLTSID=ac8886ad8ae1162d950000e0ed96ae55; JSESSIONID=0000kUzPjygD-mXbFpXvA5a0Yez:1bbcn21dv; NSC_uppmt-usvf-ofx=ffffffff3b22378945525d5f4f58455e445a4a4212d3'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    valid = []
    for facility in response.json()["facilityDetails"]:
        if any(day["status"] == "true" for day in facility["date"]):
            valid.append(facility)
    return valid


d = datetime.today()
end_day = datetime.today() + timedelta(days=26)
dates = []
while d < end_day:
    d += timedelta(days=1)
    if d.weekday() in (1, 4):
        dates.append(d.strftime('%Y%m%d'))
print('Dates to check: ', dates)


# target cities to search
cities = ['foster city', 'san francisco', 'half moon bay', 'palo alto', 'san jose', 'fremont', 'oakland', 'hayward']
known = set()
t0 = time.time()

# simply loop through all and check if they are available
for date in dates:
    print(f'Checking +-1 days around {date}...')
    for city in cities:
        results = search(date, city)
        for result in results:
            entry = {"city": result['address']['city'], "dates":[item["date"] for item in result["date"] if item["status"] == "true"]}
            result_s = json.dumps(entry, indent=2)
            if result_s not in known:
                print('FOUND OPENING:')
                print(result_s)
                known.add(result_s)
print(f'A full sweep took {time.time()-t0:.1f} seconds')
