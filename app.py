import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime
from fpdf import FPDF

# ==========================================
# 0. 初期設定 & データ管理
# ==========================================
st.set_page_config(layout="wide", page_title="Life Mapping Console v8.2")

DATA_DIR = "data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

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

if "data" not in st.session_state:
    st.session_state.data = DEFAULT_DATA.copy()
else:
    for key, value in DEFAULT_DATA.items():
        if key not in st.session_state.data:
            st.session_state.data[key] = value

# --- ⚡️ オートセーブ関数 ---
def auto_save():
    if not st.session_state.data["name"]:
        filename = "autosave_draft.json"
    else:
        filename = f"{st.session_state.data['name']}_{st.session_state.data['date']}.json"
    
    filepath = os.path.join(DATA_DIR, filename)
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(st.session_state.data, f, ensure_ascii=False, indent=4)
        st.toast(f"💾 Auto-saved: {filename}", icon="✅")
    except Exception as e:
        print(f"Auto-save failed: {e}")

# --- 読み込み & 削除関数 ---
def load_data(filename):
    filepath = os.path.join(DATA_DIR, filename)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
            new_data = DEFAULT_DATA.copy()
            new_data.update(loaded_data)
            st.session_state.data = new_data
        st.sidebar.success(f"📂 読み込み完了: {filename}")
    except Exception as e:
        st.sidebar.error(f"読み込みエラー: {e}")

def delete_data(filename):
    filepath = os.path.join(DATA_DIR, filename)
    try:
        os.remove(filepath)
        st.success(f"🗑️ 削除しました: {filename}")
        return True
    except Exception as e:
        st.error(f"削除エラー: {e}")
        return False

def get_saved_files():
    files = [f for f in os.listdir(DATA_DIR) if f.endswith('.json')]
    return sorted(files, reverse=True)

# ==========================================
# 📄 PDF生成クラス (IPAexゴシック固定)
# ==========================================
FONT_FILE = "ipaexg.ttf"

class PDFReport(FPDF):
    def header(self):
        # ヘッダーも日本語フォントで描画トライ
        if os.path.exists(FONT_FILE):
            self.add_font('Japanese', '', FONT_FILE)
            self.set_font('Japanese', '', 10)
        else:
            self.set_font('Arial', '', 10)
        
        self.cell(0, 10, 'Life Mapping Fieldwork Log', align='R')
        self.ln(15)

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
    # フォント存在チェック（最重要）
    if not os.path.exists(FONT_FILE):
        return None # エラーハンドリングは呼び出し元で行う

    pdf = PDFReport()
    pdf.add_page()
    pdf.add_font('Japanese', '', FONT_FILE) # フォント追加
    pdf.set_font("Japanese", size=12)       # フォントセット

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
    pdf.card_body("👾 The Enemy (倒すべき敵)", data['cliff'])
    pdf.card_body("⚔️ Weapon (武器・戦略)", data['slope'])

    pdf.chapter_title("4. Quests (クエスト)")
    pdf.card_body("🏆 Main Quest (3ヶ月後の勝利条件)", data['goal'])
    pdf.card_body("📜 Daily Mission (最初の一歩)", data['action'])

    return bytes(pdf.output())

