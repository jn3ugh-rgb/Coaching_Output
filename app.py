import streamlit as st
import json
import os
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from fpdf import FPDF

# ==========================================
# 0. 初期設定
# ==========================================
st.set_page_config(layout="wide", page_title="Life Mapping Console v14.0")

# デフォルトデータ（質問項目はv8.0形式を維持）
DEFAULT_DATA = {
    "name": "",
    "date": datetime.now().strftime("%Y-%m-%d"),
    "temp_pin": "",
    "bedrock": "",
    "sediment": "",
    "cliff": "",
    "slope": "",
    "goal": "",
    "action": ""
}

if "data" not in st.session_state:
    st.session_state.data = DEFAULT_DATA.copy()

client_name = st.session_state.data["name"] if st.session_state.data["name"] else "クライアント"

# ==========================================
# 📄 PDF生成：セッション後分析レポート形式
# ==========================================
FONT_FILE = "ipaexg.ttf"
FONT_NAME = "IPAexGothic"

class AnalysisReport(FPDF):
    def header(self):
        if os.path.exists(FONT_FILE):
            self.add_font(FONT_NAME, '', FONT_FILE)
            self.set_font(FONT_NAME, '', 9)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, 'Life Mapping Strategy Report', align='R', ln=True)
        self.ln(5)

    def section_title(self, label):
        self.set_font(FONT_NAME, 'B', 13)
        self.set_fill_color(248, 248, 248)
        self.set_text_color(60, 60, 60)
        self.cell(0, 10, f"  {label}", fill=True, ln=True)
        self.ln(3)

    def section_body(self, text):
        self.set_font(FONT_NAME, '', 11)
        self.set_text_color(40, 40, 40)
        self.multi_cell(0, 7, text)
        self.ln(5)

def generate_pdf(data):
    pdf = AnalysisReport()
    if os.path.exists(FONT_FILE):
        pdf.add_font(FONT_NAME, '', FONT_FILE)
        pdf.set_font(FONT_NAME, '', 12)
    pdf.add_page()

    # タイトル
    pdf.set_font(FONT_NAME, 'B', 18)
    pdf.cell(0, 15, "セッション後分析レポート", ln=True, align='L')
    pdf.set_font(FONT_NAME, '', 11)
    pdf.cell(0, 8, f"クライアント名：{data['name']} 様 / 作成日：{data['date']}", ln=True, align='L')
    pdf.ln(10)

    # 各フェーズ
    pdf.section_title("Phase 1：地盤調査（本質的な原動力）")
    pdf.section_body(data['bedrock'])
    
    pdf.section_title("Phase 2：堆積物確認（これまでの経験と役割）")
    pdf.section_body(data['sediment'])

    pdf.section_title("Phase 3：地形測量（課題の再定義）")
    pdf.set_font(FONT_NAME, 'B', 11)
    pdf.cell(0, 8, "【心理的な壁：崖】", ln=True)
    pdf.section_body(data['cliff'])
    pdf.cell(0, 8, "【攻略ルート：坂】", ln=True)
    pdf.section_body(data['slope'])

    pdf.section_title("Phase 4：航路策定（具体的アクション）")
    pdf.set_font(FONT_NAME, 'B', 11)
    pdf.cell(0, 8, "【3ヶ月後の目的地】", ln=True)
    pdf.section_body(data['goal'])
    pdf.cell(0, 8, "【最初の一歩】", ln=True)
    pdf.section_body(data['action'])

    return pdf.output()

# ==========================================
# 📊 NotebookLM 用プロンプト生成
# ==========================================
def get_notebooklm_prompt(data):
    name = data['name'] if data['name'] else "対象者"
    return f"""
# セッション後分析レポート：構造化データ

以下の構造化データとセッションログを照らし合わせ、{name}さんのための詳細な分析レポートを作成してください。

## 1. 構造化データ
- 【地盤（原動力）】: {data['bedrock']}
- 【堆積物（経験）】: {data['sediment']}
- 【崖（葛藤）】: {data['cliff']}
- 【坂（再定義）】: {data['slope']}
- 【目的地（ゴール）】: {data['goal']}

## 2. インフォグラフィック生成指示（差し込み図用）
レポートのPhase 3に差し込むための、精神構造の地殻断面図を設計してください。
- デザイン：ミニマルで清潔感のあるトーン。
- 配色：テラコッタ（赤）、ウォームグレー（灰）、サンドベージュ（地表）、ペールイエロー（光）。ナチュラルなアースカラーに統一。
- 構成：深層のマグマが重厚な堆積層を貫き、地表へ噴出口を作る様子を可視化。

このデータを元に、説得力のある「セッション後分析レポート」の本文を執筆してください。
"""

