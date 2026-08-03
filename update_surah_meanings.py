with open("templates/index.html", "r", encoding="utf-8") as f:
    code = f.read()

# Replace Surah list generation to include meanings
old_surah_part = 'const sampleSurahs = ["Al-Fatihah", "Al-Baqarah", "Aali \'Imran", "An-Nisa\'", "Al-Ma\'idah", "Al-An\'am", "Al-A\'raf", "Al-Anfal", "At-Tawbah", "Yunus", "Hud", "Yusuf", "Ar-Ra\'d", "Ibrahim", "Al-Hijr", "An-Nahl", "Al-Isra", "Al-Kahf", "Maryam", "Ta-Ha", "Al-Anbiya", "Al-Hajj", "Al-Mu\'minun", "An-Nur", "Al-Furqan", "Ash-Shu\'ara", "An-Naml", "Al-Qasas", "Al-\'Ankabut", "Ar-Rum", "Luqman", "As-Sajdah", "Al-Ahzab", "Saba", "Fatir", "Ya-Sin", "As-Saffat", "Sad", "Az-Zumar", "Ghafir", "Fussilat", "Ash-Shuraa", "Az-Zukhruf", "Ad-Dukhan", "Al-Jathiyah", "Al-Ahqaf", "Muhammad", "Al-Fath", "Al-Hujurat", "Qaf", "Ad-Dhariyat", "At-Tur", "An-Najm", "Al-Qamar", "Ar-Rahman", "Al-Waqi\'ah", "Al-Hadid", "Al-Mujadila", "Al-Hashr", "Al-Mumtahana", "As-Saff", "Al-Jumu\'ah", "Al-Munafiqun", "At-Taghabun", "At-Talaq", "At-Tahrim", "Al-Mulk", "Al-Qalam", "Al-Haqqah", "Al-Ma\'arij", "Nuh", "Al-Jinn", "Al-Muzzammil", "Al-Muddaththir", "Al-Qiyamah", "Al-Insan", "Al-Mursalat", "An-Naba", "An-Nazi\'at", "\'Abasa", "At-Takwir", "Al-Infitar", "Al-Mutaffifin", "Al-Inshiqaq", "Al-Buruj", "At-Tariq", "Al-A\'la", "Al-Ghashiyah", "Al-Fajr", "Al-Balad", "Ash-Shams", "Al-Lail", "Ad-Duha", "Ash-Sharh", "At-Tin", "Al-Alaq", "Al-Qadr", "Al-Bayyinah", "Az-Zalzalah", "Al-\'Adiyat", "Al-Qari\'ah", "At-Takathur", "Al-Asr", "Al-Humazah", "Al-Fil", "Quraish", "Al-Ma\'un", "Al-Kawthar", "Al-Kafirun", "An-Nasr", "Al-Masad", "Al-Ikhlas", "Al-Falaq", "An-Nas"];'