# ==========================================
# 🦋 Hiiro's RPG View
# ==========================================
def render_hiiro_rpg(data):
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
    .rpg-content {
        font-family: 'Meiryo', sans-serif;
        color: #000;
        font-weight: 500;
        white-space: pre-wrap;
    }
    .badge-rpg {
        display: inline-block;
        background: #000;
        color: #fff;
        padding: 4px 8px;
        margin: 2px;
        border-radius: 4px;
        font-size: 0.9em;
        font-family: 'Courier New', monospace;
    }
    </style>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown('<div class="rpg-box">', unsafe_allow_html=True)
        st.markdown('<div class="rpg-title">🎒 EQUIPMENT (装備・スキル)</div>', unsafe_allow_html=True)
        skills = data["sediment"].split('\n')
        html_skills = ""
        for s in skills:
            if s.strip():
                html_skills += f'<span class="badge-rpg">{s.strip()}</span>'
        st.markdown(html_skills, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="rpg-box">', unsafe_allow_html=True)
        st.markdown('<div class="rpg-title">❤️ CORE ENGINE (原動力)</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="rpg-content">{data["bedrock"]}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="rpg-box" style="background-color: #fff0f5;">', unsafe_allow_html=True)
        st.markdown('<div class="rpg-title">⚔️ BATTLE STRATEGY</div>', unsafe_allow_html=True)
        st.markdown(f"**👾 ENEMY (BOSS):**\n{data['cliff']}")
        st.markdown("---")
        st.markdown(f"**🧙‍♀️ SPELL (攻略法):**\n{data['slope']}")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="rpg-box" style="background-color: #f0f8ff;">', unsafe_allow_html=True)
        st.markdown('<div class="rpg-title">📜 QUEST BOARD</div>', unsafe_allow_html=True)
        st.info(f"**🏆 MAIN QUEST:**\n\n{data['goal']}")
        st.success(f"**🏃 DAILY MISSION:**\n\n{data['action']}")
        st.markdown('</div>', unsafe_allow_html=True)

    st.divider()
    
    # PDF生成処理
    if not os.path.exists(FONT_FILE):
        st.error(f"⚠️ エラー：同じフォルダに '{FONT_FILE}' が見つかりません！")
        st.warning("1. IPAexゴシックをダウンロードしてください。\n2. ipaexg.ttf を app.py の隣に置いてください。")
    else:
        try:
            pdf_bytes = generate_pdf(data)
            if pdf_bytes:
                st.download_button(
                    label="💾 冒険の書を保存する (PDF Download)",
                    data=pdf_bytes,
                    file_name=f"{data['name']}_AdventureLog.pdf",
                    mime='application/pdf',
                    type="primary"
                )
        except Exception as e:
            st.error(f"PDF Error: {e}")

# ==========================================
# 1. サイドバー
# ==========================================
with st.sidebar:
    st.title("🧭 Mapping Console")
    st.caption("v8.2: Font Strict Mode")
    
    app_mode = st.radio("App Mode", ["📝 セッション実施 (Admin)", "🦋 Hiiro's RPG Mode (Personal)", "📂 過去ログ管理 (Archives)"])
    st.divider()

    if app_mode == "📝 セッション実施 (Admin)":
        menu = st.radio("フェーズ選択", [
            "0. 基本情報 (Setup)",
            "1. 地盤調査 (Bedrock)",
            "2. 堆積物確認 (Sediment)",
            "3. 地形測量 (Topography)",
            "4. 航路策定 (Routes)",
            "5. クライアント出力 (View)"
        ])
        
        st.divider()
        st.subheader("💾 Data Control")
        if st.button("Force Save"):
            auto_save()
            st.success("Saved!")
        
        saved_files = get_saved_files()
        if saved_files:
            selected_file = st.selectbox("Load Past Record", saved_files)
            if st.button("Load Selected"):
                load_data(selected_file)
                st.rerun()

# ==========================================
# 2. Admin Mode
# ==========================================
def section_header(title, purpose, questions):
    st.title(title)
    st.info(f"**【目的】** {purpose}")
    with st.expander("🗣️ 参謀の問い", expanded=True):
        for q in questions:
            st.markdown(f"- {q}")
    st.markdown("---")

if app_mode == "📝 セッション実施 (Admin)":
    # 0. Setup
    if menu == "0. 基本情報 (Setup)":
        st.title("📋 基本情報のセットアップ")
        col1, col2 = st.columns([2, 1])
        with col1:
            st.text_input("Client Name", key="name_input", value=st.session_state.data["name"], 
                        on_change=lambda: [st.session_state.data.update({"name": st.session_state.name_input}), auto_save()])
        with col2:
            st.text_input("Date", key="date_input", value=st.session_state.data["date"],
                        on_change=lambda: [st.session_state.data.update({"date": st.session_state.date_input}), auto_save()])
        
        st.divider()
        st.subheader("📍 仮ピン（現時点での目標・仮説）")
        st.text_area("Temporary Goal", key="temp_pin_input", value=st.session_state.data["temp_pin"], height=100, label_visibility="collapsed",
                     on_change=lambda: [st.session_state.data.update({"temp_pin": st.session_state.temp_pin_input}), auto_save()])

    # 1. Bedrock
    elif menu == "1. 地盤調査 (Bedrock)":
        section_header("🪨 Phase 1: 地盤調査", "価値観や原動力を特定する。", ["無意識にできてしまうことは？", "絶対に許せないことは？"])
        st.text_area("✍️ 譲れない価値観", key="bedrock_input", value=st.session_state.data["bedrock"], height=200,
                    on_change=lambda: [st.session_state.data.update({"bedrock": st.session_state.bedrock_input}), auto_save()])
        st.text_area("📝 メモ", key="bedrock_note_input", value=st.session_state.data.get("bedrock_note", ""), height=100,
                    on_change=lambda: [st.session_state.data.update({"bedrock_note": st.session_state.bedrock_note_input}), auto_save()])

    # 2. Sediment
    elif menu == "2. 堆積物確認 (Sediment)":
        section_header("🧱 Phase 2: 堆積物確認", "スキルやしがらみを棚卸しする。", ["今の肩書きは？", "もう使いたくないスキルは？"])
        st.text_area("✍️ スキル・肩書き", key="sediment_input", value=st.session_state.data["sediment"], height=200,
                    on_change=lambda: [st.session_state.data.update({"sediment": st.session_state.sediment_input}), auto_save()])

    # 3. Topography
    elif menu == "3. 地形測量 (Topography)":
        section_header("🧗 Phase 3: 地形測量", "『崖』を『坂』に再定義する。", ["何が怖い？", "失敗したらどうなる？"])
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("😱 崖に見えているもの")
            st.text_area("Cliff", key="cliff_input", value=st.session_state.data["cliff"], label_visibility="collapsed", height=150, 
                        on_change=lambda: [st.session_state.data.update({"cliff": st.session_state.cliff_input}), auto_save()])
        with col2:
            st.subheader("🚶 登れる坂への再定義")
            st.text_area("Slope", key="slope_input", value=st.session_state.data["slope"], label_visibility="collapsed", height=150,
                        on_change=lambda: [st.session_state.data.update({"slope": st.session_state.slope_input}), auto_save()])

    # 4. Routes
    elif menu == "4. 航路策定 (Routes)":
        section_header("🚩 Phase 4: 航路策定", "3ヶ月後の目的地を決める。", ["最低限どうなっていたい？", "明日何をする？"])
        st.text_area("🏁 3ヶ月後のゴール", key="goal_input", value=st.session_state.data["goal"], height=100,
                    on_change=lambda: [st.session_state.data.update({"goal": st.session_state.goal_input}), auto_save()])
        st.text_area("👟 Next Action", key="action_input", value=st.session_state.data["action"], height=100,
                    on_change=lambda: [st.session_state.data.update({"action": st.session_state.action_input}), auto_save()])

    # 5. View (Admin)
    elif menu == "5. クライアント出力 (View)":
        if not st.session_state.data["name"]:
            st.warning("名前を入力してください。")
        else:
            st.title("🗺️ Admin Preview (Standard)")
            st.caption("※ひいろさん用はサイドバーの「🦋 Hiiro's RPG Mode」を選択してください。")
            st.markdown("---")
            
            # 標準PDFダウンロードもここに配置
            if not os.path.exists(FONT_FILE):
                st.error(f"⚠️ エラー：同じフォルダに '{FONT_FILE}' が見つかりません！")
            else:
                try:
                    pdf_bytes = generate_pdf(st.session_state.data)
                    if pdf_bytes:
                        st.download_button(
                            label="📄 Standard PDF Download",
                            data=pdf_bytes,
                            file_name=f"{st.session_state.data['name']}_Standard.pdf",
                            mime='application/pdf'
                        )
                except Exception as e:
                    st.error(f"PDF Error: {e}")

# ==========================================
# 3. Hiiro's RPG Mode (Personal)
# ==========================================
elif app_mode == "🦋 Hiiro's RPG Mode (Personal)":
    if not st.session_state.data["name"]:
        st.warning("まずはAdminモードでデータを入力してください。")
    else:
        render_hiiro_rpg(st.session_state.data)

# ==========================================
# 4. Archives
# ==========================================
elif app_mode == "📂 過去ログ管理 (Archives)":
    st.title("📂 Session Archives")
    files = get_saved_files()
    if not files:
        st.info("データなし")
    else:
        all_records = []
        for f in files:
            path = os.path.join(DATA_DIR, f)
            try:
                with open(path, 'r', encoding='utf-8') as json_file:
                    d = json.load(json_file)
                    all_records.append(d)
            except:
                continue
        
        df = pd.DataFrame(all_records)
        display_cols = ["name", "date", "goal"]
        existing_cols = [c for c in display_cols if c in df.columns]
        st.dataframe(df[existing_cols], use_container_width=True)
        
        st.divider()
        st.subheader("🗑️ Delete")
        c1, c2 = st.columns([3, 1])
        with c1:
            file_to_delete = st.selectbox("削除ファイル", files)
        with c2:
            st.write("")
            st.write("")
            if st.button("❌ 削除"):
                delete_data(file_to_delete)
                st.rerun()