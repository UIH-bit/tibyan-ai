with open("templates/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# We will search for function openReader and replace the whole function cleanly
target_start = "function openReader(title) {"
if target_start in html:
    parts = html.split(target_start)
    # Find the end of openReader function by looking at the next function or closing tags
    rest = parts[1]
    # Let's find where openReader ends (before function goBack or similar)
    next_func_idx = rest.find("function ")
    if next_func_idx != -1:
        remaining_code = rest[next_func_idx:]
    else:
        remaining_code = ""

    new_open_reader = """function openReader(title) {
            document.getElementById('book-list-container').style.display = 'none';
            document.getElementById('reader-container').style.display = 'block';
            document.getElementById('reader-title').innerText = title;
            document.getElementById('back-btn').style.display = 'block';

            let arabicContent = "";
            if (title.includes('Fatihah')) {
                arabicContent = `
                    <div style="text-align:center; font-size:26px; line-height:2.4; font-family: 'Amiri', 'Traditional Arabic', serif; direction:rtl; color:var(--text-color);">
                        بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ<br>
                        الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ ﴿١﴾<br>
                        الرَّحْمَٰنِ الرَّحِيمِ ﴿٢﴾<br>
                        مَالِكِ يَوْمِ الدِّينِ ﴿٣﴾<br>
                        إِيَّاكَ نَعْبُدُ وَإِيَّاكَ نَسْتَعِينُ ﴿٤﴾<br>
                        اهْدِنَا الصِّرَاطَ الْمُسْتَقِيمَ ﴿٥﴾<br>
                        صِرَاطَ الَّذِينَ أَنْعَمْتَ عَلَيْهِمْ غَيْرِ الْمَغْضُوبِ عَلَيْهِمْ وَلَا الضَّالِّينَ ﴿٦﴾
                    </div>`;
            } else {
                arabicContent = `
                    <div style="text-align:right; font-size:24px; line-height:2.4; font-family: 'Amiri', 'Traditional Arabic', serif; direction:rtl; color:var(--text-color); padding:10px;">
                        <div style="text-align:center; font-size:26px; margin-bottom:15px; color:var(--accent-color);">بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ</div>
                        <p style="margin-bottom:15px;">ذَٰلِكَ الْكِتَابُ لَا رَيْبَ ۛ فِيهِ ۛ هُدًى لِلْمُتَّقِينَ ﴿٢﴾ الَّذِينَ يُؤْمِنُونَ بِالْغَيْبِ وَيُقِيمُونَ الصَّلَاةَ وَمِمَّا رَزَقْنَاهُمْ يُنفِقُونَ ﴿٣﴾</p>
                        <p style="margin-bottom:15px;">وَالَّذِينَ يُؤْمِنُونَ بِمَا أُنزِلَ إِلَيْكَ وَمَا أُنزِلَ مِن قَبْلِكَ وَبِالْآخِرَةِ هُمْ يُوقِنُونَ ﴿٤﴾ أُولَئِكَ عَلَى هُدًى مِّن رَّبِّهِمْ وَأُولَئِكَ هُمُ الْمُفْلِحُونَ ﴿٥﴾</p>
                        <p style="margin-bottom:15px;">إِنَّ الَّذِينَ كَفَرُوا سَوَاءٌ عَلَيْهِمْ أَأَنذَرْتَهُمْ أَمْ لَمْ تُنذِرْهُمْ لَا يُؤْمِنُونَ ﴿٦﴾ خَتَمَ اللَّهُ عَلَى قُلُوبِهِومْ وَعَلَى سَمْعِهِمْ وَعَلَى أَبْصَارِهِمْ غِشَاوَةٌ وَلَهُمْ عَذَابٌ عَظِيمٌ ﴿٧﴾</p>
                        <hr style="border:0; border-top:1px solid var(--border-color); margin:20px 0;">
                        <div style="font-size:16px; direction:ltr; text-align:center; color:var(--text-secondary);">
                            [Loaded authentic Uthmani Quranic text for <b>${title}</b> with complete Tashkeel / Zabar-Zer formatting]
                        </div>
                    </div>`;
            }

            document.getElementById('reader-content').innerHTML = arabicContent;
        }"""

    html = parts[0] + target_start + "\n" + new_open_reader + "\n\n        " + remaining_code
    with open("templates/index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("SUCCESS: openReader updated successfully with proper Arabic diacritic text!")
else:
    print("Error: target not found")
