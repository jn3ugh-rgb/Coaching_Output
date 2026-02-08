import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime
from fpdf import FPDF
from io import BytesIO

# ==========================================
# 0. 初期設定 & ライフマッピング地層モデル
# ==========================================
st.set_page_config(layout="wide", page_title="Life Mapping Strata v11.0")

# デフォルトデータ構造（名前の初期値を設定）
DEFAULT_DATA = {
    "name": "Explorer",
    "date": datetime.now().strftime("%Y-%m-%d"),
    "magma_core": "",      # 原始地盤（本能・好奇心）
    "magma_note": "",
    "sediment_layer": "",   # 堆積岩層（生存戦略・役割）
    "sediment_note": "",
    "surface_conflict": "", # 地表の歪み（現在の悩み・葛藤）
    "drill_weapon": "",     # 掘削ドリル（資格・スキル・戦略）
    "geothermal_goal": "",  # 地熱発電所（3ヶ月後の噴出口）
    "next_step": ""         
}

if "data" not in st.session_state:
    st.session_state.data = DEFAULT_DATA.copy()

# 汎用的な表示名の取得
client_name = st.session_state.data["name"] if st.session_state.data["name"] else "Explorer"

# ==========================================
# 📄 PDF生成クラス (fpdf2 / 日本語対応)
# ==========================================
# requirements.txt に fpdf2, pandas を記述すること
FONT_FILE = "ipaexg.ttf"
FONT_NAME = "IPAexGothic"

class PDFReport(FPDF):
    def header(self):
        if os.path.exists(FONT_FILE):
            self.set_font(FONT_NAME, '', 10)
        else:
            self.set_font('Helvetica', '', 10)
        self.cell(0, 10, 'Psychological Geological Survey Report', align='R', ln=True)
        self.ln(5)

    def layer_section(self, title, content, color=(240, 240, 240)):
        self.set_font(FONT_NAME, 'B', 12)
        self.set_fill_color(*color)
        self.cell(0, 10, f" {title}", fill=True, ln=True)
        self.ln(2)
        self.set_font(FONT_NAME, '', 11)
        self.multi_cell(0, 7, content)
        self.ln(5)

def generate_pdf(data):
    if not os.path.exists(FONT_FILE):
        return None
    
    pdf = PDFReport()
    pdf.add_font(FONT_NAME, '', FONT_FILE)
    pdf.set_font(FONT_NAME, '', 11)
    pdf.add_page()

    # タイトル（名前に連動）
    pdf.set_font_size(22)
    pdf.cell(0, 20, f"{client_name} 精神断面調査報告書", ln=True, align='C')
    pdf.set_font_size(10)
    pdf.cell(0, 10, f"調査実施日: {data['date']}", ln=True, align='C')
    pdf.ln(10)

    # 各レイヤーの出力
    pdf.layer_section("【深度1000m】原始地盤：マグマ・コア（本能・原動力）", data['magma_core'], color=(255, 230, 230))
    pdf.layer_section("【深度500m】堆積岩層：サバイバル・ストラテジー（役割・経験）", data['sediment_layer'], color=(240, 240, 240))
    pdf.layer_section("【地表】現在地形：地殻変動の歪み（現在の葛藤）", data['surface_conflict'], color=(255, 255, 220))
    pdf.layer_section("【戦略】掘削ドリル：変革の武器（戦略・行動）", data['drill_weapon'], color=(230, 245, 255))
    
    pdf.set_font(FONT_NAME, 'B', 14)
    pdf.cell(0, 15, "3ヶ月後の目的地：地熱発電（自己解放の状態）", ln=True)
    pdf.set_font(FONT_NAME, '', 12)
    pdf.multi_cell(0, 8, data['geothermal_goal'], border=1)

    return pdf.output()

# ==========================================
# 📊 NotebookLM / インフォグラフィック用プロンプト生成
# ==========================================
def get_infographic_prompt(data):
    name = data['name'] if data['name'] else "クライアント"
    prompt = f"""
# インフォグラフィック生成用設計図

以下の構造化データを元に、{name}さんの精神構造を「地質学的な断面図」として可視化するインフォグラフィックの構成案を作成してください。

## 1. 深度1000m：原始地盤（THE CORE MAGMA）
- 性質：純粋な好奇心、独創性、反骨心
- キーワード：{data['magma_core']}

## 2. 深度500m：堆積岩層（SURVIVAL SEDIMENT）
- 性質：生存戦略、役割、期待への応答、過去の経験
- キーワード：{data['sediment_layer']}

## 3. 地表：現在地形（CRACKED SURFACE）
- 性質：現在の葛藤、歪み、エネルギーの目詰まり
- キーワード：{data['surface_conflict']}

## 4. 戦略：掘削ドリル（DRILLING WEAPONS）
- 武器：{data['drill_weapon']}

## デザイン指示
地底から地表に向かって、マグマの熱が岩盤を突き破ろうとしている断面図を作成。
配色は「情熱の赤（深層）」「理性の灰（中層）」「現状の黄（表層）」を使用。
"""
    return prompt