new_surah_part = '''const sampleSurahs = [
    {n: "Al-Fatihah", meaning: "The Opening (الفتحة)"},
    {n: "Al-Baqarah", meaning: "The Cow (البقرة)"},
    {n: "Aali 'Imran", meaning: "The Family of Imran (آل عمران)"},
    {n: "An-Nisa'", meaning: "The Women (النساء)"},
    {n: "Al-Ma'idah", meaning: "The Table Spread (المائدة)"},
    {n: "Al-An'am", meaning: "The Cattle (الأنعام)"},
    {n: "Al-A'raf", meaning: "The Heights (الأعراف)"},
    {n: "Al-Anfal", meaning: "The Spoils of War (الأنفال)"},
    {n: "At-Tawbah", meaning: "The Repentance (التوبة)"},
    {n: "Yunus", meaning: "Prophet Jonah (يونس)"},
    {n: "Hud", meaning: "Prophet Hud (هود)"},
    {n: "Yusuf", meaning: "Prophet Joseph (يوسف)"},
    {n: "Ar-Ra'd", meaning: "The Thunder (الرعد)"},
    {n: "Ibrahim", meaning: "Prophet Abraham (إبراهيم)"},
    {n: "Al-Hijr", meaning: "The Rocky Tract (الحجر)"},
    {n: "An-Nahl", meaning: "The Bee (النحل)"},
    {n: "Al-Isra", meaning: "The Night Journey (الإسراء)"},
    {n: "Al-Kahf", meaning: "The Cave (الكهف)"},
    {n: "Maryam", meaning: "Mary (مريم)"},
    {n: "Ta-Ha", meaning: "Ta-Ha (طه)"},
    {n: "Al-Anbiya", meaning: "The Prophets (الأنبياء)"},
    {n: "Al-Hajj", meaning: "The Pilgrimage (الحج)"},
    {n: "Al-Mu'minun", meaning: "The Believers (المؤمنون)"},
    {n: "An-Nur", meaning: "The Light (النور)"},
    {n: "Al-Furqan", meaning: "The Criterion (الفرقان)"},
    {n: "Ash-Shu'ara", meaning: "The Poets (الشعراء)"},
    {n: "An-Naml", meaning: "The Ant (النمل)"},
    {n: "Al-Qasas", meaning: "The Stories (القصص)"},
    {n: "Al-'Ankabut", meaning: "The Spider (العنكبوت)"},
    {n: "Ar-Rum", meaning: "The Romans (الروم)"},
    {n: "Luqman", meaning: "Luqman the Wise (لقمان)"},
    {n: "As-Sajdah", meaning: "The Prostration (السجدة)"},
    {n: "Al-Ahzab", meaning: "The Combined Forces (الأحزاب)"},
    {n: "Saba", meaning: "Sheba (سبأ)"},
    {n: "Fatir", meaning: "The Originator (فاطر)"},
    {n: "Ya-Sin", meaning: "Ya-Sin (يس)"},
    {n: "As-Saffat", meaning: "Those Ranged in Ranks (الصافات)"},
    {n: "Sad", meaning: "The Letter Sad (ص)"},
    {n: "Az-Zumar", meaning: "The Troops (الزمر)"},
    {n: "Ghafir", meaning: "The Forgiver (غافر)"},
    {n: "Fussilat", meaning: "Explained in Detail (فصلت)"},
    {n: "Ash-Shuraa", meaning: "The Consultation (الشورى)"},
    {n: "Az-Zukhruf", meaning: "The Gold Ornaments (الزخرف)"},
    {n: "Ad-Dukhan", meaning: "The Smoke (الدخان)"},
    {n: "Al-Jathiyah", meaning: "The Crouching (الجاثية)"},
    {n: "Al-Ahqaf", meaning: "The Wind-Curved Sandhills (الأحقاف)"},
    {n: "Muhammad", meaning: "Prophet Muhammad (محمد)"},
    {n: "Al-Fath", meaning: "The Victory (الفَتْح)"},
    {n: "Al-Hujurat", meaning: "The Dwellings (الحجرات)"},
    {n: "Qaf", meaning: "The Letter Qaf (ق)"},
    {n: "Ad-Dhariyat", meaning: "The Winnowing Winds (الذاريات)"},
    {n: "At-Tur", meaning: "The Mount (الطور)"},
    {n: "An-Najm", meaning: "The Star (النجم)"},
    {n: "Al-Qamar", meaning: "The Moon (القمر)"},
    {n: "Ar-Rahman", meaning: "The Beneficent (الرحمن)"},
    {n: "Al-Waqi'ah", meaning: "The Inevitable (واقعة)"},
    {n: "Al-Hadid", meaning: "The Iron (الحديد)"},
    {n: "Al-Mujadila", meaning: "The Pleading Woman (المجادلة)"},
    {n: "Al-Hashr", meaning: "The Exile (الحشر)"},
    {n: "Al-Mumtahana", meaning: "The Tested Woman (الممتحنة)"},
    {n: "As-Saff", meaning: "The Ranks (الصف)"},
    {n: "Al-Jumu'ah", meaning: "Friday (الجمعة)"},
    {n: "Al-Munafiqun", meaning: "The Hypocrites (المنافقون)"},
    {n: "At-Taghabun", meaning: "The Mutual Disillusion (التغابن)"},
    {n: "At-Talaq", meaning: "The Divorce (الطلاق)"},
    {n: "At-Tahrim", meaning: "The Prohibition (التحريم)"},
    {n: "Al-Mulk", meaning: "The Sovereignty (الملك)"},
    {n: "Al-Qalam", meaning: "The Pen (القلم)"},
    {n: "Al-Haqqah", meaning: "The Reality (الحاقة)"},
    {n: "Al-Ma'arij", meaning: "The Ascending Stairways (المعارج)"},
    {n: "Nuh", meaning: "Prophet Noah (نوح)"},
    {n: "Al-Jinn", meaning: "The Jinn (الجن)"},
    {n: "Al-Muzzammil", meaning: "The Enshrouded One (المزمل)"},
    {n: "Al-Muddaththir", meaning: "The Cloaked One (المدثر)"},
    {n: "Al-Qiyamah", meaning: "The Resurrection (القيامة)"},
    {n: "Al-Insan", meaning: "Man (الإنسان)"},
    {n: "Al-Mursalat", meaning: "The Emissaries (المرسلات)"},
    {n: "An-Naba", meaning: "The Tidings (النبأ)"},
    {n: "An-Nazi'at", meaning: "Those Who Drag Forth (النازعات)"},
    {n: "'Abasa", meaning: "He Frowned (عبس)"},
    {n: "At-Takwir", meaning: "The Overthrowing (التكوير)"},
    {n: "Al-Infitar", meaning: "The Cleaving (الانفطار)"},
    {n: "Al-Mutaffifin", meaning: "The Defrauding (المطففين)"},
    {n: "Al-Inshiqaq", meaning: "The Splitting Open (الانشقاق)"},
    {n: "Al-Buruj", meaning: "The Big Stars (البروج)"},
    {n: "At-Tariq", meaning: "The Nightcomer (الطارق)"},
    {n: "Al-A'la", meaning: "The Most High (الأعلى)"},
    {n: "Al-Ghashiyah", meaning: "The Overwhelming (الغاشية)"},
    {n: "Al-Fajr", meaning: "The Dawn (الفجر)"},
    {n: "Al-Balad", meaning: "The City (البلد)"},
    {n: "Ash-Shams", meaning: "The Sun (الشمس)"},
    {n: "Al-Lail", meaning: "The Night (الليل)"},
    {n: "Ad-Duha", meaning: "The Morning Hours (الضحى)"},
    {n: "Ash-Sharh", meaning: "The Relief (الشرح)"},
    {n: "At-Tin", meaning: "The Fig (التين)"},
    {n: "Al-Alaq", meaning: "The Clot (العلق)"},
    {n: "Al-Qadr", meaning: "The Power (القدر)"},
    {n: "Al-Bayyinah", meaning: "The Clear Proof (البينة)"},
    {n: "Az-Zalzalah", meaning: "The Earthquake (الزلزلة)"},
    {n: "Al-Adiyat", meaning: "The Chargers (العاديات)"},
    {n: "Al-Qari'ah", meaning: "The Striking Hour (القارعة)"},
    {n: "At-Takathur", meaning: "The Rivalry in World Increase (التكاثر)"},
    {n: "Al-Asr", meaning: "The Declining Day (العصر)"},
    {n: "Al-Humazah", meaning: "The Traducer (الهمزة)"},
    {n: "Al-Fil", meaning: "The Elephant (الفيل)"},
    {n: "Quraish", meaning: "Quraish Tribe (قريش)"},
    {n: "Al-Ma'un", meaning: "The Small Kindnesses (الماعون)"},
    {n: "Al-Kawthar", meaning: "Abundance (الكوثر)"},
    {n: "Al-Kafirun", meaning: "The Disbelievers (الكافرون)"},
    {n: "An-Nasr", meaning: "The Divine Support (النصر)"},
    {n: "Al-Masad", meaning: "The Palm Fiber (المسد)"},
    {n: "Al-Ikhlas", meaning: "The Sincerity (الإخلاص)"},
    {n: "Al-Falaq", meaning: "The Daybreak (الفلق)"},
    {n: "An-Nas", meaning: "Mankind (الناس)"}
];'''

