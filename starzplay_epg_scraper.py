import requests
import json
import time
from datetime import datetime, timezone
import xml.etree.ElementTree as ET
import math
import xml.dom.minidom

def format_time(unix_ts):
    dt = datetime.fromtimestamp(unix_ts, tz=timezone.utc)
    return dt.strftime('%Y%m%d%H%M%S +0000')

def fetch_epg():
    print(f"[{datetime.now()}] Fetching EPG data from Starzplay...")
    base_url = 'https://epg.aws.playco.com/api/v1.1/epg/category/events/web-epg-scraper-sp'
    
    now = int(time.time())
    ts_start = now - (86400 * 1)
    ts_end = now + (86400 * 2)

    page = 1
    limit = 20
    total_pages = 1
    
    channels_dict = {}
    
    while page <= total_pages:
        params = {
            'ts_start': ts_start,
            'ts_end': ts_end,
            'lang': 'ar',
            'pg': 18,
            'category': 'all',
            'page': page,
            'limit': limit,
            'x-geo-country': 'SA'
        }
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        try:
            r = requests.get(base_url, params=params, headers=headers)
            r.raise_for_status()
            data = r.json()
            
            if page == 1:
                total = data.get('total', 0)
                if limit == 10: limit = 20  # increased limit
                total_pages = math.ceil(total / limit)
                print(f"Total channels to fetch: {total} ({total_pages} pages)")
                
            for channel in data.get('data', []):
                chan_slug = channel.get('slug')
                if not chan_slug:
                    continue
                channels_dict[chan_slug] = channel
                
            print(f"Fetched page {page}/{total_pages}")
            page += 1
            time.sleep(0.5)
            
        except Exception as e:
            print(f"Error fetching page {page}: {e}")
            break

    print(f"[{datetime.now()}] Generating XML file...")
    
    tv = ET.Element("tv", {"generator-info-name": "Starzplay Scraper"})
    
    for slug, channel in channels_dict.items():
        chan_el = ET.SubElement(tv, "channel", {"id": slug})
        name_el = ET.SubElement(chan_el, "display-name")
        name_el.text = channel.get('title', slug)
        
        images = channel.get('images', [])
        if images:
            logo = next((img for img in images if img.get('type') == 'logo-png'), None)
            if not logo:
                logo = images[0]
            ET.SubElement(chan_el, "icon", {"src": logo.get('url', '')})
            
    for slug, channel in channels_dict.items():
        events = channel.get('events', [])
        for event in events:
            prog_el = ET.SubElement(tv, "programme", {
                "start": format_time(event.get('tsStart', 0)),
                "stop": format_time(event.get('tsEnd', 0)),
                "channel": slug
            })
            
            title_el = ET.SubElement(prog_el, "title")
            title_el.text = event.get('title', 'Unknown')
            
            desc_el = ET.SubElement(prog_el, "desc")
            desc_el.text = event.get('description', '')
            
            ev_images = event.get('images', [])
            if ev_images:
                ET.SubElement(prog_el, "icon", {"src": ev_images[0].get('url', '')})

    xml_str = ET.tostring(tv, encoding="utf-8")
    reparsed = xml.dom.minidom.parseString(xml_str)
    pretty_xml = reparsed.toprettyxml(indent="  ")
    
    output_file = "starzplay_epg.xml"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(pretty_xml)
        
    print(f"[{datetime.now()}] Saved successfully to {output_file}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true", help="Run only once")
    parser.add_argument("--interval", type=int, default=12, help="Interval in hours")
    args = parser.parse_args()

    if args.once:
        fetch_epg()
    else:
        print(f"Starting scheduled EPG fetch every {args.interval} hours.")
        while True:
            fetch_epg()
            sleep_time = args.interval * 3600
            print(f"Sleeping for {args.interval} hours until next run...")
            time.sleep(sleep_time)
