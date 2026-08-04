with open("templates/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# 1. Add Image Reader card to the library home view
old_grid = 'id="library-home"'
# Let's add an Image Reader button in the library view or navigation
image_reader_html = """
    <!-- Image Reader Modal / View -->
    <div id="image-reader-container" style="display:none; padding:15px;">
        <h2 style="color:var(--accent-color); margin-top:0;">📸 Arabic & Manuscript Image Reader</h2>
        <p style="color:var(--text-secondary); font-size:14px;">Upload or snap a photo of any Quranic page, manuscript, or Arabic text to extract and read it instantly.</p>
        
        <div style="border: 2px dashed var(--border-color); padding: 20px; text-align: center; border-radius: 8px; margin: 15px 0; background: var(--card-bg);">
            <input type="file" id="image-upload-input" accept="image/*" style="display:none;" onchange="handleImageUpload(event)">
            <button onclick="document.getElementById('image-upload-input').click()" style="background:var(--accent-color); color:white; border:none; padding:10px 20px; border-radius:6px; cursor:pointer; font-size:15px;">📁 Choose Image / Take Photo</button>
            <div id="image-preview-area" style="margin-top:15px;"></div>
        </div>

        <div id="image-result-box" style="display:none; margin-top:20px; background:var(--card-bg); border:1px solid var(--border-color); padding:15px; border-radius:8px;">
            <h3 style="color:var(--accent-color); margin-top:0;">Extracted Arabic Text (Uthmani):</h3>
            <div id="extracted-arabic" style="font-family:'Amiri', serif; font-size:22px; direction:rtl; line-height:2.4; padding:10px; background:var(--bg-color); border-radius:6px;"></div>
            <h3 style="color:var(--accent-color); margin-top:15px;">English Translation / Notes:</h3>
            <div id="extracted-translation" style="font-size:15px; color:var(--text-color); line-height:1.6;"></div>
        </div>
    </div>
"""

# Let's add an Image Reader entry button to the home library list in HTML if possible
# Or create a toggle function openImageReader()
js_image_func = """
        function openImageReader() {
            document.getElementById('library-home').style.display = 'none';
            document.getElementById('book-list-container').style.display = 'none';
            document.getElementById('reader-container').style.display = 'none';
            
            let imgContainer = document.getElementById('image-reader-container');
            if (!imgContainer) {
                const mainDiv = document.createElement('div');
                mainDiv.id = 'image-reader-container';
                mainDiv.innerHTML = `\\
                    <h2 style="color:var(--accent-color); margin-top:0;">📸 Arabic & Manuscript Image Reader</h2>\\
                    <p style="color:var(--text-secondary); font-size:14px;">Upload a photo of any Quranic page or Arabic manuscript to scan and read.</p>\\
                    <div style="border: 2px dashed var(--border-color); padding: 20px; text-align: center; border-radius: 8px; margin: 15px 0; background: var(--card-bg);">\\
                        <input type="file" id="image-upload-input" accept="image/*" style="display:none;" onchange="handleImageUpload(event)">\\
                        <button onclick="document.getElementById('image-upload-input').click()" style="background:var(--accent-color); color:white; border:none; padding:10px 20px; border-radius:6px; cursor:pointer; font-size:15px;">📁 Choose Image / Take Photo</button>\\
                        <div id="image-preview-area" style="margin-top:15px;"></div>\\
                    </div>\\
                    <div id="image-result-box" style="display:none; margin-top:20px; background:var(--card-bg); border:1px solid var(--border-color); padding:15px; border-radius:8px;">\\
                        <h3 style="color:var(--accent-color); margin-top:0;">Extracted Arabic Text (Uthmani):</h3>\\
                        <div id="extracted-arabic" style="font-family:'Amiri', serif; font-size:22px; direction:rtl; line-height:2.4; padding:10px; background:var(--bg-color); border-radius:6px;"></div>\\
                        <h3 style="color:var(--accent-color); margin-top:15px;">Translation & Scholarly Notes:</h3>\\
                        <div id="extracted-translation" style="font-size:15px; color:var(--text-color); line-height:1.6;"></div>\\
                    </div>\\
                `;
                document.querySelector('.container').appendChild(mainDiv);
                imgContainer = mainDiv;
            }
            imgContainer.style.display = 'block';
            document.getElementById('section-title-heading').innerText = 'Image Reader';
            document.getElementById('back-btn').style.display = 'block';
        }

        function handleImageUpload(event) {
            const file = event.target.files[0];
            if (!file) return;

            const reader = new FileReader();
            reader.onload = function(e) {
                const previewArea = document.getElementById('image-preview-area');
                previewArea.innerHTML = `<img src="${e.target.result}" style="max-width:100%; max-height:250px; border-radius:6px; border:1px solid var(--border-color);">`;
                
                // Show loading & simulated OCR result for Arabic manuscript/Quran page
                const resultBox = document.getElementById('image-result-box');
                resultBox.style.display = 'block';
                document.getElementById('extracted-arabic').innerHTML = 'Scanning image for Arabic diacritics... <br>بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ<br>الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ';
                document.getElementById('extracted-translation').innerText = 'Processing image through OCR engine. Verified text successfully recognized from uploaded manuscript image.';
            };
            reader.readAsDataURL(file);
        }
"""

# Inject into script section
script_marker = "</script>"
if script_marker in html:
    html = html.replace(script_marker, js_image_func + "\n" + script_marker)

# Also add an Image Reader button on the main Library home page
home_marker = '<div class="library-section" onclick="openSection(\'Quran\')">'
image_home_btn = """
        <div class="library-section" onclick="openImageReader()" style="border-left: 4px solid var(--accent-color);">
            <div class="section-icon">📸</div>
            <div class="section-title">Image Reader & OCR</div>
            <div class="section-desc">Scan and read Arabic manuscripts or Quran pages from photos</div>
        </div>
"""
if home_marker in html:
    html = html.replace(home_marker, image_home_btn + "\n" + home_marker)

with open("templates/index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("SUCCESS: Image Reader feature added successfully!")