# ==========================================
# 🛠️ メインUI
# ==========================================
with st.sidebar:
    st.title("🧭 Mapping Console")
    app_mode = st.radio("表示モード", ["📝 セッション入力", "🌋 断面図プレビュー", "📊 NotebookLM出力"])
    st.divider()
    
    # セキュアなデータ管理
    current_json = json.dumps(st.session_state.data, ensure_ascii=False, indent=4)
    st.download_button("📥 JSONデータを保存", current_json, f"mapping_{client_name}.json")
    
    uploaded = st.file_uploader("📂 JSONを読み込む", type=['json'])
    if uploaded:
        st.session_state.data.update(json.load(uploaded))

if app_mode == "📝 セッション入力":
    st.title(f"🕳️ Excavation: {client_name}")
    tabs = st.tabs(["Setup", "1. Bedrock", "2. Sediment", "3. Topography", "4. Routes"])
    
    with tabs[0]:
        st.text_input("クライアント名", key="name_in", value=st.session_state.data["name"], on_change=lambda: st.session_state.data.update({"name": st.session_state.name_in}))
        st.text_area("仮ピン (Temporary Goal)", key="temp_in", value=st.session_state.data["temp_pin"], on_change=lambda: st.session_state.data.update({"temp_pin": st.session_state.temp_in}))
    
    with tabs[1]:
        st.text_area("Phase 1: 地盤（原動力）", key="b_in", value=st.session_state.data["bedrock"], height=250, on_change=lambda: st.session_state.data.update({"bedrock": st.session_state.b_in}))
    
    with tabs[2]:
        st.text_area("Phase 2: 堆積物（経験・しがらみ）", key="s_in", value=st.session_state.data["sediment"], height=250, on_change=lambda: st.session_state.data.update({"sediment": st.session_state.s_in}))
    
    with tabs[3]:
        c1, c2 = st.columns(2)
        with c1: st.text_area("😱 崖 (崖に見えているもの)", key="c_in", value=st.session_state.data["cliff"], height=200, on_change=lambda: st.session_state.data.update({"cliff": st.session_state.c_in}))
        with c2: st.text_area("🚶 坂 (再定義)", key="sl_in", value=st.session_state.data["slope"], height=200, on_change=lambda: st.session_state.data.update({"slope": st.session_state.sl_in}))
    
    with tabs[4]:
        st.text_area("🏁 目的地 (Goal)", key="g_in", value=st.session_state.data["goal"], on_change=lambda: st.session_state.data.update({"goal": st.session_state.g_in}))
        st.text_area("👟 Next Action", key="a_in", value=st.session_state.data["action"], on_change=lambda: st.session_state.data.update({"action": st.session_state.a_in}))

elif app_mode == "🌋 断面図プレビュー":
    st.title(f"🌋 {client_name} 様 断面図構造")
    
    # Plotlyによる簡易視覚化（アースカラー採用）
    fig = go.Figure()
    fig.add_trace(go.Bar(name="地表 (Surface)", x=[client_name], y=[15], marker_color="#E6D5B8", hovertext=st.session_state.data['cliff']))
    fig.add_trace(go.Bar(name="堆積岩 (Sediment)", x=[client_name], y=[40], marker_color="#8D8D8D", hovertext=st.session_state.data['sediment']))
    fig.add_trace(go.Bar(name="原始地盤 (Magma)", x=[client_name], y=[30], marker_color="#C06C84", hovertext=st.session_state.data['bedrock']))
    
    fig.update_layout(barmode='stack', title="精神断面の構成（プレビュー）", yaxis_title="深度", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)
    
    

    if os.path.exists(FONT_FILE):
        pdf_out = generate_pdf(st.session_state.data)
        st.download_button("💾 分析レポート(PDF)をダウンロード", pdf_out, f"AnalysisReport_{client_name}.pdf", "application/pdf")

elif app_mode == "📊 NotebookLM出力":
    st.title("📊 NotebookLM 連携用出力")
    st.markdown("以下のプロンプトをコピーして、NotebookLMのソース（またはチャット）に追加してください。レポート本文とインフォグラフィックの設計図が生成されます。")
    st.code(get_notebooklm_prompt(st.session_state.data))