def fetch_beIN_3_days(root):
    categories = ['sports', 'entertainment']
    for i in range(3):
        current_date = (datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d')
        # نظام beIN يستخدم offset رقمي (0, 1, 2)
        offset = str(i) 
        
        for cat in categories:
            print(f"📡 [beIN {cat}] جاري محاولة سحب بيانات يوم: {current_date}...")
            url = f"https://www.bein.com/ar/epg-ajax-template/"
            params = {
                'action': 'epg_fetch',
                'offset': offset,
                'category': cat,
                'serviceidentity': 'bein.net',
                'language': 'AR'
            }
            
            try:
                # أضفنا مهلة زمنية (timeout) للتأكد من عدم تعليق السكربت
                response = requests.get(url, params=params, headers=HEADERS, timeout=20)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # محاولة البحث عن الحاويات بأسلوب أكثر شمولاً
                channels_html = soup.find_all('div', class_='channel-item')
                
                if not channels_html:
                    print(f"⚠️ لم يتم العثور على قنوات في {cat} لهذا اليوم. قد يكون الموقع غير هيكلته أو قام بحظر الطلب.")
                    continue

                print(f"✅ تم العثور على {len(channels_html)} قناة في فئة {cat}")

                for ch_item in channels_html:
                    ch_name_tag = ch_item.find('div', class_='channel-name') or ch_item.find('h3')
                    if not ch_name_tag: continue
                    
                    ch_display_name = ch_name_tag.text.strip()
                    ch_id = f"beIN_{ch_display_name.replace(' ', '_')}"
                    
                    if root.find(f"channel[@id='{ch_id}']") is None:
                        chan_el = ET.SubElement(root, "channel", id=ch_id)
                        ET.SubElement(chan_el, "display-name").text = ch_display_name

                    # البحث عن البرامج
                    programs_html = ch_item.find_all('li', class_='program-item')
                    for prog_item in programs_html:
                        title_tag = prog_item.find('h3') or prog_item.find('div', class_='title')
                        if not title_tag: continue
                        
                        title = title_tag.text.strip()
                        
                        # توقيت تقريبي لضمان ظهور البرنامج في الدليل
                        start_time = datetime.strptime(current_date, "%Y-%m-%d").strftime('%Y%m%d000000 +0000')
                        stop_time = datetime.strptime(current_date, "%Y-%m-%d").strftime('%Y%m%d235959 +0000')

                        prog = ET.SubElement(root, "programme", start=start_time, stop=stop_time, channel=ch_id)
                        ET.SubElement(prog, "title", lang="ar").text = title
            except Exception as e:
                print(f"⚠️ خطأ أثناء جلب beIN: {e}")
