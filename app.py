import streamlit as st
import streamlit.components.v1 as components
import random
import re
import time
from gtts import gTTS
from io import BytesIO

# --- 0. 系統配置 ---
st.set_page_config(
    page_title="第 10 課 - 跌倒 Matolo'", 
    page_icon="🤕", 
    layout="centered"
)

# --- 1. 資料庫 (身體與醫療 第 10 課) ---
VOCAB_MAP = {
    "misalama": "玩耍", "kako": "我", "i": "在", "dafak": "早上/前院",
    "malitosor": "傷到膝蓋", "a": "連接詞", "matolo'": "跌倒",
    "madoka'": "受傷", "maremes": "流血", "ko": "主格", "tosor": "膝蓋",
    "ako": "我的", "paiyoen": "被治療", "tafoen": "被包紮", "no": "屬格(被)",
    "singsi": "老師", "doka'": "傷口", "talacowa": "雖然", "romakat": "走路",
    "to": "了", "anini": "現在", "mapi'iw": "跛腳", "ho": "還",
    "nikaorira": "但是", "o": "是", "mamaadah": "將要痊癒", "anocila": "明天"
}

VOCABULARY = [
    {"amis": "matolo'", "zh": "跌倒", "emoji": "🤸", "root": "tolo'", "root_zh": "倒", "type": "bad"},
    {"amis": "malitosor", "zh": "傷到膝蓋", "emoji": "🦵", "root": "tosor", "root_zh": "膝蓋", "type": "bad"},
    {"amis": "maremes", "zh": "流血", "emoji": "🩸", "root": "remes", "root_zh": "血", "type": "bad"},
    {"amis": "paiyoen", "zh": "治療(給藥)", "emoji": "💊", "root": "iyo", "root_zh": "藥", "type": "good"},
    {"amis": "tafoen", "zh": "包紮", "emoji": "🩹", "root": "tafo", "root_zh": "包", "type": "good"},
    {"amis": "mamaadah", "zh": "將要痊癒", "emoji": "✨", "root": "adah", "root_zh": "痊癒", "type": "good"},
    {"amis": "talacowa", "zh": "雖然", "emoji": "🔄", "root": "talacowa", "root_zh": "雖然", "type": "neutral"},
]

SENTENCES = [
    {
        "amis": "Misalama kako i dafak, malitosor a matolo'.", 
        "zh": "我在早上(或前院)玩耍時，跌倒傷到膝蓋了。", 
        "note": """
        <br><b>Malitosor</b>：Mali- (受傷) + tosor (膝蓋)。
        <br><b>連動句</b>：... a matolo' (以...的方式跌倒)。"""
    },
    {
        "amis": "Madoka', maremes ko tosor ako.", 
        "zh": "受傷了，我的膝蓋流血了。", 
        "note": """
        <br><b>Madoka'</b>：受傷 (狀態)。
        <br><b>Maremes</b>：流血 (有血的狀態)。
        <br>連續使用狀態動詞來描述慘況。"""
    },
    {
        "amis": "Paiyoen, tafoen no singsi ko doka' ako.", 
        "zh": "老師幫我治療並包紮傷口。", 
        "note": """
        <br><b>Paiyo-en</b>：被治療 (受事焦點)。
        <br><b>Tafo-en</b>：被包紮。
        <br>結構：[動作] <b>no</b> [行為者] <b>ko</b> [受事者]。"""
    },
    {
        "amis": "Talacowa romakat to anini, mapi'iw ho kako.", 
        "zh": "雖然現在可以走路了，但我還是一跛一跛的。", 
        "note": """
        <br><b>Talacowa</b>：雖然。
        <br><b>Mapi'iw</b>：跛腳。
        <br><b>To</b> (已經) vs <b>Ho</b> (還在) 的對比。"""
    },
    {
        "amis": "Nikaorira o mamaadah ko doka' ako anocila.", 
        "zh": "但是我的傷口明天將會痊癒。", 
        "note": """
        <br><b>Mama-adah</b>：將要痊癒 (未來狀態)。
        <br><b>Mama-</b> 是表示「即將發生」的重要前綴。"""
    }
]

