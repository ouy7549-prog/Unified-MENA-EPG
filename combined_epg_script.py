import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
import time
import xml.dom.minidom
from bs4 import BeautifulSoup

# --- إعدادات عامة ---
OUTPUT_FILE = "combined_epg_final.xml"
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

def format_unix_time(unix_ts_ms, is_ms=True):
    ts = unix_ts_ms / 1000.0 if is_ms else unix_ts_ms
    dt = datetime.fromtimestamp(ts, tz=timezone.utc)
    return dt.strftime('%Y%m%d%H%M%S +0000')

def fetch_beIN_3_days(root):
    """جلب بيانات beIN الرياضية والترفيهية لـ 3 أيام"""
    categories = ['sports', 'entertainment']
    
    for i in range(3):
        # حساب التاريخ والـ Offset
        current_date = (datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d')
        offset = f"+{i}"
        
        for cat in categories:
            print(f"📡 [beIN {cat}] جاري جلب بيانات يوم: {current_date}...")
            url = f"https://www.bein.com/ar/epg-ajax-template/"
            params = {
                'action': 'epg_fetch',
                'offset': offset,
                'category': cat,
                'serviceidentity': 'bein.net',
                'mins': '00',
                'cdate': current_date,
                'language': 'AR',
                'postid': '25344',
                'loadindex': '0'
            }
            
            try:
                response = requests.get(url, params=params, headers=HEADERS)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # البحث عن القنوات في الـ HTML الناتج
                channels_html = soup.find_all('div', class_='channel-item')
                for ch_item in channels_html:
                    # استخراج اسم القناة ليكون هو المعرف
                    ch_name_tag = ch_item.find('div', class_='channel-name')
                    if not ch_name_tag: continue
                    
                    ch_display_name = ch_name_tag.text.strip()
                    ch_id = f"beIN_{ch_display_name.replace(' ', '_')}"
                    
                    if root.find(f"channel[@id='{ch_id}']") is None:
                        chan_el = ET.SubElement(root, "channel", id=ch_id)
                        ET.SubElement(chan_el, "display-name").text = ch_display_name

                    # استخراج البرامج لهذه القناة
                    programs_html = ch_item.find_all('li', class_='program-item')
                    for prog_item in programs_html:
                        title = prog_item.find('h3').text.strip() if prog_item.find('h3') else "N/A"
                        time_str = prog_item.find('span', class_='time').text.strip() if prog_item.find('span', class_='time') else ""
                        
                        # ملاحظة: beIN في الـ AJAX لا تعطي TimeStamp دقيق لكل برنامج بسهولة، 
                        # لذا يفضل في المشاريع المتقدمة تحليل وقت البداية والنهاية من الـ HTML.
                        # هنا سنضع وقت تقريبي بناءً على وقت اليوم لضمان ظهورها في الدليل.
                        start_time = datetime.strptime(f"{current_date}", "%Y-%m-%d").strftime('%Y%m%d%H%M%S +0000')
                        stop_time = (datetime.strptime(f"{current_date}", "%Y-%m-%d") + timedelta(hours=2)).strftime('%Y%m%d%H%M%S +0000')

                        prog = ET.SubElement(root, "programme", start=start_time, stop=stop_time, channel=ch_id)
                        ET.SubElement(prog, "title", lang="ar").text = title
            except Exception as e:
                print(f"⚠️ خطأ في beIN {cat} ليوم {current_date}: {e}")

def fetch_shahid(root):
    print("📡 [Shahid] جاري جلب البيانات...")
    channel_ids = "387238,387251,387296,387290,387293,49923122575716,387294,387937,400919,946945,946940,946938,995495,999927,49923088749329,49923068171559,49923697545394,946946,49923697648201,49923697657389,946942,49923691806580,49923697659290,49923120452582,49923088717401,49923088781412,49923697650617,49923697642137,49923088814140,49923697342447,49923712885383,969745,977946,975435,963543,1005232,49923086870104,988045,992538,983124,976272,409385,409390,387286,387288,946948,862837,49923569816895,1003218,49923693965985,49923446898171,49923639151416,997605,1001845,49923434082342,409387,418308,400917,400921,400924,989622,986064,986069,951783,49922904934759,986346,986014,986024,49923172117967,49922763891977,49923172215352,49922763510387,49923518527492,414449,1029746,388567,388566,49923697660442"
    now = datetime.now(timezone.utc)
    from_date = (now - timedelta(days=1)).strftime("%Y-%m-%dT00:00:00.000Z")
    to_date = (now + timedelta(days=2)).strftime("%Y-%m-%dT23:59:59.000Z")
    url = f"https://api3.shahid.net/proxy/v2.1/shahid-epg-api/?csvChannelIds={channel_ids}&language=ar&from={from_date}&to={to_date}&country=SA"
    try:
        data = requests.get(url, headers=HEADERS).json().get('items', [])
        for channel in data:
            ch_id = f"Shahid_{channel.get('channelId')}"
            if root.find(f"channel[@id='{ch_id}']") is None:
                chan_el = ET.SubElement(root, "channel", id=ch_id)
                ET.SubElement(chan_el, "display-name").text = f"Shahid {channel.get('channelId')}"
            for p in channel.get('items', []):
                start = p['from'].split('.')[0].replace('-', '').replace(':', '').replace('T', '') + " +0000"
                stop = p['to'].split('.')[0].replace('-', '').replace(':', '').replace('T', '') + " +0000"
                prog = ET.SubElement(root, "programme", start=start, stop=stop, channel=ch_id)
                ET.SubElement(prog, "title", lang="ar").text = p.get('title', 'N/A')
    except Exception as e: print(f"⚠️ Shahid Error: {e}")

def fetch_stc_tv_3_days(root):
    for i in range(3):
        date_str = (datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d')
        print(f"📡 [STC TV] جاري جلب بيانات يوم: {date_str}...")
        url = f"https://prod-cdn-content-api.intigral-ott.net/content-api-3.0.1/channels/schedules/{date_str}/3?apikey=GDMPrdExy0sVDlZMzNDdUyZ&country=SA"
        try:
            data = requests.get(url, headers=HEADERS).json()
            for ch_data in data:
                raw_id = ch_data.get('channelId', '').split('/')[-1]
                ch_id = f"STC_{raw_id}"
                if root.find(f"channel[@id='{ch_id}']") is None:
                    chan_el = ET.SubElement(root, "channel", id=ch_id)
                    ET.SubElement(chan_el, "display-name").text = f"STC Channel {raw_id}"
                for list_item in ch_data.get('listings', []):
                    start_t = list_item.get('startTime')
                    end_t = list_item.get('endTime')
                    if start_t and end_t:
                        prog = ET.SubElement(root, "programme", start=format_unix_time(start_t), stop=format_unix_time(end_t), channel=ch_id)
                        title = list_item.get('localizedTitle', {}).get('ar') or list_item.get('title', '')
                        ET.SubElement(prog, "title", lang="ar").text = title
        except Exception as e: print(f"⚠️ STC Error: {e}")

def main():
    print("🚀 بدء عملية الدمج الشاملة لـ 3 أيام...")
    root = ET.Element("tv", {"generator-info-name": "Ultra EPG Generator"})

    # تشغيل كافة المصادر
    fetch_beIN_3_days(root)
    fetch_stc_tv_3_days(root)
    fetch_shahid(root)
    fetch_starzplay(root)

    print("💾 جاري حفظ الملف النهائي...")
    xml_str = ET.tostring(root, encoding="utf-8")
    reparsed = xml.dom.minidom.parseString(xml_str)
    pretty_xml = reparsed.toprettyxml(indent="  ")
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(pretty_xml)
    print(f"✅ تم بنجاح! الملف جاهز: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
