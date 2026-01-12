import requests
import json
import gzip
import datetime

# Configuration
CHANNELS_API = "https://jiotv.data.cdn.jio.com/apis/v1.4/getMobileChannelList/get/?os=android&devicetype=phone"
EPG_API = "http://jiotv.data.cdn.jio.com/apis/v1.3/getepg/get"

def generate_epg():
    print("Fetching channel list...")
    channels = requests.get(CHANNELS_API).json()['result']
    
    # Start XML
    xml = '<?xml version="1.0" encoding="UTF-8"?><tv generator-info-name="MyCustomEPG">'
    
    # Process Channels
    for ch in channels[:50]: # Limiting to 50 for speed
        xml += f'<channel id="{ch["channel_id"]}">'
        xml += f'<display-name lang="en">{ch["channel_name"]}</display-name>'
        xml += f'<icon src="http://jiotv.catchup.cdn.jio.com/dare_images/images/{ch["logoUrl"]}" />'
        xml += '</channel>'

    # Process Programs (Today)
    for ch in channels[:50]:
        print(f"Fetching guide for {ch['channel_name']}...")
        params = {"offset": 0, "channel_id": ch["channel_id"], "langId": 6}
        try:
            epg_data = requests.get(EPG_API, params=params).json().get("epg", [])
            for p in epg_data:
                # Convert timestamps
                start = datetime.datetime.fromtimestamp(p['startEpoch']/1000).strftime('%Y%m%d%H%M%S +0530')
                stop = datetime.datetime.fromtimestamp(p['endEpoch']/1000).strftime('%Y%m%d%H%M%S +0530')
                
                xml += f'<programme start="{start}" stop="{stop}" channel="{ch["channel_id"]}">'
                xml += f'<title lang="en">{p["showname"]}</title>'
                xml += f'<desc lang="en">{p.get("description", "No description")}</desc>'
                xml += '</programme>'
        except:
            continue

    xml += '</tv>'
    
    # Save as .xml
    with open("epg.xml", "w", encoding="utf-8") as f:
        f.write(xml)
        
    # Save as .xml.gz (Compressed)
    with gzip.open("epg.xml.gz", "wb") as f:
        f.write(xml.encode("utf-8"))
    
    print("Done! epg.xml.gz created.")

if __name__ == "__main__":
    generate_epg()
