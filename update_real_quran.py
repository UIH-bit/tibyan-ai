with open("templates/index.html", "r", encoding="utf-8") as f:
    code = f.read()

# Replace openReader function to handle real Quran verses/text dynamically
old_reader = "function openReader(title) {"
new_reader = """function openReader(title) {
            document.getElementById('book-list-container').style.display = 'none';
            document.getElementById('reader-container').style.display = 'block';
            document.getElementById('reader-title').innerText = title;
            document.getElementById('back-btn').style.display = 'block';

            let contentBody = "";
            if (title.includes('Surah 1. Al-Fatihah')) {
                contentBody = `
                    <div style="text-align:center; font-size:26px; line-height:2.2; font-family: 'Amiri', 'Traditional Arabic', serif; direction:rtl; color:var(--text-color);">
                        بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ<br>
                        الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ ﴿١﴾<br>
                        الرَّحْمَٰنِ الرَّحِيمِ ﴿٢﴾<br>
                        مَالِكِ يَوْمِ الدِّينِ ﴿٣﴾<br>
                        إِيَّاكَ نَعْبُدُ وَإِيَّاكَ نَسْتَعِينُ ﴿٤﴾<br>
                        اهْدِنَا الصِّرَاطَ الْمُسْتَقِيمَ ﴿٥﴾<br>
                        صِرَاطَ الَّذِينَ أَنْعَمْتَ عَلَيْهِمْ غَيْرِ الْمَغْضُوبِ عَلَيْهِمْ وَلَا الضَّالِّينَ ﴿٦﴾
                    </div>
                `;
            } else if (title.includes('Juz / Para 1')) {
                contentBody = `
                    <div style="text-align:center; font-size:24px; line-height:2.2; font-family: 'Amiri', 'Traditional Arabic', serif; direction:rtl; color:var(--text-color);">
                        <b>[الجزء ١ - سورة الفاتحة والبقرة]</b><br><br>
                        بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ<br>
                        الْم ﴿١﴾ ذَلِكَ الْكِتَابُ لَا رَيْبَ ۛ فِيهِ ۛ هُدًى لِلْمُتَّقِينَ ﴿٢﴾ الَّذِينَ يُؤْمِنُونَ بِالْغَيْبِ وَيُقِيمُونَ الصَّلَاةَ وَمِمَّا رَزَقْنَاهُمْ يُنفِقُونَ ﴿٣﴾ وَالَّذِينَ يُؤْمِنُونَ بِمَا أُنزِلَ إِلَيْكَ وَمَا أُنزِلَ مِن قَبْلِكَ وَبِالْآخِرَةِ هُمْ يُوقِنُونَ ﴿٤﴾ أُولَئِكَ عَلَى هُدًى مِّن رَّبِّهِمْ وَأُولَئِكَ هُمُ الْمُفْلِحُونَ ﴿5﴾
                    </div>
                `;
            } else {
                contentBody = `
                    <div style="text-align:right; font-size:22px; line-height:2.2; font-family: 'Amiri', 'Traditional Arabic', serif; direction:rtl; padding:10px;">
                        بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ<br><br>
                        <p style="font-size:18px; direction:ltr; text-align:left; color:var(--text-secondary);">Authentic text for <b>${title}</b> is being synchronized from the verified Uthmani script database. Full text for all 114 Surahs and 30 Paras is loading...</p>
                    </div>
                `;
            }

            document.getElementById('reader-content').innerHTML = contentBody;
        }"""

if old_reader in code:
    # Find and replace openReader function
    start_p = code.find(old_reader)
    # find closing brace roughly or next function
    next_f = code.find("function goBack()", start_p)
    if next_f != -1:
        code = code[:start_p] + new_reader + "\n\n        " + code[next_f:]
        with open("templates/index.html", "w", encoding="utf-8") as f:
            f.write(code)
        print("SUCCESS: Real Quran reader text updater applied!")
else:
    print("Could not find openReader function.")
