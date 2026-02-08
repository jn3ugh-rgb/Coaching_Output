import streamlit as st
import json
import os
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from fpdf import FPDF

# ==========================================
# 0. 初期設定 & ライフマッピング地層モデル
# ==========================================
st.set_page_config(layout="wide", page_title="Life Mapping Strata Console")

# デフォルトデータ
DEFAULT_DATA = {
    "name": "Explorer",
    "date": datetime.now().strftime("%Y-%m-%d"),
    "magma_core": "",      # 原始地盤（本能）
    "sediment_layer": "",   # 堆積岩層（役割）
    "surface_conflict": "", # 地表（葛藤）
    "drill_weapon": "",     # 戦略
    "geothermal_goal": ""   # 目的地
}

if "data" not in st.session_state:
    st.session_state.data = DEFAULT_DATA.copy()

client_name = st.session_state.data["name"] if st.session_state.data["name"] else "Explorer"

# ==========================================
# 📄 PDF生成クラス (fpdf2)
# ==========================================
FONT_FILE = "ipaexg.ttf"
FONT_NAME = "IPAexGothic"

class PDFReport(FPDF):
    def header(self):
        if os.path.exists(FONT_FILE):
            self.add_font(FONT_NAME, '', FONT_FILE)
            self.set_font(FONT_NAME, '', 10)
        else:
            self.set_font('Helvetica', '', 10)
        self.cell(0, 10, 'Psychological Geological Survey Report', align='R', ln=True)

    def layer_section(self, title, content, color=(240, 240, 240)):
        self.set_font(FONT_NAME, 'B', 12)
        self.set_fill_color(*color)
        self.cell(0, 10, f" {title}", fill=True, ln=True)
        self.set_font(FONT_NAME, '', 11)
        self.multi_cell(0, 7, content)
        self.ln(5)

def generate_pdf(data):
    if not os.path.exists(FONT_FILE): return None
    pdf = PDFReport()
    pdf.add_font(FONT_NAME, '', FONT_FILE)
    pdf.add_page()
    pdf.set_font(FONT_NAME, 'B', 22)
    pdf.cell(0, 20, f"{client_name} 精神断面調査報告書", ln=True, align='C')
    pdf.set_font(FONT_NAME, '', 10)
    pdf.cell(0, 10, f"Date: {data['date']}", ln=True, align='C')
    pdf.ln(10)
    pdf.layer_section("【深層】原始地盤（マグマ）", data['magma_core'], (255, 230, 230))
    pdf.layer_section("【中層】堆積岩層（生存戦略）", data['sediment_layer'], (240, 240, 240))
    pdf.layer_section("【表層】現在地形（歪み）", data['surface_conflict'], (255, 255, 220))
    return pdf.output()

# ==========================================
# 🌋 Plotly による地層の視覚化
# ==========================================
def render_strata_chart(data):
    # 地層を積み上げ棒グラフで表現
    fig = go.Figure()
    
    # 各層の厚みを定義（視覚的なダミー値）
    layers = [
        {"name": "原始地盤 (Magma)", "val": 30, "color": "salmon", "text": data['magma_core']},
        {"name": "堆積岩層 (Sediment)", "val": 40, "color": "lightgrey", "text": data['sediment_layer']},
        {"name": "地表 (Surface)", "val": 15, "color": "khaki", "text": data['surface_conflict']}
    ]
    
    for l in layers:
        fig.add_trace(go.Bar(
            name=l['name'],
            x=[client_name],
            y=[l['val']],
            marker_color=l['color'],
            hovertext=l['text'],
            hovertemplate="<b>%{short_name}</b><br>%{hovertext}<extra></extra>"
        ))

    fig.update_layout(
        barmode='stack',
        title=f"{client_name} の精神断面図 (Strata Analysis)",
        xaxis_title="クライアント",
        yaxis_title="深度 / 精神的重圧",
        height=500,
        showlegend=True
    )
    st.plotly_chart(fig, use_container_width=True)

# ==========================================
# 🛠️ メインUI
# ==========================================
with st.sidebar:
    st.title("🧭 Mapping Console")
    app_mode = st.radio("Mode", ["📝 掘削セッション", "🌋 地質断面図(View)"])
    st.divider()
    save_data = json.dumps(st.session_state.data, ensure_ascii=False, indent=4)
    st.download_button("💾 JSON保存", save_data, f"mapping_{client_name}.json")
    uploaded = st.file_uploader("📂 JSON読込", type=['json'])
    if uploaded: st.session_state.data.update(json.load(uploaded))

if app_mode == "📝 掘削セッション":
    st.title(f"🕳️ Excavation: {client_name}")
    t0, t1, t2, t3 = st.tabs(["Setup", "1. Magma", "2. Strata", "3. Goals"])
    
    with t0:
        st.text_input("クライアント名", key="name_in", value=st.session_state.data["name"], 
                     on_change=lambda: st.session_state.data.update({"name": st.session_state.name_in}))
    with t1:
        st.text_area("深層：原始地盤（本能・原動力）", key="m_c", value=st.session_state.data["magma_core"], height=200,
                    on_change=lambda: st.session_state.data.update({"magma_core": st.session_state.m_c}))
    with t2:
        st.text_area("中層：堆積岩層（役割・経験）", key="s_l", value=st.session_state.data["sediment_layer"], height=150,
                    on_change=lambda: st.session_state.data.update({"sediment_layer": st.session_state.s_l}))
        st.text_area("表層：現在地形（葛藤）", key="s_c", value=st.session_state.data["surface_conflict"],
                    on_change=lambda: st.session_state.data.update({"surface_conflict": st.session_state.s_c}))
    with t3:
        st.text_area("戦略・武器", key="d_w", value=st.session_state.data["drill_weapon"],
                    on_change=lambda: st.session_state.data.update({"drill_weapon": st.session_state.d_w}))
        st.text_area("3ヶ月後の目標", key="g_g", value=st.session_state.data["geothermal_goal"],
                    on_change=lambda: st.session_state.data.update({"geothermal_goal": st.session_state.g_g}))

elif app_mode == "🌋 地質断面図(View)":
    st.title(f"🌋 {client_name}'s Strata Chart")
    
    # Plotlyでビジュアル表示
    render_strata_chart(st.session_state.data)
    
    st.divider()
    
    if os.path.exists(FONT_FILE):
        pdf = generate_pdf(st.session_state.data)
        st.download_button("💾 PDFレポート保存", pdf, f"Report_{client_name}.pdf")

    st.subheader("🎨 NotebookLM用プロンプト")
    st.code(f"以下のデータを元に、{client_name}さんの地質断面インフォグラフィックを作成して。\n1.深層：{st.session_state.data['magma_core']}\n2.中層：{st.session_state.data['sediment_layer']}\n3.表層：{st.session_state.data['surface_conflict']}")