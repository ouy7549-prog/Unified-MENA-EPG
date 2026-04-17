import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
import xml.dom.minidom

API_URL = "https://prod-cdn-content-api.intigral-ott.net/content-api-3.0.1/channels/schedules/2026-04-18/3?apikey=GDMPrdExy0sVDlZMzNDdUyZ"
OUTPUT_FILE = "epgs_guide.xml"

def fetch_data(url):
    print(f"Fetching data from API...")
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def format_time(timestamp_ms):
    # Convert milliseconds to seconds
    dt = datetime.fromtimestamp(timestamp_ms / 1000.0, timezone.utc)
    # XMLTV format: YYYYMMDDHHMMSS +0000
    return dt.strftime('%Y%m%d%H%M%S +0000')

def generate_xmltv(data):
    print("Converting JSON data to XMLTV format...")
    tv_elem = ET.Element('tv', {'generator-info-name': 'STC TV EPG Extractor'})
    
    for channel_data in data:
        raw_channel_id = channel_data.get('channelId', '')
        # Clean channel ID (extract the last part from the URL-like ID)
        channel_id = raw_channel_id.split('/')[-1] if raw_channel_id else 'unknown_channel'
        
        # Add channel definition element
        channel_elem = ET.SubElement(tv_elem, 'channel', {'id': channel_id})
        display_name = ET.SubElement(channel_elem, 'display-name')
        
        # We try to get a channel name if it is available in the listings, otherwise use the ID
        listings = channel_data.get('listings', [])
        display_name.text = f"Channel {channel_id}"
        
        for listing in listings:
            start_time = listing.get('startTime')
            end_time = listing.get('endTime')
            
            if not start_time or not end_time:
                continue
                
            # Add programme element
            prog_elem = ET.SubElement(tv_elem, 'programme', {
                'start': format_time(start_time),
                'stop': format_time(end_time),
                'channel': channel_id
            })
            
            # Title (prefer Arabic if available)
            title_text = listing.get('localizedTitle', {}).get('ar') or listing.get('title', '')
            title_elem = ET.SubElement(prog_elem, 'title', {'lang': 'ar'})
            title_elem.text = title_text
            
            # Description
            desc_text = listing.get('localizedDescription', {}).get('ar') or listing.get('description', '')
            if desc_text:
                desc_elem = ET.SubElement(prog_elem, 'desc', {'lang': 'ar'})
                desc_elem.text = desc_text
                
            # Image URL
            images = listing.get('images', [])
            if images and isinstance(images, list) and len(images) > 0:
                image_url = images[0].get('imageUrl')
                if image_url:
                    ET.SubElement(prog_elem, 'icon', {'src': image_url})
                    
    # Format XML nicely
    xml_str = ET.tostring(tv_elem, encoding='utf-8')
    parsed_xml = xml.dom.minidom.parseString(xml_str)
    return parsed_xml.toprettyxml(indent="  ")

def main():
    try:
        data = fetch_data(API_URL)
        xml_content = generate_xmltv(data)
        
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write(xml_content)
            
        print(f"Success! EPG Guide saved to '{OUTPUT_FILE}'")
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    main()
