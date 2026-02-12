import streamlit as st
import streamlit.components.v1 as components
import random
import re
import time
from gtts import gTTS
from io import BytesIO

# --- 0. 系統配置 ---
st.set_page_config(
    page_title="O Lahok - 午餐", 
    page_icon="🍚", 
    layout="centered"
)

# --- 1. 資料庫 (第 10 課：O Lahok) ---
VOCAB_MAP = {
    "malahok": "吃午餐", "to": "了(完成)", "kiso": "你", 
    "caay": "不", "ho": "還", "o": "是/焦點", "maan": "什麼", 
    "kaenen": "食物/要吃的", "ira": "有", "ko": "主格標記", 
    "hemay": "飯", "ato": "和/與", "foting": "魚", 
    "kaeso'": "好吃(味覺)", "kora": "那個", "hai": "是的", 
    "tada": "非常", "nikaen": "滋味/吃"
}

VOCABULARY = [
    {"amis": "malahok", "zh": "吃午餐", "emoji": "🕛", "root": "lahok", "root_zh": "中午"},
    {"amis": "hemay", "zh": "飯(煮熟的)", "emoji": "🍚", "root": "hemay", "root_zh": "飯"},
    {"amis": "foting", "zh": "魚", "emoji": "🐟", "root": "foting", "root_zh": "魚"},
    {"amis": "kaeso'", "zh": "好吃(味覺)", "emoji": "😋", "root": "eso'", "root_zh": "味"},
    {"amis": "kaenen", "zh": "食物/要吃的", "emoji": "🍱", "root": "kaen", "root_zh": "吃"},
    {"amis": "caay ho", "zh": "還沒", "emoji": "⏳", "root": "caay", "root_zh": "不"},
    {"amis": "nikaen", "zh": "滋味/吃的結果", "emoji": "👅", "root": "kaen", "root_zh": "吃"},
]

SENTENCES = [
    {
        "amis": "Malahok to kiso?", 
        "zh": "你吃過午餐了嗎？", 
        "note": """
        <br><b>Malahok</b>：吃午餐 (詞根 <i>lahok</i> 中午)。
        <br><b>時間動詞化</b>：
        <br>☀️ 早上 <i>ranam</i> → <b>Maranam</b> (吃早餐)
        <br>🕛 中午 <i>lahok</i> → <b>Malahok</b> (吃午餐)
        <br>🌙 晚上 <i>lafi</i> → <b>Malafi</b> (吃晚餐)"""
    },
    {
        "amis": "Caay ho, o maan ko kaenen?", 
        "zh": "還沒，有什麼好吃的？", 
        "note": """
        <br><b>Caay ho</b>：還沒 (固定搭配)。
        <br><b>kaenen</b>：要吃的東西 (<i>kaen</i> + <i>-en</i> 受事焦點)。
        <br><b>語境</b>：這是在問「菜單是什麼」或「準備了什麼菜」。"""
    },
    {
        "amis": "Ira ko hemay ato foting.", 
        "zh": "有飯和魚。", 
        "note": """
        <br><b>Ira</b>：有 (存在動詞)。
        <br><b>ato</b>：和/與 (專門連接兩個名詞 A ato B)。
        <br><b>hemay</b>：煮熟的飯 (生米是 <i>beras</i>)。"""
    },
    {
        "amis": "Kaeso' kora foting?", 
        "zh": "那個魚好吃嗎？", 
        "note": """
        <br><b>Kaeso'</b>：好吃 (專指味覺)。
        <br><b>比較</b>：
        <br>✨ <b>Fangcal</b>：好看/漂亮 (視覺)
        <br>😋 <b>Kaeso'</b>：好吃/美味 (味覺)"""
    },
    {
        "amis": "Hai, tada kaeso' ko nikaen.", 
        "zh": "是的，味道非常好。", 
        "note": """
        <br><b>tada</b>：非常 (程度副詞)。
        <br><b>nikaen</b>：吃下去的感覺/滋味。
        <br><b>解析</b>：這裡不重複說魚，而是強調「品嚐後的結果」。"""
    }
]

STORY_DATA = [
    {"amis": "Malahok to kiso?", "zh": "你吃過午餐了嗎？"},
    {"amis": "Caay ho, o maan ko kaenen?", "zh": "還沒，有什麼好吃的？"},
    {"amis": "Ira ko hemay ato foting.", "zh": "有飯和魚。"},
    {"amis": "Kaeso' kora foting?", "zh": "那個魚好吃嗎？"},
    {"amis": "Hai, tada kaeso' ko nikaen.", "zh": "是的，味道非常好。"}
]

