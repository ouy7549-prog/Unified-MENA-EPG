import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
import xml.dom.minidom

# تعديل: السكريبت الآن يحدد تاريخ اليوم تلقائياً بصيغة YYYY-MM-DD
TODAY_DATE = datetime.now().strftime('%Y-%m-%d')
API_URL = f"https://prod-cdn-content-api.intigral-ott.net/content-api-3.0.1/channels/schedules/{TODAY_DATE}/3?apikey=GDMPrdExy0sVDlZMzNDdUyZ"
OUTPUT_FILE = "epg_guide.xml"

def fetch_data(url):
    print(f"Fetching data for {TODAY_DATE} from API...")
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

def format_time(timestamp_ms):
    # تحويل الملي ثانية إلى ثواني ثم إلى تنسيق XMLTV
    dt = datetime.fromtimestamp(timestamp_ms / 1000.0, timezone.utc)
    return dt.strftime('%Y%m%d%H%M%S +0000')

def generate_xmltv(data):
    if not data:
        return None
    
    print("Converting JSON data to XMLTV format...")
    tv_elem = ET.Element('tv', {'generator-info-name': 'STC TV EPG Extractor'})
    
    for channel_data in data:
        raw_channel_id = channel_data.get('channelId', '')
        channel_id = raw_channel_id.split('/')[-1] if raw_channel_id else 'unknown_channel'
        
        # إعداد بيانات القناة
        channel_elem = ET.SubElement(tv_elem, 'channel', {'id': channel_id})
        display_name = ET.SubElement(channel_elem, 'display-name')
        display_name.text = f"Channel {channel_id}"
        
        listings = channel_data.get('listings', [])
        for listing in listings:
            start_time = listing.get('startTime')
            end_time = listing.get('endTime')
            
            if not start_time or not end_time:
                continue
                
            prog_elem = ET.SubElement(tv_elem, 'programme', {
                'start': format_time(start_time),
                'stop': format_time(end_time),
                'channel': channel_id
            })
            
            # العناوين (الأولوية للغة العربية)
            title_text = listing.get('localizedTitle', {}).get('ar') or listing.get('title', '')
            title_elem = ET.SubElement(prog_elem, 'title', {'lang': 'ar'})
            title_elem.text = title_text
            
            # الوصف
            desc_text = listing.get('localizedDescription', {}).get('ar') or listing.get('description', '')
            if desc_text:
                desc_elem = ET.SubElement(prog_elem, 'desc', {'lang': 'ar'})
                desc_elem.text = desc_text
                
            # أيقونة البرنامج
            images = listing.get('images', [])
            if images and isinstance(images, list) and len(images) > 0:
                image_url = images[0].get('imageUrl')
                if image_url:
                    ET.SubElement(prog_elem, 'icon', {'src': image_url})
                    
    # تنسيق الـ XML بشكل جميل (Pretty Print)
    xml_str = ET.tostring(tv_elem, encoding='utf-8')
    parsed_xml = xml.dom.minidom.parseString(xml_str)
    return parsed_xml.toprettyxml(indent="  ")

def main():
    data = fetch_data(API_URL)
    if data:
        xml_content = generate_xmltv(data)
        if xml_content:
            with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
                f.write(xml_content)
            print(f"Success! EPG Guide saved to '{OUTPUT_FILE}' for date {TODAY_DATE}")
    else:
        print("Failed to update EPG. Check API or Internet connection.")

if __name__ == '__main__':
    main()
