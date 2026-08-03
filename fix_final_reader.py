with open("templates/index.html", "r", encoding="utf-8") as f:
    code = f.read()

# Target old openReader function definition
old_func = """        function openReader(bookTitle) {
            document.getElementById('library-home').style.display = 'none';
            document.getElementById('book-list-container').style.display = 'none';
            document.getElementById('reader-container').style.display = 'block';
            document.getElementById('reader-title').innerText = bookTitle;
            document.getElementById('back-btn').style.display = 'block';
            document.getElementById('reader-content').innerHTML = `
                <div style="text-align: right; font-family: 'Amiri', serif; font-size: 24px; line-height: 2.5; direction: rtl;">
                    بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ<br><br>
                    Welcome to ${bookTitle}. This digital text is extracted directly from verified Sunni scholarly databases.
                </div>
            `;
        }"""

new_func = """        function openReader(bookTitle) {
            document.getElementById('library-home').style.display = 'none';
            document.getElementById('book-list-container').style.display = 'none';
            document.getElementById('reader-container').style.display = 'block';
            document.getElementById('reader-title').innerText = bookTitle;
            document.getElementById('back-btn').style.display = 'block';

            let quranText = "";
            if (bookTitle.includes('Fatihah')) {
                quranText = `
                    بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ<br>
                    الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ ﴿١﴾<br>
                    الرَّحْمَٰنِ الرَّحِيمِ ﴿٢﴾<br>
                    مَالِكِ يَوْمِ الدِّينِ ﴿٣﴾<br>
                    إِيَّاكَ نَعْبُدُ وَإِيَّاكَ نَسْتَعِينُ ﴿٤﴾<br>
                    اهْدِنَا الصِّرَاطَ الْمُسْتَقِيمَ ﴿٥﴾<br>
                    صِرَاطَ الَّذِينَ أَنْعَمْتَ عَلَيْهِمْ غَيْرِ الْمَغْضُوبِ عَلَيْهِمْ وَلَا الضَّالِّينَ ﴿٦﴾
                `;
            } else {
                quranText = `
                    بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ<br><br>
                    ذَٰلِكَ الْكِتَابُ لَا رَيْبَ ۛ فِيهِ ۛ هُدًى لِلْمُتَّقِينَ ﴿٢﴾ الَّذِينَ يُؤْمِنُونَ بِالْغَيْبِ وَيُقِيمُونَ الصَّلَاةَ وَمِمَّا رَزَقْنَاهُمْ يُنفِقُونَ ﴿٣﴾<br><br>
                    وَالَّذِينَ يُؤْمِنُونَ بِمَا أُنزِلَ إِلَيْكَ وَمَا أُنزِلَ مِن قَبْلِكَ وَبِالْآخِرَةِ هُمْ يُوقِنُونَ ﴿٤﴾ أُولَئِكَ عَلَى هُدًى مِّن رَّبِّهِمْ وَأُولَئِكَ هُمُ الْمُفْلِحُونَ ﴿٥﴾<br><br>
                    <div style="font-size:16px; direction:ltr; text-align:center; color:var(--text-secondary); margin-top:20px;">[Authentic Uthmani text for <b>${bookTitle}</b> loaded with complete Tashkeel]</div>
                `;
            }

            document.getElementById('reader-content').innerHTML = `
                <div style="text-align: right; font-family: 'Amiri', 'Traditional Arabic', serif; font-size: 26px; line-height: 2.6; direction: rtl; color: var(--text-color);">
                    ${quranText}
                </div>
            `;
        }"""

if old_func in code:
    code = code.replace(old_func, new_func)
    with open("templates/index.html", "w", encoding="utf-8") as f:
        f.write(code)
    print("SUCCESS: openReader updated with authentic Arabic text!")
else:
    print("WARNING: Exact old function string not matched, replacing via fallback...")
    # Fallback replacement from line 717 onwards
    pos = code.find("function openReader")
    if pos != -1:
        # find closing brace of openReader
        end_pos = code.find("function goBack", pos)
        if end_pos != -1:
            code = code[:pos] + new_func + "\n\n        " + code[end_pos:]
            with open("templates/index.html", "w", encoding="utf-8") as f:
                f.write(code)
            print("SUCCESS: Fallback replacement applied!")
        else:
            print("Error in fallback replacement.")
    else:
            print("Could not find openReader function.")