# ==========================================
# 🛠️ Admin Mode (セッション入力)
# ==========================================
with st.sidebar:
    st.title("🧭 Mapping Console")
    app_mode = st.radio("App Mode", ["📝 掘削セッション (Admin)", "🌋 地質断面図 (View)"])
    st.divider()
    
    # セーブ＆ロード
    current_json = json.dumps(st.session_state.data, ensure_ascii=False, indent=4)
    save_filename = f"mapping_{client_name}_{st.session_state.data['date']}.json"
    st.download_button("💾 JSONを保存", current_json, save_filename, "application/json")
    
    uploaded_file = st.file_uploader("📂 JSONを読込", type=['json'])
    if uploaded_file:
        st.session_state.data.update(json.load(uploaded_file))

if app_mode == "📝 掘削セッション (Admin)":
    st.title("🕳️ Life-Mapping Excavation")
    
    tab1, tab2, tab3, tab4 = st.tabs(["0. Setup", "1. Core Magma", "2. Sediment", "3. Strategy"])
    
    with tab1:
        st.text_input("クライアント名", key="name_input", value=st.session_state.data["name"], 
                     on_change=lambda: st.session_state.data.update({"name": st.session_state.name_input}))
        st.text_input("日付", key="date_input", value=st.session_state.data["date"],
                     on_change=lambda: st.session_state.data.update({"date": st.session_state.date_input}))

    with tab2:
        st.subheader(f"🌋 深度1000m：原始地盤（{client_name}のマグマ）")
        st.text_area("本能的な好奇心・譲れない価値観", key="m_core", value=st.session_state.data["magma_core"], height=200,
                    on_change=lambda: st.session_state.data.update({"magma_core": st.session_state.m_core}))
        
    with tab3:
        st.subheader("🧱 深度500m：堆積岩層（生存戦略）")
        st.text_area("積み重ねたスキル・役割・しがらみ", key="s_layer", value=st.session_state.data["sediment_layer"], height=200,
                    on_change=lambda: st.session_state.data.update({"sediment_layer": st.session_state.s_layer}))
        st.subheader("🏘️ 地表：現在地形（葛藤）")
        st.text_area("今起きている歪み・悩み", key="s_conflict", value=st.session_state.data["surface_conflict"], height=150,
                    on_change=lambda: st.session_state.data.update({"surface_conflict": st.session_state.s_conflict}))

    with tab4:
        st.subheader("⚙️ 航路策定")
        st.text_area("掘削ドリル（具体的武器・戦略）", key="d_weapon", value=st.session_state.data["drill_weapon"], height=150,
                    on_change=lambda: st.session_state.data.update({"drill_weapon": st.session_state.d_weapon}))
        st.text_area("地熱発電所（3ヶ月後のゴール）", key="g_goal", value=st.session_state.data["geothermal_goal"], height=150,
                    on_change=lambda: st.session_state.data.update({"geothermal_goal": st.session_state.g_goal}))

# ==========================================
# 🌋 View Mode & NotebookLM Prompt
# ==========================================
elif app_mode == "🌋 地質断面図 (View)":
    st.title(f"🌋 {client_name}'s Geothermal Map")
    
    # シンプルな断面図表示（プレビュー）
    st.error(f"【地表：{client_name}の現在地】\n{st.session_state.data['surface_conflict']}")
    st.markdown("⬇️ (重たい生存戦略の岩盤)")
    st.info(f"【中層：形成された役割】\n{st.session_state.data['sediment_layer']}")
    st.markdown("⬇️ (煮えたぎる本能のマグマ)")
    st.warning(f"【深層：本来のエネルギー】\n{st.session_state.data['magma_core']}")
    
    st.divider()
    
    # PDF出力
    if os.path.exists(FONT_FILE):
        pdf_data = generate_pdf(st.session_state.data)
        pdf_filename = f"Survey_{client_name}_{st.session_state.data['date']}.pdf"
        st.download_button("💾 調査報告書をPDFで保存", pdf_data, pdf_filename, "application/pdf")
    else:
        st.warning("ipaexg.ttf が見つからないためPDF出力はスキップされます。")

    # NotebookLM用プロンプト表示
    st.subheader("🎨 インフォグラフィック用プロンプト")
    st.markdown(f"このテキストをコピーして、NotebookLMや画像生成AIに渡してください。{client_name}さんの断面図が生成されます。")
    st.code(get_infographic_prompt(st.session_state.data))