# Replace loop rendering for surahs
old_loop = 'sampleSurahs.forEach((s, idx) => {'
# Let's check and replace appropriately in the openSection function block
if "sampleSurahs.forEach" in code:
    # We will rewrite the surah rendering part inside openSection
    code = code.replace('const sampleSurahs = ["Al-Fatihah", "Al-Baqarah", "Aali \'Imran", "An-Nisa\'", "Al-Ma\'idah", "Al-An\'am", "Al-A\'raf", "Al-Anfal", "At-Tawbah", "Yunus", "Hud", "Yusuf", "Ar-Ra\'d", "Ibrahim", "Al-Hijr", "An-Nahl", "Al-Isra", "Al-Kahf", "Maryam", "Ta-Ha", "Al-Anbiya", "Al-Hajj", "Al-Mu\'minun", "An-Nur", "Al-Furqan", "Ash-Shu\'ara", "An-Naml", "Al-Qasas", "Al-\'Ankabut", "Ar-Rum", "Luqman", "As-Sajdah", "Al-Ahzab", "Saba", "Fatir", "Ya-Sin", "As-Saffat", "Sad", "Az-Zumar", "Ghafir", "Fussilat", "Ash-Shuraa", "Az-Zukhruf", "Ad-Dukhan", "Al-Jathiyah", "Al-Ahqaf", "Muhammad", "Al-Fath", "Al-Hujurat", "Qaf", "Ad-Dhariyat", "At-Tur", "An-Najm", "Al-Qamar", "Ar-Rahman", "Al-Waqi\'ah", "Al-Hadid", "Al-Mujadila", "Al-Hashr", "Al-Mumtahana", "As-Saff", "Al-Jumu\'ah", "Al-Munafiqun", "At-Taghabun", "At-Talaq", "At-Tahrim", "Al-Mulk", "Al-Qalam", "Al-Haqqah", "Al-Ma\'arij", "Nuh", "Al-Jinn", "Al-Muzzammil", "Al-Muddaththir", "Al-Qiyamah", "Al-Insan", "Al-Mursalat", "An-Naba", "An-Nazi\'at", "\'Abasa", "At-Takwir", "Al-Infitar", "Al-Mutaffifin", "Al-Inshiqaq", "Al-Buruj", "At-Tariq", "Al-A\'la", "Al-Ghashiyah", "Al-Fajr", "Al-Balad", "Ash-Shams", "Al-Lail", "Ad-Duha", "Ash-Sharh", "At-Tin", "Al-Alaq", "Al-Qadr", "Al-Bayyinah", "Az-Zalzalah", "Al-\'Adiyat", "Al-Qari\'ah", "At-Takathur", "Al-Asr", "Al-Humazah", "Al-Fil", "Quraish", "Al-Ma\'un", "Al-Kawthar", "Al-Kafirun", "An-Nasr", "Al-Masad", "Al-Ikhlas", "Al-Falaq", "An-Nas"];', new_surah_part)
    
    old_foreach = '''                sampleSurahs.forEach((s, idx) => {
                    html += `<div class="book-item" onclick="openReader('Surah ${idx+1}. ${s}')"><span>Surah ${idx+1}: ${s}</span><span>➔</span></div>`;
                });'''
                
    new_foreach = '''                sampleSurahs.forEach((item, idx) => {
                    html += `<div class="book-item" onclick="openReader('Surah ${idx+1}. ${item.n}')">
                        <div><b>Surah ${idx+1}: ${item.n}</b><br><small style="color:#6c757d;">Meaning: ${item.meaning}</small></div>
                        <span>➔</span>
                    </div>`;
                });'''
                
    if old_foreach in code:
        code = code.replace(old_foreach, new_foreach)

with open("templates/index.html", "w", encoding="utf-8") as f:
    f.write(code)

print("SUCCESS: Surah meanings list added!")
