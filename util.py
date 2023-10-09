import requests


def notification_helper(notifcationURL, error):
    print("Sending notification to " + notifcationURL)

    requests.post(notifcationURL, data={
        "username": "Air Quality Monitor",
        "message": str(error)
    })

    print("Notification sent")


def upload_to_db(mongo_client, data):
    print("Uploading data to DB ...")

    mongo_client.air_quality.air_quality.insert_one(data)

    print("Data uploaded to DB")