# --- 2. 視覺系統 (CSS 注入 - 全域設定) ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;700;900&family=Noto+Sans+TC:wght@300;500;700&display=swap');
.stApp { background-color: #FFF3E0; color: #E65100; font-family: 'Noto Sans TC', sans-serif; }
.stTabs [data-baseweb="tab"] { color: #EF6C00 !important; font-family: 'Nunito', 'Noto Sans TC', sans-serif; font-size: 18px; font-weight: 700; }
.stTabs [aria-selected="true"] { border-bottom: 4px solid #E65100 !important; color: #BF360C !important; }
.stButton>button { border: 2px solid #E65100 !important; background: #FFFFFF !important; color: #E65100 !important; font-family: 'Nunito', 'Noto Sans TC', sans-serif !important; font-size: 18px !important; font-weight: 700 !important; width: 100%; border-radius: 12px; }
.stButton>button:hover { background: #E65100 !important; color: #FFFFFF !important; }
.quiz-card { background: #FFFFFF; border: 2px solid #FFB74D; padding: 25px; border-radius: 12px; margin-bottom: 20px; }
.quiz-tag { background: #BF360C; color: #FFF; padding: 4px 12px; border-radius: 4px; font-weight: bold; font-size: 14px; margin-right: 10px; font-family: 'Nunito', 'Noto Sans TC', sans-serif; }
.zh-translation-block { background: #FFF8E1; border-left: 5px solid #FF6F00; padding: 20px; color: #BF360C; font-size: 16px; line-height: 2.0; font-family: 'Noto Sans TC', monospace; }
</style>
""", unsafe_allow_html=True)

# --- 3. 核心技術：沙盒渲染引擎 ---
def get_html_card(item, type="word"):
    pt = "100px" if type == "full_amis_block" else "80px"
    mt = "-40px" if type == "full_amis_block" else "-30px" 

    style_block = f"""<style>
        @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;700;900&family=Noto+Sans+TC:wght@300;500;700&display=swap');
        body {{ background-color: transparent; color: #BF360C; font-family: 'Noto Sans TC', sans-serif; margin: 0; padding: 5px; padding-top: {pt}; overflow-x: hidden; }}
        .interactive-word {{ position: relative; display: inline-block; border-bottom: 2px solid #FF6F00; cursor: pointer; margin: 0 3px; color: #BF360C; transition: 0.3s; font-size: 19px; font-weight: 600; }}
        .interactive-word:hover {{ color: #E65100; border-bottom-color: #E65100; }}
        .interactive-word .tooltip-text {{ visibility: hidden; min-width: 80px; background-color: #BF360C; color: #FFF; text-align: center; border-radius: 8px; padding: 8px; position: absolute; z-index: 100; bottom: 145%; left: 50%; transform: translateX(-50%); opacity: 0; transition: opacity 0.3s; font-size: 14px; white-space: nowrap; box-shadow: 0 4px 10px rgba(0,0,0,0.3); font-family: 'Nunito', 'Noto Sans TC', sans-serif; font-weight: 700; }}
        .interactive-word:hover .tooltip-text {{ visibility: visible; opacity: 1; }}
        .play-btn-inline {{ background: #E65100; border: none; color: #FFF; border-radius: 50%; width: 28px; height: 28px; cursor: pointer; margin-left: 8px; display: inline-flex; align-items: center; justify-content: center; font-size: 14px; transition: 0.3s; vertical-align: middle; }}
        .play-btn-inline:hover {{ background: #BF360C; transform: scale(1.1); }}
        .word-card-static {{ background: #FFFFFF; border: 1px solid #FFCC80; border-left: 6px solid #E65100; padding: 15px; border-radius: 8px; display: flex; justify-content: space-between; align-items: center; margin-top: {mt}; height: 100px; box-sizing: border-box; box-shadow: 0 3px 6px rgba(0,0,0,0.05); }}
        .wc-root-tag {{ font-size: 12px; background: #FFF3E0; color: #E65100; padding: 3px 8px; border-radius: 4px; font-weight: bold; margin-right: 5px; font-family: 'Nunito', 'Noto Sans TC', sans-serif; }}
        .wc-amis {{ color: #BF360C; font-size: 26px; font-weight: 900; margin: 2px 0; font-family: 'Nunito', sans-serif; }}
        .wc-zh {{ color: #5D4037; font-size: 16px; font-weight: 500; }}
        .play-btn-large {{ background: #FFF3E0; border: 2px solid #E65100; color: #E65100; border-radius: 50%; width: 42px; height: 42px; cursor: pointer; font-size: 20px; transition: 0.2s; }}
        .play-btn-large:hover {{ background: #E65100; color: #FFF; }}
        .amis-full-block {{ line-height: 2.2; font-size: 18px; margin-top: {mt}; }}
        .sentence-row {{ margin-bottom: 12px; display: block; }}
    </style>
    <script>
        function speak(text) {{ window.speechSynthesis.cancel(); var msg = new SpeechSynthesisUtterance(); msg.text = text; msg.lang = 'id-ID'; msg.rate = 0.9; window.speechSynthesis.speak(msg); }}
    </script>"""

    header = f"<!DOCTYPE html><html><head>{style_block}</head><body>"
    body = ""
    
    if type == "word":
        v = item
        body = f"""<div class="word-card-static">
            <div>
                <div style="margin-bottom:5px;"><span class="wc-root-tag">ROOT: {v['root']}</span> <span style="font-size:12px; color:#757575;">({v['root_zh']})</span></div>
                <div class="wc-amis">{v['emoji']} {v['amis']}</div>
                <div class="wc-zh">{v['zh']}</div>
            </div>
            <button class="play-btn-large" onclick="speak('{v['amis'].replace("'", "\\'")}')">🔊</button>
        </div>"""

    elif type == "full_amis_block": 
        all_sentences_html = []
        for sentence_data in item:
            s_amis = sentence_data['amis']
            words = s_amis.split()
            parts = []
            for w in words:
                clean_word = re.sub(r"[^\w']", "", w).lower()
                translation = VOCAB_MAP.get(clean_word, "")
                js_word = clean_word.replace("'", "\\'") 
                
                if translation:
                    chunk = f'<span class="interactive-word" onclick="speak(\'{js_word}\')">{w}<span class="tooltip-text">{translation}</span></span>'
                else:
                    chunk = f'<span class="interactive-word" onclick="speak(\'{js_word}\')">{w}</span>'
                parts.append(chunk)
            
            full_amis_js = s_amis.replace("'", "\\'")
            sentence_html = f"""
            <div class="sentence-row">
                {' '.join(parts)}
                <button class="play-btn-inline" onclick="speak('{full_amis_js}')" title="播放此句">🔊</button>
            </div>
            """
            all_sentences_html.append(sentence_html)
            
        body = f"""<div class="amis-full-block">{''.join(all_sentences_html)}</div>"""
    
    elif type == "sentence": 
        s = item
        words = s['amis'].split()
        parts = []
        for w in words:
            clean_word = re.sub(r"[^\w']", "", w).lower()
            translation = VOCAB_MAP.get(clean_word, "")
            js_word = clean_word.replace("'", "\\'") 
            
            if translation:
                chunk = f'<span class="interactive-word" onclick="speak(\'{js_word}\')">{w}<span class="tooltip-text">{translation}</span></span>'
            else:
                chunk = f'<span class="interactive-word" onclick="speak(\'{js_word}\')">{w}</span>'
            parts.append(chunk)
            
        full_js = s['amis'].replace("'", "\\'")
        body = f'<div style="font-size: 18px; line-height: 1.6; margin-top: {mt};">{" ".join(parts)}</div><button style="margin-top:10px; background:#E65100; border:none; color:#FFF; padding:6px 15px; border-radius:8px; cursor:pointer; font-family:Nunito; font-weight:700; box-shadow: 0 2px 4px rgba(0,0,0,0.2);" onclick="speak(`{full_js}`)">▶ PLAY AUDIO</button>'

    return header + body + "</body></html>"

# --- 4. 測驗生成引擎 ---
def generate_quiz():
    questions = []
    
    # 1. 聽音辨義
    q1 = random.choice(VOCABULARY)
    q1_opts = [q1['amis']] + [v['amis'] for v in random.sample([x for x in VOCABULARY if x != q1], 2)]
    random.shuffle(q1_opts)
    questions.append({"type": "listen", "tag": "🎧 聽音辨義", "text": "請聽語音，選擇正確的單字", "audio": q1['amis'], "correct": q1['amis'], "options": q1_opts})
    
    # 2. 中翻阿
    q2 = random.choice(VOCABULARY)
    q2_opts = [q2['amis']] + [v['amis'] for v in random.sample([x for x in VOCABULARY if x != q2], 2)]
    random.shuffle(q2_opts)
    questions.append({"type": "trans", "tag": "🧩 中翻阿", "text": f"請選擇「<span style='color:#E65100'>{q2['zh']}</span>」的阿美語", "correct": q2['amis'], "options": q2_opts})
    
    # 3. 阿翻中
    q3 = random.choice(VOCABULARY)
    q3_opts = [q3['zh']] + [v['zh'] for v in random.sample([x for x in VOCABULARY if x != q3], 2)]
    random.shuffle(q3_opts)
    questions.append({"type": "trans_a2z", "tag": "🔄 阿翻中", "text": f"單字 <span style='color:#E65100'>{q3['amis']}</span> 的意思是？", "correct": q3['zh'], "options": q3_opts})

    # 4. 詞根偵探
    q4 = random.choice(VOCABULARY)
    other_roots = list(set([v['root'] for v in VOCABULARY if v['root'] != q4['root']]))
    if len(other_roots) < 2: other_roots += ["lahok", "kaen", "eso'"]
    q4_opts = [q4['root']] + random.sample(other_roots, 2)
    random.shuffle(q4_opts)
    questions.append({"type": "root", "tag": "🧬 詞根偵探", "text": f"單字 <span style='color:#E65100'>{q4['amis']}</span> 的詞根是？", "correct": q4['root'], "options": q4_opts, "note": f"詞根意思：{q4['root_zh']}"})
    
    # 5. 語感聽解
    q5 = random.choice(STORY_DATA)
    questions.append({"type": "listen_sent", "tag": "🔊 語感聽解", "text": "請聽句子，選擇正確的中文翻譯", "audio": q5['amis'], "correct": q5['zh'], "options": [q5['zh']] + [s['zh'] for s in random.sample([x for x in STORY_DATA if x != q5], 2)]})

    # 6. 句型翻譯
    q6 = random.choice(STORY_DATA)
    q6_opts = [q6['amis']] + [s['amis'] for s in random.sample([x for x in STORY_DATA if x != q6], 2)]
    random.shuffle(q6_opts)
    questions.append({"type": "sent_trans", "tag": "📝 句型翻譯", "text": f"請選擇中文「<span style='color:#E65100'>{q6['zh']}</span>」對應的阿美語", "correct": q6['amis'], "options": q6_opts})

    # 7. 克漏字
    q7 = random.choice(STORY_DATA)
    words = q7['amis'].split()
    valid_indices = []
    for i, w in enumerate(words):
        clean_w = re.sub(r"[^\w']", "", w).lower()
        if clean_w in VOCAB_MAP:
            valid_indices.append(i)
    
    if valid_indices:
        target_idx = random.choice(valid_indices)
        target_raw = words[target_idx]
        target_clean = re.sub(r"[^\w']", "", target_raw).lower()
        
        words_display = words[:]
        words_display[target_idx] = "______"
        q_text = " ".join(words_display)
        
        correct_ans = target_clean
        distractors = [k for k in VOCAB_MAP.keys() if k != correct_ans and len(k) > 2]
        if len(distractors) < 2: distractors += ["kako", "ira"]
        opts = [correct_ans] + random.sample(distractors, 2)
        random.shuffle(opts)
        
        questions.append({"type": "cloze", "tag": "🕳️ 文法克漏字", "text": f"請填空：<br><span style='color:#BF360C; font-size:18px;'>{q_text}</span><br><span style='color:#5D4037; font-size:14px;'>{q7['zh']}</span>", "correct": correct_ans, "options": opts})
    else:
        questions.append(questions[0]) 

    questions.append(random.choice(questions[:4])) 
    random.shuffle(questions)
    return questions

def play_audio_backend(text):
    try:
        tts = gTTS(text=text, lang='id'); fp = BytesIO(); tts.write_to_fp(fp); st.audio(fp, format='audio/mp3')
    except: pass

# --- 5. UI 呈現層 (使用 components.html 隔離渲染標題) ---
# 為了配合「午餐/食物」主題，這裡微調了配色為暖色系 (橙色/米色)，但結構保持不變
header_html = """
<!DOCTYPE html>
<html>
<head>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@900&family=Noto+Sans+TC:wght@700&display=swap');
        body { margin: 0; padding: 0; background-color: transparent; font-family: 'Noto Sans TC', sans-serif; text-align: center; }
        .container {
            background: linear-gradient(180deg, #E65100 0%, #BF360C 100%);
            border-bottom: 6px solid #5D4037;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.3);
            color: #FFFFFF; /* 強制白色 */
        }
        h1 {
            font-family: 'Nunito', sans-serif;
            color: #FFFFFF !important; /* 強制白色 */
            font-size: 48px;
            margin: 0 0 10px 0;
            text-shadow: 3px 3px 0 #000000;
            letter-spacing: 2px;
        }
        .subtitle {
            color: #FFF3E0; /* 亮米色 */
            border: 1px solid #FFF3E0;
            background: rgba(0,0,0,0.3);
            border-radius: 20px;
            padding: 5px 20px;
            display: inline-block;
            font-weight: bold;
            font-size: 18px;
        }
        .footer {
            margin-top: 10px;
            font-size: 12px;
            color: #FFCC80;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>O Lahok</h1>
        <div class="subtitle">第 10 課：午餐/用餐</div>
        <div class="footer">Code-CRF v6.5 | Theme: Harvest Feast (Warm)</div>
    </div>
</body>
</html>
"""

components.html(header_html, height=220)

tab1, tab2, tab3, tab4 = st.tabs([
    "🍚 互動課文", 
    "🐟 核心單字", 
    "🧬 句型解析", 
    "⚔️ 實戰測驗"
])

with tab1:
    st.markdown("### // 文章閱讀")
    st.caption("👆 點擊單字可聽發音並查看翻譯")
    
    st.markdown("""<div style="background:#FFFFFF; padding:10px; border: 2px solid #FFCC80; border-radius:12px;">""", unsafe_allow_html=True)
    components.html(get_html_card(STORY_DATA, type="full_amis_block"), height=400, scrolling=True)
    st.markdown("</div>", unsafe_allow_html=True)

    zh_content = "<br>".join([item['zh'] for item in STORY_DATA])
    st.markdown(f"""
    <div class="zh-translation-block">
        {zh_content}
    </div>
    """, unsafe_allow_html=True)

with tab2:
    st.markdown("### // 單字與詞根")
    for v in VOCABULARY:
        components.html(get_html_card(v, type="word"), height=150)

with tab3:
    st.markdown("### // 語法結構分析")
    for s in SENTENCES:
        st.markdown("""<div style="background:#FFFFFF; padding:15px; border:1px dashed #E65100; border-radius: 12px; margin-bottom:15px;">""", unsafe_allow_html=True)
        components.html(get_html_card(s, type="sentence"), height=160)
        st.markdown(f"""
        <div style="color:#BF360C; font-size:16px; margin-bottom:10px; border-top:1px solid #FFCC80; padding-top:10px;">{s['zh']}</div>
        <div style="color:#E65100; font-size:14px; line-height:1.8; border-top:1px dashed #FFCC80; padding-top:5px;"><span style="color:#BF360C; font-family:Nunito; font-weight:bold;">ANALYSIS:</span> {s.get('note', '')}</div>
        </div>
        """, unsafe_allow_html=True)

with tab4:
    if 'quiz_questions' not in st.session_state:
        st.session_state.quiz_questions = generate_quiz()
        st.session_state.quiz_step = 0; st.session_state.quiz_score = 0
    
    if st.session_state.quiz_step < len(st.session_state.quiz_questions):
        q = st.session_state.quiz_questions[st.session_state.quiz_step]
        st.markdown(f"""<div class="quiz-card"><div style="margin-bottom:10px;"><span class="quiz-tag">{q['tag']}</span> <span style="color:#5D4037;">Q{st.session_state.quiz_step + 1}</span></div><div style="font-size:18px; color:#BF360C; margin-bottom:10px;">{q['text']}</div></div>""", unsafe_allow_html=True)
        if 'audio' in q: play_audio_backend(q['audio'])
        opts = q['options']; cols = st.columns(min(len(opts), 3))
        for i, opt in enumerate(opts):
            with cols[i % 3]:
                if st.button(opt, key=f"q_{st.session_state.quiz_step}_{i}"):
                    if opt.lower() == q['correct'].lower():
                        st.success("✅ 正確 (Correct)"); st.session_state.quiz_score += 1
                    else:
                        st.error(f"❌ 錯誤 - 正解: {q['correct']}"); 
                        if 'note' in q: st.info(q['note'])
                    time.sleep(1.5); st.session_state.quiz_step += 1; st.rerun()
    else:
        st.markdown(f"""<div style="text-align:center; padding:30px; border:4px solid #E65100; border-radius:15px; background:#FFFFFF;"><h2 style="color:#BF360C; font-family:Nunito;">MISSION COMPLETE</h2><p style="font-size:20px; color:#E65100;">得分: {st.session_state.quiz_score} / {len(st.session_state.quiz_questions)}</p></div>""", unsafe_allow_html=True)
        if st.button("🔄 重新挑戰 (Reboot)"): del st.session_state.quiz_questions; st.rerun()

st.markdown("---")
st.caption("Powered by Code-CRF v6.5 | Architecture: Chief Architect")