STORY_DATA = [
    {"amis": "Misalama kako i dafak, malitosor a matolo'.", "zh": "我在前院玩耍時，跌倒傷到膝蓋了。"},
    {"amis": "Madoka', maremes ko tosor ako.", "zh": "受傷了，我的膝蓋流血了。"},
    {"amis": "Paiyoen, tafoen no singsi ko doka' ako.", "zh": "老師幫我治療並包紮傷口。"},
    {"amis": "Talacowa romakat to anini, mapi'iw ho kako.", "zh": "雖然現在可以走路了，但我還是一跛一跛的。"},
    {"amis": "Nikaorira o mamaadah ko doka' ako anocila.", "zh": "但是我的傷口明天將會痊癒。"}
]

# --- 2. 視覺系統 (CSS 注入 - 風格：醫療白與十字紅) ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto+Rounded:wght@400;700&family=Noto+Sans+TC:wght@400;700&display=swap');

/* 全局背景：柔和的醫療灰白 */
.stApp { 
    background-color: #F5F7F9; 
    color: #263238; /* 深灰黑，高對比 */
    font-family: 'Noto Sans TC', sans-serif; 
}

/* Tab 樣式：乾淨俐落 */
.stTabs [data-baseweb="tab-list"] {
    gap: 10px;
    background-color: #FFFFFF;
    padding: 10px;
    border-radius: 10px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.05);
}
.stTabs [data-baseweb="tab"] {
    height: 45px;
    border-radius: 8px;
    background-color: transparent;
    color: #546E7A;
    font-weight: 700;
    border: 1px solid #CFD8DC !important;
}
.stTabs [aria-selected="true"] {
    background-color: #E53935 !important; /* 急救紅 */
    color: #FFFFFF !important;
    border: none !important;
}

/* 按鈕樣式：緊急按鈕風格 */
.stButton>button { 
    background-color: #E53935 !important; 
    color: white !important; 
    border: none !important; 
    border-radius: 8px !important; 
    font-size: 18px !important; 
    font-weight: 700 !important; 
    box-shadow: 0 4px 0 #B71C1C !important;
    transition: all 0.1s ease !important;
}
.stButton>button:active { 
    transform: translateY(4px);
    box-shadow: 0 0 0 #B71C1C !important;
}

/* 測驗卡片：純白卡片 */
.quiz-card { 
    background: #FFFFFF; 
    border-left: 6px solid #E53935; 
    padding: 25px; 
    border-radius: 10px; 
    margin-bottom: 20px; 
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.08);
    color: #263238;
}
.quiz-tag { 
    background: #FFEBEE; 
    color: #C62828; 
    padding: 5px 12px; 
    border-radius: 4px; 
    font-weight: bold; 
    font-size: 14px; 
    display: inline-block;
    margin-bottom: 10px;
    border: 1px solid #FFCDD2;
}

