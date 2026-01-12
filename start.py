import requests
import json
import datetime
import os

# Configuration for past/future days
prevEpgDayCount = 2
nextEpgDayCount = 2

# Headers to bypass API blocking
headers = {
    "User-Agent": "JioTV 7.0.5 (Android 10)",
    "appkey": "NzNiMDhlYzQyNjJm",
    "os": "android",
    "devicetype": "phone",
    "versionCode": "300"
}

def getChannels():
    url = "https://jiotv.data.cdn.jio.com/apis/v1.4/getMobileChannelList/get/?os=android&devicetype=phone"
    try:
        res = requests.get(url, headers=headers, timeout=15)
        return res.json().get("result", []) if res.status_code == 200 else []
    except: return []

def writeEpgChannel(id, name, icon, fp):
    name = str(name).replace("&", "&amp;").replace("<", "&lt;")
    fp.write(f'\t<channel id="{id}">\n\t\t<display-name>{name}</display-name>\n')
    fp.write(f'\t\t<icon src="{icon}"></icon>\n\t</channel>\n')

# Main execution loop
channels = getChannels()
if channels:
    with open("channels.xml", "w", encoding='utf-8') as cf:
        for c in channels:
            writeEpgChannel(c["channel_id"], c["channel_name"], c["logoUrl"], cf)
    # Note: Further logic for individual program files would follow here
    print("Action complete")
