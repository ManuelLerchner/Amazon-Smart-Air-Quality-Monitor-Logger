# Amazon Smart Air Quality Monitor - Logger

Since the Amazon Smart Air Quality Monitor does not provide a way to export the data and only keeps the data for 7 days, a custom script is needed to log the data.

The additional problem is that there isn't even an API to get the data from the device. The only way to get the data is to scrape the data from the web interface using the credentials of the Amazon account.

This script is mostly adapted from [alexa-exporter](https://github.com/knyar/alexa-exporter/tree/main)

It additionally sends a notification to a webhook when an error occurs, this helps to detect when the script stops working.

All the captured data is stored in a database. In my case I use a MongoDB database.

## Usage

1. Create a `config.json` file in the same directory as the script with the following content:

    ```json
    {
        "device_id": "YOUR_DEVICE_ID",
        "at_acbde": "YOUR_AT_ACBDE_COOKIE",
        "ubid_acbde": "YOUR_UBID_ACBDE_COOKIE",
        "notification_url": "YOUR_NOTIFICATION_URL",
        "db_url": "YOUR_MONGODB_URL"
    }
    ```

2. Run pip to install the dependencies:

    ```bash
    pip3 install -r requirements.txt
    ```

2. Create a `cronjob` to run the script every 10 minutes. You can use (https://crontab.guru/)[https://crontab.guru] to generate the cronjob.

    ```bash
    crontab -e
    ```

    Enter the following line:

    ```bash
    */10 * * * * cd /path/to/script && /usr/bin/python3 main.py > /tmp/alexa-exporter.log 2>&1
    ```