/* 翻譯區塊：處方箋風格 */
.zh-translation-block { 
    background: #FFFFFF; 
    border: 1px solid #CFD8DC;
    border-top: 4px solid #43A047; /* 康復綠 */
    border-radius: 8px;
    padding: 20px; 
    color: #37474F; 
    font-size: 16px; 
    line-height: 1.8; 
    font-family: 'Noto Sans TC', monospace; 
}
</style>
""", unsafe_allow_html=True)

# --- 3. 核心技術：沙盒渲染引擎 ---
def get_html_card(item, type="word"):
    pt = "80px" if type == "full_amis_block" else "60px"
    mt = "-20px" if type == "full_amis_block" else "-10px" 
    
    # 根據單字類型決定邊框顏色 (紅=受傷, 綠=治療)
    border_color = "#E53935" # Default Red
    if isinstance(item, dict) and item.get('type') == 'good':
        border_color = "#43A047" # Green
    elif isinstance(item, dict) and item.get('type') == 'neutral':
        border_color = "#78909C" # Grey

    style_block = f"""<style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto+Rounded:wght@500;700&family=Noto+Sans+TC:wght@400;700&display=swap');
        body {{ background-color: transparent; color: #263238; font-family: 'Noto Sans TC', sans-serif; margin: 0; padding: 10px; padding-top: {pt}; overflow-x: hidden; }}
        
        /* 互動單字 */
        .interactive-word {{ 
            position: relative; 
            display: inline-block; 
            border-bottom: 2px solid #CFD8DC;
            cursor: pointer; 
            margin: 0 4px; 
            color: #37474F; 
            transition: 0.3s; 
            font-size: 20px; 
            font-weight: 700; 
            font-family: 'Roboto Rounded', sans-serif;
        }}
        .interactive-word:hover {{ color: #E53935; border-bottom-color: #E53935; background: #FFEBEE; }}
        
        /* Tooltip */
        .interactive-word .tooltip-text {{ 
            visibility: hidden; 
            min-width: 80px; 
            background-color: #263238; 
            color: #FFF; 
            text-align: center; 
            border-radius: 4px; 
            padding: 8px; 
            position: absolute; 
            z-index: 100; 
            bottom: 140%; 
            left: 50%; 
            transform: translateX(-50%); 
            opacity: 0; 
            transition: opacity 0.3s; 
            font-size: 14px; 
            white-space: nowrap; 
            box-shadow: 0 4px 10px rgba(0,0,0,0.3); 
        }}
        .interactive-word:hover .tooltip-text {{ visibility: visible; opacity: 1; }}
        
        /* 播放按鈕 */
        .play-btn-inline {{ background: #E53935; border: none; color: #FFF; border-radius: 50%; width: 28px; height: 28px; cursor: pointer; margin-left: 8px; display: inline-flex; align-items: center; justify-content: center; font-size: 14px; transition: 0.3s; vertical-align: middle; }}
        .play-btn-inline:hover {{ background: #B71C1C; }}
        
        /* 單字卡 - 純白高對比 */
        .word-card-static {{ 
            background: #FFFFFF; 
            border-radius: 8px; 
            padding: 15px; 
            display: flex; 
            justify-content: space-between; 
            align-items: center; 
            margin-top: {mt}; 
            height: 100px; 
            box-sizing: border-box; 
            box-shadow: 0 2px 6px rgba(0,0,0,0.1); 
            border-left: 6px solid {border_color};
            border-top: 1px solid #ECEFF1;
            border-right: 1px solid #ECEFF1;
            border-bottom: 1px solid #ECEFF1;
        }}
        .wc-root-tag {{ font-size: 12px; background: #ECEFF1; color: #455A64; padding: 3px 8px; border-radius: 4px; font-weight: bold; margin-right: 5px; }}
        .wc-amis {{ color: #263238; font-size: 26px; font-weight: 700; margin: 2px 0; font-family: 'Roboto Rounded', sans-serif; }}
        .wc-zh {{ color: #546E7A; font-size: 16px; font-weight: 500; }}
        
        .play-btn-large {{ background: #FFEBEE; border: 2px solid #FFCDD2; color: #C62828; border-radius: 50%; width: 42px; height: 42px; cursor: pointer; font-size: 20px; transition: 0.2s; }}
        .play-btn-large:hover {{ background: #E53935; color: #FFF; border-color: #E53935; }}
        
        .amis-full-block {{ line-height: 2.4; font-size: 18px; margin-top: {mt}; text-align: left; padding: 0 5px; }}
        .sentence-row {{ margin-bottom: 12px; display: block; border-bottom: 1px dashed #CFD8DC; padding-bottom: 8px; }}
        .sentence-row:last-child {{ border-bottom: none; }}
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
                <div style="margin-bottom:5px;"><span class="wc-root-tag">ROOT: {v['root']}</span> <span style="font-size:12px; color:#78909C;">({v['root_zh']})</span></div>
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
        body = f'<div style="font-size: 18px; line-height: 1.8; margin-top: {mt};">{" ".join(parts)}</div><button style="margin-top:10px; background:#455A64; border:none; color:#FFF; padding:6px 15px; border-radius:4px; cursor:pointer; font-family:Roboto Rounded; font-weight:700; box-shadow: 0 2px 4px rgba(0,0,0,0.2);" onclick="speak(`{full_js}`)">▶ PLAY AUDIO</button>'

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
    questions.append({"type": "trans", "tag": "🧩 中翻阿", "text": f"請選擇「<span style='color:#E53935'>{q2['zh']}</span>」的阿美語", "correct": q2['amis'], "options": q2_opts})
    
    # 3. 語法題 (Mama-)
    q3_data = {"text": "O _____ ko doka' ako. (我的傷口將要痊癒)", "ans": "mamaadah", "note": "Mama- 表示未來將要發生"}
    questions.append({"type": "grammar", "tag": "⚖️ 文法急救站", "text": f"請填空：<br>{q3_data['text']}", "correct": "mamaadah", "options": ["mamaadah", "adah", "maadah"], "note": q3_data['note']})

    # 4. 語法題 (Talacowa)
    q4_data = {"text": "_____ romakat to, mapi'iw ho. (雖然已經可以走，但還是一跛一跛)", "ans": "Talacowa", "note": "Talacowa = 雖然"}
    questions.append({"type": "grammar", "tag": "⚖️ 文法急救站", "text": f"請填空：<br>{q4_data['text']}", "correct": "Talacowa", "options": ["Talacowa", "Nikaorira", "Ato"], "note": q4_data['note']})

    # 5. 句型翻譯
    q6 = random.choice(STORY_DATA)
    q6_opts = [q6['amis']] + [s['amis'] for s in random.sample([x for x in STORY_DATA if x != q6], 2)]
    random.shuffle(q6_opts)
    questions.append({"type": "sent_trans", "tag": "📝 句型翻譯", "text": f"請選擇中文「<span style='color:#E53935'>{q6['zh']}</span>」對應的阿美語", "correct": q6['amis'], "options": q6_opts})

    random.shuffle(questions)
    return questions[:5]

def play_audio_backend(text):
    try:
        tts = gTTS(text=text, lang='id'); fp = BytesIO(); tts.write_to_fp(fp); st.audio(fp, format='audio/mp3')
    except: pass

# --- 5. UI 呈現層 (使用 components.html 隔離渲染標題) ---
# 主題：醫療白與十字紅 (Clinical White & Red)
header_html = """
<!DOCTYPE html>
<html>
<head>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto+Rounded:wght@700&family=Noto+Sans+TC:wght@700&display=swap');
        body { margin: 0; padding: 0; background-color: transparent; font-family: 'Noto Sans TC', sans-serif; text-align: center; }
        .container {
            background: #FFFFFF;
            border-radius: 12px;
            padding: 20px;
            color: #263238;
            border-top: 6px solid #E53935; /* 紅十字風格 */
            box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        }
        h1 {
            font-family: 'Roboto Rounded', sans-serif;
            color: #E53935;
            font-size: 42px;
            margin: 0 0 5px 0;
            letter-spacing: 1px;
        }
        .subtitle {
            color: #546E7A;
            background: #ECEFF1;
            border-radius: 4px;
            padding: 5px 15px;
            display: inline-block;
            font-weight: bold;
            font-size: 16px;
        }
        .footer {
            margin-top: 10px;
            font-size: 12px;
            color: #90A4AE;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Matolo'</h1>
        <div class="subtitle">第 10 課：跌倒 (受傷與復原)</div>
        <div class="footer">Theme: Clinical White & Red 🚑</div>
    </div>
</body>
</html>
"""

components.html(header_html, height=200)

tab1, tab2, tab3, tab4 = st.tabs([
    "🤕 故事閱讀", 
    "💊 核心單字", 
    "🧬 語法解析", 
    "🚑 實戰測驗"
])

with tab1:
    st.markdown("### // 意外的發生")
    st.caption("👆 點擊單字可聽發音並查看翻譯")
    
    # 使用純白背景容器
    st.markdown("""<div style="background:#FFFFFF; padding:15px; border-radius:10px; border: 1px solid #CFD8DC; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">""", unsafe_allow_html=True)
    components.html(get_html_card(STORY_DATA, type="full_amis_block"), height=400, scrolling=True)
    st.markdown("</div>", unsafe_allow_html=True)

    zh_content = "<br>".join([item['zh'] for item in STORY_DATA])
    st.markdown(f"""
    <div class="zh-translation-block">
        {zh_content}
    </div>
    """, unsafe_allow_html=True)

with tab2:
    st.markdown("### // 傷痛與治療")
    col1, col2 = st.columns(2)
    for i, v in enumerate(VOCABULARY):
        with col1 if i % 2 == 0 else col2:
            components.html(get_html_card(v, type="word"), height=130)

with tab3:
    st.markdown("### // 結構分析")
    for s in SENTENCES:
        st.markdown("""<div style="background:#FFFFFF; padding:20px; border-radius: 10px; margin-bottom:20px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); border-left: 4px solid #546E7A;">""", unsafe_allow_html=True)
        components.html(get_html_card(s, type="sentence"), height=160)
        st.markdown(f"""
        <div style="color:#263238; font-size:16px; margin-bottom:10px; border-top:1px solid #ECEFF1; padding-top:10px; font-weight:bold;">{s['zh']}</div>
        <div style="color:#455A64; font-size:14px; line-height:1.8; background:#ECEFF1; padding:10px; border-radius:6px;">
            <span style="color:#E53935; font-weight:bold;">💡 NOTE:</span> {s.get('note', '')}
        </div>
        </div>
        """, unsafe_allow_html=True)

with tab4:
    if 'quiz_questions' not in st.session_state:
        st.session_state.quiz_questions = generate_quiz()
        st.session_state.quiz_step = 0; st.session_state.quiz_score = 0
    
    if st.session_state.quiz_step < len(st.session_state.quiz_questions):
        q = st.session_state.quiz_questions[st.session_state.quiz_step]
        st.markdown(f"""<div class="quiz-card">
            <span class="quiz-tag">{q['tag']}</span>
            <div style="font-size:20px; color:#263238; margin-bottom:20px; font-weight:bold;">{q['text']}</div>
        </div>""", unsafe_allow_html=True)
        
        if 'audio' in q: play_audio_backend(q['audio'])
        
        opts = q['options']; cols = st.columns(min(len(opts), 3))
        for i, opt in enumerate(opts):
            with cols[i % 3]:
                if st.button(opt, key=f"q_{st.session_state.quiz_step}_{i}"):
                    if opt.lower() == q['correct'].lower():
                        st.success("✅ Fangcal! (Correct)"); st.session_state.quiz_score += 1
                    else:
                        st.error(f"❌ Caay ka matira... 正解: {q['correct']}"); 
                        if 'note' in q: st.info(q['note'])
                    time.sleep(1.5); st.session_state.quiz_step += 1; st.rerun()
    else:
        st.markdown(f"""<div style="text-align:center; padding:40px; border-radius:10px; background:#FFFFFF; border: 1px solid #CFD8DC;">
            <h1 style="color:#43A047; font-family:Roboto Rounded;">Mamaadah To!</h1>
            <p style="font-size:22px; color:#263238;">得分: {st.session_state.quiz_score} / {len(st.session_state.quiz_questions)}</p>
            <p style="color:#546E7A;">快痊癒了！(You are recovering!)</p>
        </div>""", unsafe_allow_html=True)
        if st.button("🔄 重新挑戰 (Replay)"): del st.session_state.quiz_questions; st.rerun()

st.markdown("---")
st.caption("Powered by Code-CRF v7.2 | Theme: Clinical White & Red 🚑")
