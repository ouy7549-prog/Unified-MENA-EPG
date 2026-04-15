# Starzplay EPG Scraper

هذا المشروع عبارة عن سكريبت (Python) يقوم بتحديث واستخراج دليل البرامج التلفزيونية (EPG) لقنوات Starzplay المباشرة بشكل دوري وتلقائي بصيغة `XMLTV` القياسية.

## المميزات
- استخراج EPG لأكثر من 120 قناة من قنوات Starzplay.
- يعمل بشكل تلقائي (مجدول) باستخدام GitHub Actions ليقوم بتحديث الدليل يومياً.
- يقوم بحفظ دليل البرامج (الجدول الزمني) بصيغة `starzplay_epg.xml` الجاهزة للربط مع تطبيقات IPTV ومشغلات البث.

## التشغيل المحلي (على جهازك)

**1. تثبيت المتطلبات:**
تأكد من وجود Python، ثم قم بتثبيت الحزمة المطلوبة `requests`:
```bash
pip install -r requirements.txt
```

**2. تشغيل السكريبت لمرة واحدة:**
```bash
python starzplay_epg_scraper.py --once
```

**3. تشغيل السكريبت في الخلفية (كل 12 ساعة افتراضياً):**
```bash
python starzplay_epg_scraper.py
```

يمكنك تعديل المدة عن طريق `--interval` متبوعاً بعدد الساعات:
```bash
python starzplay_epg_scraper.py --interval 24
```

## التحديث التلقائي عبر GitHub Actions (موصى به)

قمنا بتجهيز ملف GitHub Actions داخل المسار `.github/workflows/main.yml`. بمجرد رفعك لهذه الملفات على مساحة (Repository) في حسابك على قيت هب:
1. سيقوم السيرفر الخاص بـ GitHub بتشغيل هذا السكريبت تلقائياً كل يوم في الساعة 12:00 منتصف الليل بوقت جرينتش.
2. سيقوم تلقائياً بتحديث ملف `starzplay_epg.xml` ورفعه (Commit) إلى المستودع الخاص بك.
3. يمكنك استخدام رابط الملف الخام (Raw) كـ EPG URL مباشر داخل تطبيق الـ IPTV الخاص بك ليتم تحديثه تلقائياً كل يوم دون أي تدخل منك!

**الرابط المباشر للملف (بعد الرفع لـ Github):**
سيكون بصيغة:
`https://raw.githubusercontent.com/[YOUR_USERNAME]/[REPO_NAME]/main/starzplay_epg.xml`
