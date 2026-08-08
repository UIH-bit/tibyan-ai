import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Safe HTML template wrapped cleanly
safe_html = '''
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tibyan AI - Professional Scholar Assistant</title>
    <style>
        :root {
            --primary: #1b4332;
            --secondary: #2d6a4f;
            --bg: #f8f9fa;
            --card-bg: #ffffff;
            --text: #212529;
            --border: #dee2e6;
        }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 0; }
        .container { max-width: 800px; margin: 0 auto; padding: 20px; }
        .card { background: var(--card-bg); border-radius: 12px; padding: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); margin-bottom: 20px; border-left: 5px solid var(--primary); }
        .search-input { width: 100%; padding: 12px; border: 1px solid var(--border); border-radius: 8px; font-size: 14px; margin-bottom: 15px; box-sizing: border-box; }
        .profile-header { display: flex; align-items: center; gap: 20px; margin-bottom: 15px; }
        .profile-img-preview { width: 70px; height: 70px; border-radius: 50%; object-fit: cover; background: #e9f5ed; display: flex; align-items: center; justify-content: center; font-size: 30px; border: 2px solid var(--primary); }
        .form-group { margin-bottom: 12px; }
        .form-group label { display: block; font-weight: 600; font-size: 13px; margin-bottom: 5px; color: var(--primary); }
        .form-control { width: 100%; padding: 10px; border: 1px solid var(--border); border-radius: 6px; font-size: 14px; box-sizing: border-box; }
        .faq-category h3 { color: var(--primary); border-bottom: 2px solid #e9f5ed; padding-bottom: 5px; font-size: 16px; margin-top: 20px; }
        .faq-item { background: #fafafa; border: 1px solid var(--border); padding: 12px; border-radius: 6px; margin-bottom: 10px; }
        .quick-tips { background: #fff8e1; border-left: 4px solid #ffc107; padding: 12px; border-radius: 6px; font-size: 14px; margin-bottom: 15px; }
        .contact-btn { display: inline-block; background: var(--primary); color: white; padding: 10px 20px; border-radius: 6px; text-decoration: none; font-weight: 500; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="container">
        
        <div class="card">
            <h2 style="margin-top:0; color: var(--primary);">Scholar Profile 👤</h2>
            <div class="profile-header">
                <div id="avatarContainer" class="profile-img-preview">🕌</div>
                <div>
                    <h3 id="displayName" style="margin:0;">Tibyan User</h3>
                    <p id="displayBio" style="margin:4px 0 0; color: #6c757d; font-size: 13px;">Seeking authentic Islamic knowledge.</p>
                </div>
            </div>
            <div class="form-group">
                <label>Your Name:</label>
                <input type="text" id="profileNameInput" class="form-control" value="Tibyan User" oninput="updateProfile()">
            </div>
            <div class="form-group">
                <label>Bio / Status:</label>
                <input type="text" id="profileBioInput" class="form-control" value="Seeking authentic Islamic knowledge." oninput="updateProfile()">
            </div>
            <div class="form-group">
                <label>Profile Image URL:</label>
                <input type="text" id="profileImgInput" class="form-control" placeholder="Paste image link here..." oninput="updateProfile()">
            </div>
        </div>

        <div class="card">
            <h2 style="margin-top:0; color: var(--primary);">Chat History 📜</h2>
            <input type="text" id="chatSearchInput" class="search-input" placeholder="Search previous chats... (Matching items move to top)" onkeyup="filterAndSortChats()">
            
            <div id="chatListContainer">
                <div class="chat-item-box faq-item" data-keywords="roza sawm fasting islam pillars">
                    <strong>Q: Roza</strong>
                    <p style="margin: 5px 0 0; font-size: 13px;">Roza, or Sawm, is one of the five fundamental pillars of Islam...</p>
                </div>
                <div class="chat-item-box faq-item" data-keywords="samas hindi grammar dvandva">
                    <strong>Q: Dvandva Samas</strong>
                    <p style="margin: 5px 0 0; font-size: 13px;">Hindi grammar explanation regarding Dvandva Samas...</p>
                </div>
                <div class="chat-item-box faq-item" data-keywords="zakat charity wealth islam">
                    <strong>Q: Zakat Calculation</strong>
                    <p style="margin: 5px 0 0; font-size: 13px;">Details regarding rules of Zakat and Nisab threshold...</p>
                </div>
            </div>
        </div>

        <div class="card">
            <h2 style="margin-top:0; color: var(--primary);">Help & Support 💡</h2>
            
            <div class="quick-tips">
                <strong>Pro Tip:</strong> Use exact keywords in the search bar above to instantly filter and lift your required chats to the very top.
            </div>

            <div class="faq-category">
                <h3>🚀 Getting Started</h3>
                <div class="faq-item">
                    <strong>How to ask queries?</strong>
                    <p style="margin:4px 0 0; font-size:13px;">Type any question into the input console to fetch verified scholarly content.</p>
                </div>
            </div>

            <div class="faq-category">
                <h3>📁 Uploading Fatawa</h3>
                <div class="faq-item">
                    <strong>How to scan documents?</strong>
                    <p style="margin:4px 0 0; font-size:13px;">Tap the '+' icon to upload scanned images/Fatawa for instant breakdown.</p>
                </div>
            </div>

            <div class="faq-category">
                <h3>📚 References</h3>
                <div class="faq-item">
                    <strong>Are citations provided?</strong>
                    <p style="margin:4px 0 0; font-size:13px;">Yes, structural responses include Quranic verses and Hadith references.</p>
                </div>
            </div>

            <div style="margin-top: 20px; padding-top: 15px; border-top: 1px solid var(--border); text-align: center;">
                <p style="margin: 0 0 10px; font-size: 14px; color: #555;">Need direct assistance or technical support?</p>
                <a href="mailto:uih0209@gmail.com" class="contact-btn">✉️ Email Support: uih0209@gmail.com</a>
            </div>
        </div>

    </div>

    <script>
        function updateProfile() {
            const name = document.getElementById('profileNameInput').value;
            const bio = document.getElementById('profileBioInput').value;
            const imgUrl = document.getElementById('profileImgInput').value;
            
            document.getElementById('displayName').innerText = name || "Tibyan User";
            document.getElementById('displayBio').innerText = bio || "";
            
            const avatarContainer = document.getElementById('avatarContainer');
            if (imgUrl.trim() !== "") {
                avatarContainer.innerHTML = `<img src="${imgUrl}" style="width:100%; height:100%; border-radius:50%; object-fit:cover;" onerror="this.onerror=null;this.parentNode.innerHTML='🕌';">`;
            } else {
                avatarContainer.innerHTML = "🕌";
            }
        }

        function filterAndSortChats() {
            const query = document.getElementById('chatSearchInput').value.toLowerCase();
            const container = document.getElementById('chatListContainer');
            const items = Array.from(container.getElementsByClassName('chat-item-box'));

            items.sort((a, b) => {
                const textA = (a.getAttribute('data-keywords') + " " + a.innerText).toLowerCase();
                const textB = (b.getAttribute('data-keywords') + " " + b.innerText).toLowerCase();
                const matchA = textA.includes(query) ? 1 : 0;
                const matchB = textB.includes(query) ? 1 : 0;
                return matchB - matchA;
            });

            items.forEach(item => {
                const fullText = (item.innerText + " " + item.getAttribute('data-keywords')).toLowerCase();
                if (query === "" || fullText.includes(query)) {
                    item.style.display = "block";
                    container.appendChild(item);
                } else {
                    item.style.display = "none";
                }
            });
        }
    </script>
</body>
</html>
"""
'''

if "HTML_TEMPLATE = " in content:
    updated = re.sub(r'HTML_TEMPLATE\s*=\s*[\'"].*?[\'"](\s*\n|$)', safe_html, content, flags=re.DOTALL)
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(updated)
    print("SUCCESS: app.py syntax fixed!")
else:
    print("ERROR")
