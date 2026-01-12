import requests
import datetime
import xml.etree.ElementTree as ET
from xml.dom import minidom
import time
import gzip

# 1. API Configuration
MASTER_LIST_URL = "https://tm-api.tataplay.com/content-detail/pub/api/v1/channels?limit=600"
SCHEDULE_URL_TEMPLATE = "https://tm-api.tataplay.com/content-detail/pub/api/v1/channels/{id}/schedule?date={date}"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Origin': 'https://www.tataplay.com',
    'Referer': 'https://www.tataplay.com/'
}

# 2. Filter List: Names of channels you want to include
# If the script finds these in the master list, it will grab their EPG
FILTER_NAMES = ["Star Plus", "Zee TV", "Sony Entertainment Television", "Colors", "Star Sports 1", "Sun TV"]

def format_xml_time(ts):
    dt = datetime.datetime.fromtimestamp(int(ts)/1000)
    return dt.strftime("%Y%m%d%H%M%S +0530")

def get_live_channel_map():
    print("Discovering live channel IDs...")
    try:
        response = requests.get(MASTER_LIST_URL, headers=HEADERS, timeout=15)
        response.raise_for_status()
        channels = response.json().get('data', {}).get('list', [])
        
        found_channels = []
        for ch in channels:
            name = ch.get('channelName', '')
            # Match against our filter
            if any(f_name.lower() in name.lower() for f_name in FILTER_NAMES):
                found_channels.append({
                    "id": str(ch.get('channelId')),
                    "name": name,
                    "xmlid": name.replace(" ", "") + ".in"
                })
        print(f"Discovered {len(found_channels)} channels.")
        return found_channels
    except Exception as e:
        print(f"Discovery failed: {e}")
        return []

def fetch_epg():
    channels_to_fetch = get_live_channel_map()
    if not channels_to_fetch: return

    root = ET.Element("tv", {"generator-info-name": "Auto-Discovery-EPG"})

    # Add channel headers
    for ch in channels_to_fetch:
        c_tag = ET.SubElement(root, "channel", id=ch['xmlid'])
        ET.SubElement(c_tag, "display-name").text = ch['name']

    # Fetch 7-day data
    for day_offset in range(-7, 1):
        target_date = (datetime.datetime.now() + datetime.timedelta(days=day_offset)).strftime("%d-%m-%Y")
        print(f"--- Fetching for {target_date} ---")

        for ch in channels_to_fetch:
            url = SCHEDULE_URL_TEMPLATE.format(id=ch['id'], date=target_date)
            try:
                resp = requests.get(url, headers=HEADERS, timeout=10)
                if resp.status_code == 200:
                    schedules = resp.json().get('data', {}).get('schedules', [])
                    for prog in schedules:
                        p_tag = ET.SubElement(root, "programme", 
                                             start=format_xml_time(prog['startTime']), 
                                             stop=format_xml_time(prog['endTime']), 
                                             channel=ch['xmlid'])
                        ET.SubElement(p_tag, "title", lang="en").text = prog.get('title', 'No Title')
                        ET.SubElement(p_tag, "desc", lang="en").text = prog.get('description', 'No Description')
                time.sleep(0.2)
            except: continue

    # Save and Compress
    xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
    with open("epg.xml", "w", encoding="utf-8") as f: f.write(xml_str)
    with open("epg.xml", "rb") as f_in, gzip.open("epg.xml.gz", "wb") as f_out:
        f_out.writelines(f_in)
    print("Done!")

if __name__ == "__main__":
    fetch_epg()
