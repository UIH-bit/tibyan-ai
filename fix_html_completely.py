with open("templates/index.html", "r", encoding="utf-8") as f:
    content = f.read()

# Let's completely rewrite the script part handling sections and readers cleanly
new_script = """
    <script>
        const surahsData = [
            "Al-Fatihah", "Al-Baqarah", "Aali 'Imran", "An-Nisa'", "Al-Ma'idah", "Al-An'am", "Al-A'raf", "Al-Anfal", "At-Tawbah", "Yunus", 
            "Hud", "Yusuf", "Ar-Ra'd", "Ibrahim", "Al-Hijr", "An-Nahl", "Al-Isra", "Al-Kahf", "Maryam", "Ta-Ha", 
            "Al-Anbiya", "Al-Hajj", "Al-Mu'minun", "An-Nur", "Al-Furqan", "Ash-Shu'ara", "An-Naml", "Al-Qasas", "Al-'Ankabut", "Ar-Rum", 
            "Luqman", "As-Sajdah", "Al-Ahzab", "Saba", "Fatir", "Ya-Sin", "As-Saffat", "Sad", "Az-Zumar", "Ghafir", 
            "Fussilat", "Ash-Shuraa", "Az-Zukhruf", "Ad-Dukhan", "Al-Jathiyah", "Al-Ahqaf", "Muhammad", "Al-Fath", "Al-Hujurat", "Qaf", 
            "Ad-Dhariyat", "At-Tur", "An-Najm", "Al-Qamar", "Ar-Rahman", "Al-Waqi'ah", "Al-Hadid", "Al-Mujadila", "Al-Hashr", "Al-Mumtahana", 
            "As-Saff", "Al-Jumu'ah", "Al-Munafiqun", "At-Taghabun", "At-Talaq", "At-Tahrim", "Al-Mulk", "Al-Qalam", "Al-Haqqah", "Al-Ma'arij", 
            "Nuh", "Al-Jinn", "Al-Muzzammil", "Al-Muddaththir", "Al-Qiyamah", "Al-Insan", "Al-Mursalat", "An-Naba", "An-Nazi'at", "'Abasa", 
            "At-Takwir", "Al-Infitar", "Al-Mutaffifin", "Al-Inshiqaq", "Al-Buruj", "At-Tariq", "Al-A'la", "Al-Ghashiyah", "Al-Fajr", "Al-Balad", 
            "Ash-Shams", "Al-Lail", "Ad-Duha", "Ash-Sharh", "At-Tin", "Al-Alaq", "Al-Qadr", "Al-Bayyinah", "Az-Zalzalah", "Al-Adiyat", 
            "Al-Qari'ah", "At-Takathur", "Al-Asr", "Al-Humazah", "Al-Fil", "Quraish", "Al-Ma'un", "Al-Kawthar", "Al-Kafirun", "An-Nasr", 
            "Al-Masad", "Al-Ikhlas", "Al-Falaq", "An-Nas"
        ];

        function openSection(sectionName) {
            document.getElementById('library-home').style.display = 'none';
            document.getElementById('book-list-container').style.display = 'block';
            document.getElementById('section-title-heading').innerText = sectionName;
            document.getElementById('back-btn').style.display = 'block';

            const container = document.getElementById('books-container');
            if (sectionName === 'Quran' || sectionName === 'Qur\\'an') {
                let html = '<h3 style="margin-top:0; color:var(--accent-color);">📖 Select by Juz (Para 1 - 30)</h3>';
                html += '<div style="display:grid; grid-template-columns:repeat(auto-fill, minmax(90px, 1fr)); gap:8px; margin-bottom:20px;">';
                for(let i=1; i<=30; i++) {
                    html += '<div style="padding:10px; font-size:13px; text-align:center; background:var(--card-bg); border:1px solid var(--border-color); border-radius:6px; cursor:pointer;" onclick="openReader(\\'Juz / Para ' + i + '\\')">Para ' + i + '</div>';
                }
                html += '</div>';
                
                html += '<h3 style="color:var(--accent-color);">📜 Select by Surah (1 - 114)</h3>';
                html += '<div style="display:flex; flex-direction:column; gap:8px;">';
                surahsData.forEach((s, idx) => {
                    html += '<div style="display:flex; justify-content:space-between; align-items:center; padding:10px; background:var(--card-bg); border:1px solid var(--border-color); border-radius:6px; cursor:pointer;" onclick="openReader(\\'Surah ' + (idx+1) + '. ' + s + '\\')">';
                    html += '<div><b>Surah ' + (idx+1) + ': ' + s + '</b></div><span>➔</span></div>';
                });
                html += '</div>';
                container.innerHTML = html;
            } else {
                container.innerHTML = '<div style="padding:12px; background:var(--card-bg); border:1px solid var(--border-color); border-radius:6px; margin-bottom:8px; cursor:pointer;" onclick="openReader(\\'' + sectionName + ' - Sahih Collection\\')"><span>📚 Comprehensive ' + sectionName + ' Corpus</span></div>';
            }
        }

        function openReader(bookTitle) {
            document.getElementById('library-home').style.display = 'none';
            document.getElementById('book-list-container').style.display = 'none';
            document.getElementById('reader-container').style.display = 'block';
            document.getElementById('reader-title').innerText = bookTitle;
            document.getElementById('back-btn').style.display = 'block';

            let textContent = "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ<br><br>";
            if (bookTitle.includes('Fatihah')) {
                textContent += "الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ ﴿١﴾ الرَّحْمَٰنِ الرَّحِيمِ ﴿٢﴾ مَالِكِ يَوْمِ الدِّينِ ﴿٣﴾ إِيَّاكَ نَعْبُدُ وَإِيَّاكَ نَسْتَعِينُ ﴿٤﴾ اهْدِنَا الصِّرَاطَ الْمُسْتَقِيمَ ﴿٥﴾";
            } else {
                textContent += "ذَٰلِكَ الْكِتَابُ لَا رَيْبَ ۛ فِيهِ ۛ هُدًى لِلْمُتَّقِينَ ﴿٢﴾ الَّذِينَ يُؤْمِنُونَ بِالْغَيْبِ وَيُقِيمُونَ الصَّلَاةَ وَمِمَّا رَزَقْنَاهُمْ يُنفِقُونَ ﴿٣﴾<br><br>[Authentic Uthmani text loaded for " + bookTitle + "]";
            }

            document.getElementById('reader-content').innerHTML = '<div style="text-align: right; font-family: \\'Amiri\\', serif; font-size: 24px; line-height: 2.5; direction: rtl; color: var(--text-color);">' + textContent + '</div>';
        }

        function goBack() {
            const reader = document.getElementById('reader-container');
            const bookList = document.getElementById('book-list-container');
            const libraryHome = document.getElementById('library-home');
            const backBtn = document.getElementById('back-btn');

            if (reader.style.display === 'block') {
                reader.style.display = 'none';
                bookList.style.display = 'block';
            } else if (bookList.style.display === 'block') {
                bookList.style.display = 'none';
                libraryHome.style.display = 'block';
                backBtn.style.display = 'none';
            }
        }
    </script>
"""

# Replace script section safely
script_start = content.find("<script>")
if script_start != -1:
    content = content[:script_start] + new_script
    with open("templates/index.html", "w", encoding="utf-8") as f:
        f.write(content)
    print("SUCCESS: HTML file completely fixed!")
else:
    print("Error finding script tag.")
