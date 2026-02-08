import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime
from fpdf import FPDF
from io import BytesIO

# ==========================================
# 0.初期設定
# ==========================================
st.set_page_config(layout="wide", page_title="Life Mapping Console v12.0")

# デフォルトのデータ構造
DEFAULT_DATA = {
    "name": "",
    "date": datetime.now().strftime("%Y-%m-%d"),
    "temp_pin": "",
    "bedrock": "",
    "bedrock_note": "",
    "sediment": "",
    "sediment_note": "",
    "cliff": "",
    "slope": "",
    "goal": "",
    "action": ""
}

# セッション状態の初期化
if "data" not in st.session_state:
    st.session_state.data = DEFAULT_DATA.copy()

# ==========================================
# 📄 PDF生成クラス (fpdf2 / IPAexゴシック対応)
# ==========================================
FONT_FILE = "ipaexg.ttf"
FONT_NAME = "IPAexGothic"

class PDFReport(FPDF):
    def header(self):
        if os.path.exists(FONT_FILE):
            self.set_font(FONT_NAME, '', 10)
        else:
            self.set_font('Arial', '', 10)
        self.cell(0, 10, 'Life Mapping Fieldwork Log', align='R', ln=True)
        self.ln(5)

    def chapter_title(self, label):
        self.set_font_size(14)
        self.set_fill_color(240, 242, 246)
        self.cell(0, 10, f"  {label}", fill=True, ln=True)
        self.ln(4)

    def chapter_body(self, text):
        self.set_font_size(11)
        self.multi_cell(0, 7, text)
        self.ln(8)

    def card_body(self, title, content):
        self.set_font_size(10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 6, title, ln=True)
        self.set_text_color(0, 0, 0)
        self.set_font_size(12)
        self.multi_cell(0, 7, content, border='L')
        self.ln(6)

def generate_pdf(data):
    pdf = PDFReport()
    if os.path.exists(FONT_FILE):
        pdf.add_font(FONT_NAME, '', FONT_FILE)
        pdf.set_font(FONT_NAME, '', 12)
    else:
        pdf.set_font("Arial", size=12)
    
    pdf.add_page()
    pdf.set_font_size(24)
    pdf.cell(0, 15, f"{data['name']}'s Adventure Log", ln=True, align='C')
    pdf.set_font_size(12)
    pdf.cell(0, 10, f"Date: {data['date']}", ln=True, align='C')
    pdf.ln(10)

    pdf.chapter_title("1. Core Engine (価値観・原動力)")
    pdf.chapter_body(data['bedrock'])
    
    pdf.chapter_title("2. Inventory (装備・スキル)")
    pdf.chapter_body(data['sediment'])

    pdf.chapter_title("3. Battle Strategy (攻略ルート)")
    pdf.card_body("The Enemy (倒すべき敵)", data['cliff'])
    pdf.card_body("Weapon (武器・戦略)", data['slope'])

    pdf.chapter_title("4. Quests (クエスト)")
    pdf.card_body("Main Quest (3ヶ月後の勝利条件)", data['goal'])
    pdf.card_body("Daily Mission (最初の一歩)", data['action'])

    return pdf.output()

# ==========================================
# 📊 NotebookLM用プロンプト生成
# ==========================================
def get_notebooklm_prompt(data):
    name = data['name'] if data['name'] else "クライアント"
    prompt = f"""
以下のセッションデータを元に、{name}さんの現状を「地質学的な断面図」として分析し、インフォグラフィックの構成案を作成してください。

1. 原始地盤（本来の価値観・原動力）:
{data['bedrock']}

2. 堆積物（これまでの経験・スキル・しがらみ）:
{data['sediment']}

3. 現在の地形（崖に見えている悩み・葛藤）:
{data['cliff']}

4. 登れる坂（再定義された攻略法）:
{data['slope']}

5. 目的地（3ヶ月後のゴール）:
{data['goal']}

デザイン指示:本来の熱い地熱（地盤）が、厚い堆積岩を貫いて地表へ噴き出そうとする断面図として可視化してください。
"""
    return prompt

