import requests
import json
import gzip
import datetime
import time
import sys

# Configuration
CHANNELS_API = "https://jiotv.data.cdn.jio.com/apis/v1.4/getMobileChannelList/get/?os=android&devicetype=phone"
EPG_API = "http://jiotv.data.cdn.jio.com/apis/v1.3/getepg/get"
HEADERS = {
    "User-Agent": "JioTV/7.0.5 (Linux; Android 11)",
    "Accept": "application/json"
}

def generate_epg():
    print("Starting EPG Generation...")
    
    try:
        response = requests.get(CHANNELS_API, headers=HEADERS, timeout=15)
        response.raise_for_status()
        channels = response.json().get('result', [])
    except Exception as e:
        print(f"CRITICAL ERROR: Could not fetch channel list. {e}")
        sys.exit(1)

    # Start XMLTV structure
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<tv generator-info-name="CustomEPG-Bot">\n'
    
    # 1. Add Channel Metadata
    print(f"Processing {len(channels[:100])} channels...") # Limited to top 100 for stability
    for ch in channels[:100]:
        ch_id = str(ch.get("channel_id"))
        ch_name = ch.get("channel_name", "Unknown")
        logo = f"http://jiotv.catchup.cdn.jio.com/dare_images/images/{ch.get('logoUrl', '')}"
        
        xml += f'  <channel id="{ch_id}">\n'
        xml += f'    <display-name lang="en">{ch_name}</display-name>\n'
        xml += f'    <icon src="{logo}" />\n'
        xml += f'  </channel>\n'

    # 2. Fetch Program Guide for each channel
    for ch in channels[:100]:
        ch_id = ch.get("channel_id")
        print(f"Fetching: {ch.get('channel_name')} (ID: {ch_id})")
        
        # params: offset 0 is Today, 1 is Tomorrow
        params = {"offset": 0, "channel_id": ch_id, "langId": 6}
        
        try:
            resp = requests.get(EPG_API, params=params, headers=HEADERS, timeout=10)
            
            # Check if response is valid JSON
            if resp.status_code == 200 and resp.text.strip():
                data = resp.json()
                programs = data.get("epg", [])
                
                for p in programs:
                    # JioTV uses milliseconds (epoch * 1000)
                    start_dt = datetime.datetime.fromtimestamp(p['startEpoch']/1000)
                    stop_dt = datetime.datetime.fromtimestamp(p['endEpoch']/1000)
                    
                    start = start_dt.strftime('%Y%m%d%H%M%S +0530')
                    stop = stop_dt.strftime('%Y%m%d%H%M%S +0530')
                    
                    title = p.get("showname", "No Title").replace("&", "&amp;")
                    desc = p.get("description", "").replace("&", "&amp;")
                    
                    xml += f'  <programme start="{start}" stop="{stop}" channel="{ch_id}">\n'
                    xml += f'    <title lang="en">{title}</title>\n'
                    xml += f'    <desc lang="en">{desc}</desc>\n'
                    xml += f'  </programme>\n'
            else:
                print(f"  ! Empty or error response for {ch_id}")
                
        except json.decoder.JSONDecodeError:
            print(f"  ! JSON Error: API likely returned HTML/Blocked message for {ch_id}")
        except Exception as e:
            print(f"  ! Skip {ch_id}: {e}")
        
        # Anti-ban delay
        time.sleep(0.5)

    xml += '</tv>'

    # 3. Save Files
    print("Saving files...")
    with open("epg.xml", "w", encoding="utf-8") as f:
        f.write(xml)
        
    with gzip.open("epg.xml.gz", "wb") as f:
        f.write(xml.encode("utf-8"))
        
    print("Successfully created epg.xml and epg.xml.gz")

if __name__ == "__main__":
    generate_epg()
