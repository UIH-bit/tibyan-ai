with open("templates/index.html", "r", encoding="utf-8") as f:
    content = f.read()

# Let's completely replace the openSection function implementation
start_marker = "function openSection(sectionName) {"
end_marker = "        }"

# We will look for a clean replacement or inject it directly
new_function = """function openSection(sectionName) {
            document.getElementById('library-home').style.display = 'none';
            document.getElementById('book-list-container').style.display = 'block';
            document.getElementById('section-title-heading').innerText = sectionName;
            document.getElementById('back-btn').style.display = 'block';

            const container = document.getElementById('books-container');
            if (sectionName === 'Quran' || sectionName === 'Qur\\'an') {
                let html = '<h3 style="margin-top:0; color:var(--accent-color);">📖 Select by Juz (Para 1 - 30)</h3><div style="display:grid; grid-template-columns:repeat(auto-fill, minmax(100px, 1fr)); gap:10px; margin-bottom:20px;">';
                for(let i=1; i<=30; i++) {
                    html += `<div class="library-card" style="padding:10px; font-size:13px; text-align:center; background:var(--card-bg); border:1px solid var(--border-color); border-radius:6px; cursor:pointer;" onclick="openReader('Juz / Para ${i}')">Para ${i}</div>`;
                }
                html += '</div><h3 style="color:var(--accent-color);">📜 Select by Surah (1 - 114 with Meanings)</h3><div style="display:flex; flex-direction:column; gap:8px;">';
                
                const sampleSurahs = [
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
                ];

                sampleSurahs.forEach((item, idx) => {
                    html += `<div class="book-item" onclick="openReader('Surah ${idx+1}. ${item.n}')" style="display:flex; justify-content:space-between; align-items:center; padding:10px; margin-bottom:6px; background:var(--card-bg); border:1px solid var(--border-color); border-radius:6px; cursor:pointer;">
                        <div><b>Surah ${idx+1}: ${item.n}</b><br><small style="color:var(--text-secondary);">${item.meaning}</small></div>
                        <span>➔</span>
                    </div>`;
                });
                html += '</div>';
                container.innerHTML = html;
            } else {
                container.innerHTML = `
                    <div class="book-item" onclick="openReader('${sectionName} - Sahih Authentic Collection')">
                        <span>📚 Comprehensive ${sectionName} Corpus (Vol. 1)</span><span>➔</span>
                    </div>
                    <div class="book-item" onclick="openReader('${sectionName} - Classical Master Texts')">
                        <span>📖 Classical Master Texts & Commentary</span><span>➔</span>
                    </div>
                `;
            }
        }"""

# Find and replace openSection function safely
if start_marker in content:
    # Find start and closing of openSection roughly or replace the whole function block
    start_pos = content.find(start_marker)
    # Let's find a secure way: replace old openSection till its closing brace
    # Or write a robust find-replace based on unique markers
    print("Found openSection function, applying force update...")
    
    # Safe replacement using python string slicing or marker identification
    # Let's write a clean script that replaces from function openSection up to the next main function
    next_func_pos = content.find("function openReader", start_pos)
    if next_func_pos != -1:
        content = content[:start_pos] + new_function + "\n\n        " + content[next_func_pos:]
        with open("templates/index.html", "w", encoding="utf-8") as f:
            f.write(content)
        print("SUCCESSFULLY forced update on index.html!")
    else:
        print("Error finding next function block.")
else:
    print("Marker not found.")
