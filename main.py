import datetime
import json
import requests
from pymongo import MongoClient

from util import notification_helper, upload_to_db

STATE_URL = 'https://alexa.amazon.de/api/phoenix/state'

HEADERS = {
    "User-Agent": "AppleWebKit PitanguiBridge/2.2.454039.0-[HARDWARE=iPhone8_1][SOFTWARE=14.4][DEVICE=iPhone]",
}

with open("config.json") as f:
    config = json.load(f)

    COOKIES = {}
    COOKIES['at-acbde'] = config['at_acbde']
    COOKIES['ubid-acbde'] = config['ubid_acbde']

    DEVICE_ID = config['device_id']
    NOTIFICATION_URL = config['notification_url']
    DB_URL = config['db_url']

mongo_client = MongoClient(DB_URL)


def make_amazon_request():
    print("Making request to Amazon ...")

    resp = requests.post(STATE_URL, headers=HEADERS, cookies=COOKIES, json={
        "stateRequests": [{"entityId": DEVICE_ID, "entityType": "APPLIANCE"}]
    })
    if resp.status_code != 200:
        raise RuntimeError("unexpected response from amazon, code %d: %s" % (
            resp.status_code, resp.text))

    j = resp.json()

    if 'errors' in j and j['errors']:
        raise RuntimeError("got an error from amazon: %s" % j['errors'])
    if 'error' in j['deviceStates'][0] and j['deviceStates'][0]['error']:
        raise RuntimeError("got error in deviceStates: %s" % resp.text)
    if 'capabilityStates' not in j['deviceStates'][0]:
        raise RuntimeError("expected capabilityStates, got %s" % resp.text)

    capabilities = {}
    for cap in j['deviceStates'][0]['capabilityStates']:
        capj = json.loads(cap)
        capabilities[capj['instance']] = capj['value']

    print("Request to Amazon successful")

    return capabilities


def result_parser(response):
    print("Parsing result ...")

    status = response['10']['value']

    if not status == 'OK':
        raise RuntimeError("Air Monitor is not OK")

    temp = response['3']['value']
    humidity = response['4']
    voc = response['5']
    particulate_matter = response['6']
    carbon_monoxide = response['8']
    quality_score = response['9']

    print("Result parsed")

    return dict(
        status=status,
        temp=temp,
        humidity=humidity,
        voc=voc,
        particulate_matter=particulate_matter,
        carbon_monoxide=carbon_monoxide,
        quality_score=quality_score,
        date=datetime.datetime.now().isoformat()
   )


def get_air_quality():

    data = make_amazon_request()

    formatted_data = result_parser(data)

    print("Data: ", formatted_data)

    upload_to_db(mongo_client, formatted_data)


if __name__ == "__main__":
    try:
        air_data = get_air_quality()
    except Exception as e:
        notification_helper(NOTIFICATION_URL, e)
