import requests
import datetime
import xml.etree.ElementTree as ET
from xml.dom import minidom
import time

# 1. UPDATED CHANNEL LIST (Using Tata Play Web IDs)
CHANNELS = [
    {"id": "117", "name": "Star Plus", "xmlid": "StarPlus.in"},
    {"id": "143", "name": "Zee TV", "xmlid": "ZeeTV.in"},
    {"id": "130", "name": "Sony SET", "xmlid": "SonySET.in"},
    {"id": "402", "name": "Star Sports 1", "xmlid": "StarSports1.in"},
]

# 2. ADDED BROWSER HEADERS (Crucial to avoid "Line 1 Column 1" error)
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://www.tataplay.com/web-guide',
    'Accept': 'application/json, text/plain, */*'
}

def format_xml_time(ts):
    # API usually returns seconds or milliseconds; adjusting for both
    dt = datetime.datetime.fromtimestamp(int(ts)/1000 if len(str(ts)) > 10 else int(ts))
    return dt.strftime("%Y%m%d%H%M%S +0530")

def fetch_epg():
    root = ET.Element("tv", {"generator-info-name": "Indian-EPG-Generator"})
    
    for ch in CHANNELS:
        c_tag = ET.SubElement(root, "channel", id=ch['xmlid'])
        ET.SubElement(c_tag, "display-name").text = ch['name']

    # Fetch 7 days of past data + today
    for day_offset in range(-7, 1):
        target_date = (datetime.datetime.now() + datetime.timedelta(days=day_offset)).strftime("%d-%m-%Y")
        print(f"--- Processing Date: {target_date} ---")

        for ch in CHANNELS:
            # 3. UPDATED API URL (The more stable web-guide version)
            url = f"https://www.tataplay.com/web-guide/api/v1/channels/{ch['id']}/schedule?date={target_date}"
            
            try:
                print(f"Fetching {ch['name']}...")
                response = requests.get(url, headers=HEADERS, timeout=20)
                
                # Check if we actually got a successful response
                if response.status_code == 200:
                    data = response.json() # This won't crash now
                    programs = data.get('data', {}).get('schedules', [])
                    
                    for prog in programs:
                        p_tag = ET.SubElement(root, "programme", 
                                             start=format_xml_time(prog['startTime']), 
                                             stop=format_xml_time(prog['endTime']), 
                                             channel=ch['xmlid'])
                        ET.SubElement(p_tag, "title", lang="hi").text = prog.get('title', 'Unknown')
                        ET.SubElement(p_tag, "desc", lang="hi").text = prog.get('description', 'No description')
                else:
                    print(f"Error: Server returned {response.status_code} for {ch['name']}")
                
                time.sleep(1) # Be gentle to the server
            except Exception as e:
                print(f"Failed to fetch {ch['name']}: {e}")

    # Save to File
    xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
    with open("epg.xml", "w", encoding="utf-8") as f:
        f.write(xml_str)
    print("DONE: epg.xml created.")

if __name__ == "__main__":
    fetch_epg()