# ==========================================
# 🦋 RPG View
# ==========================================
def render_rpg(data):
    st.title(f"🧬 {data['name']}'s Human Observation Log")
    st.caption("Target: N=100 Collection / Status: Exploring")
    st.divider()

    st.markdown("""
    <style>
    .rpg-box {
        border: 2px solid #333;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
        background-color: #fff;
        box-shadow: 4px 4px 0px #000;
    }
    .rpg-title {
        font-family: 'Courier New', monospace;
        font-weight: bold;
        color: #333;
        border-bottom: 2px dashed #ccc;
        margin-bottom: 10px;
        padding-bottom: 5px;
    }
    .badge-rpg {
        display: inline-block;
        background: #000;
        color: #fff;
        padding: 4px 8px;
        margin: 2px;
        border-radius: 4px;
        font-size: 0.9em;
    }
    </style>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="rpg-box"><div class="rpg-title">🎒 EQUIPMENT</div>', unsafe_allow_html=True)
        for s in data["sediment"].split('\n'):
            if s.strip(): st.markdown(f'<span class="badge-rpg">{s.strip()}</span>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="rpg-box"><div class="rpg-title">❤️ CORE ENGINE</div>', unsafe_allow_html=True)
        st.write(data["bedrock"])
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="rpg-box" style="background-color: #fff0f5;"><div class="rpg-title">⚔️ STRATEGY</div>', unsafe_allow_html=True)
        st.write(f"**ENEMY:** {data['cliff']}")
        st.write("---")
        st.write(f"**SPELL:** {data['slope']}")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="rpg-box" style="background-color: #f0f8ff;"><div class="rpg-title">📜 QUESTS</div>', unsafe_allow_html=True)
        st.info(f"**GOAL:** {data['goal']}")
        st.success(f"**DAILY:** {data['action']}")
        st.markdown('</div>', unsafe_allow_html=True)

    st.divider()
    if os.path.exists(FONT_FILE):
        pdf_bytes = generate_pdf(data)
        st.download_button("💾 冒険の書を保存 (PDF)", pdf_bytes, f"{data['name']}_Log.pdf", "application/pdf")

# ==========================================
# 🛠️ メインUI (セキュア構成)
# ==========================================
with st.sidebar:
    st.title("🧭 Mapping Console")
    app_mode = st.radio("Mode", ["📝 セッション実施", "🦋 RPG Mode", "📊 NotebookLM出力"])
    st.divider()

    st.subheader("💾 Data Control")
    st.caption("データはサーバーに保存されません。手元のPCに保存してください。")
    
    current_json = json.dumps(st.session_state.data, ensure_ascii=False, indent=4)
    st.download_button("📥 データをJSONで保存", current_json, f"data_{st.session_state.data['name']}.json", "application/json")
    
    uploaded = st.file_uploader("📂 JSONを読み込む", type=['json'])
    if uploaded:
        st.session_state.data.update(json.load(uploaded))
        st.success("読み込み完了")

def section_header(title, purpose, questions):
    st.title(title)
    st.info(f"目的: {purpose}")
    with st.expander("🗣️ 参謀の問い", expanded=True):
        for q in questions: st.markdown(f"- {q}")
    st.divider()

if app_mode == "📝 セッション実施":
    menu = st.radio("フェーズ", ["0.Setup", "1.Bedrock", "2.Sediment", "3.Topography", "4.Routes"], horizontal=True)

    if menu == "0.Setup":
        st.text_input("Client Name", key="name_in", value=st.session_state.data["name"], on_change=lambda: st.session_state.data.update({"name": st.session_state.name_in}))
        st.text_area("Temporary Goal", key="temp_in", value=st.session_state.data["temp_pin"], on_change=lambda: st.session_state.data.update({"temp_pin": st.session_state.temp_in}))
    
    elif menu == "1.Bedrock":
        section_header("🪨 Phase 1:地盤調査", "価値観や原動力を特定する。", ["無意識にできてしまうことは？", "絶対に許せないことは？"])
        st.text_area("譲れない価値観", key="bed_in", value=st.session_state.data["bedrock"], height=200, on_change=lambda: st.session_state.data.update({"bedrock": st.session_state.bed_in}))
    
    elif menu == "2.Sediment":
        section_header("🧱 Phase 2:堆積物確認", "スキルやしがらみを棚卸しする。", ["今の肩書きは？", "もう使いたくないスキルは？"])
        st.text_area("スキル・肩書き", key="sed_in", value=st.session_state.data["sediment"], height=200, on_change=lambda: st.session_state.data.update({"sediment": st.session_state.sed_in}))
    
    elif menu == "3.Topography":
        section_header("🧗 Phase 3:地形測量", "崖を坂に再定義する。", ["何が怖い？", "失敗したらどうなる？"])
        c1, c2 = st.columns(2)
        with c1: st.text_area("😱 崖に見えているもの", key="cli_in", value=st.session_state.data["cliff"], height=150, on_change=lambda: st.session_state.data.update({"cliff": st.session_state.cli_in}))
        with c2: st.text_area("🚶 登れる坂への再定義", key="slo_in", value=st.session_state.data["slope"], height=150, on_change=lambda: st.session_state.data.update({"slope": st.session_state.slo_in}))
    
    elif menu == "4.Routes":
        section_header("🚩 Phase 4:航路策定", "3ヶ月後の目的地を決める。", ["最低限どうなっていたい？", "明日何をする？"])
        st.text_area("🏁 3ヶ月後のゴール", key="goal_in", value=st.session_state.data["goal"], on_change=lambda: st.session_state.data.update({"goal": st.session_state.goal_in}))
        st.text_area("👟 Next Action", key="act_in", value=st.session_state.data["action"], on_change=lambda: st.session_state.data.update({"action": st.session_state.act_in}))

elif app_mode == "🦋 RPG Mode":
    render_rpg(st.session_state.data)

elif app_mode == "📊 NotebookLM出力":
    st.title("📊 NotebookLM 用プロンプト")
    st.markdown("以下のテキストをコピーして NotebookLM に貼り付けてください。地質断面図の分析が始まります。")
    st.code(get_notebooklm_prompt(st.session_state.data))