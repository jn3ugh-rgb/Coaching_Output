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
st.set_page_config(layout="wide", page_title="Life Mapping Console v15.0")

# デフォルトデータ（v8.0の項目を継承）
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
        self.set_text_color(160, 160, 160)
        self.cell(0, 10, 'Life Mapping Strategy Analysis', align='R', ln=True)
        self.ln(5)

    def section_title(self, label):
        self.set_font(FONT_NAME, 'B', 13)
        self.set_fill_color(250, 250, 250)
        self.set_text_color(70, 70, 70)
        self.cell(0, 10, f"  {label}", fill=True, ln=True)
        self.ln(3)

    def section_body(self, text):
        self.set_font(FONT_NAME, '', 11)
        self.set_text_color(50, 50, 50)
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
    pdf.set_font(FONT_NAME, '', 10)
    pdf.cell(0, 8, f"対象：{data['name']} 様 / 作成日：{data['date']}", ln=True, align='L')
    pdf.ln(10)

    # 各セクション
    pdf.section_title("Phase 1：地盤（本来の原動力）")
    pdf.section_body(data['bedrock'])
    
    pdf.section_title("Phase 2：堆積物（経験としがらみ）")
    pdf.section_body(data['sediment'])

    pdf.section_title("Phase 3：地形（崖と坂の再定義）")
    pdf.section_body(f"【現在の葛藤】\n{data['cliff']}\n\n【新たな進路】\n{data['slope']}")

    pdf.section_title("Phase 4：航路（これからの実行計画）")
    pdf.section_body(f"【3ヶ月後の目的地】\n{data['goal']}\n\n【最初の一歩】\n{data['action']}")

    return pdf.output()

# ==========================================
# 📊 NotebookLM 用プロンプト（柔らかいトーン指定）
# ==========================================
def get_notebooklm_prompt(data):
    name = data['name'] if data['name'] else "クライアント"
    return f"""
# 命令書：セッション後分析レポートの執筆

あなたは一流のライフ・ストラテジストとして、{name}さんのための「セッション後分析レポート」を執筆してください。

## 【執筆スタイル】
- 「です・ます」調で整えてください。
- ただし、「ございます」「しております」といった過剰な敬語表現は抑え、親しみやすさと誠実さが伝わる柔らかい表現を心がけてください。
- 専門用語を多用せず、心にスッと入ってくるような、見やすく、読み心地の良い文章にしてください。

## 【レポートの構成要素】
以下の構造化データと、別途提供するセッションログを統合して分析してください。

1. 地盤（本来の原動力）：
   {data['bedrock']}
2. 堆積物（これまでの経験・役割）：
   {data['sediment']}
3. 地形（現在の崖と、これから登る坂）：
   {data['cliff']} / {data['slope']}
4. 航路（目的地と最初の一歩）：
   {data['goal']} / {data['action']}

## 【インフォグラフィック生成指示（差し込み図用）】
レポートに差し込む「精神断面図」の設計案も出力してください。
- デザイン：ミニマルで清潔感のあるスタイル。
- 配色：テラコッタ（深層）、ウォームグレー（中層）、サンドベージュ（地表）、ペールイエロー（光）。ナチュラルなアースカラーで構成し、視覚的なノイズを削ぎ落としてください。
- 構図：深層のマグマの熱が、厚い岩盤を貫き、地表へ新しい噴出口を作る様子を描写してください。

この内容を元に、{name}さんが「自分の人生を自分で描ける」という確信を持てるような、温かいレポートを執筆してください。
"""

# ==========================================
# 🛠️ メインUI
# ==========================================
with st.sidebar:
    st.title("🧭 Mapping Console")
    app_mode = st.radio("Mode", ["📝 セッション入力", "🌋 構造プレビュー", "📊 NotebookLM出力"])
    st.divider()
    
    # ローカルJSON管理
    current_json = json.dumps(st.session_state.data, ensure_ascii=False, indent=4)
    st.download_button("📥 JSONデータを保存", current_json, f"mapping_{client_name}.json")
    
    uploaded = st.file_uploader("📂 JSONを読み込む", type=['json'])
    if uploaded:
        st.session_state.data.update(json.load(uploaded))

if app_mode == "📝 セッション入力":
    st.title(f"🕳️ Session Info: {client_name}")
    tabs = st.tabs(["Setup", "1. Bedrock", "2. Sediment", "3. Topography", "4. Routes"])
    
    with tabs[0]:
        st.text_input("クライアント名", key="name_in", value=st.session_state.data["name"], on_change=lambda: st.session_state.data.update({"name": st.session_state.name_in}))
        st.text_area("仮ピン (Temp Goal)", key="temp_in", value=st.session_state.data["temp_pin"], on_change=lambda: st.session_state.data.update({"temp_pin": st.session_state.temp_in}))
    
    with tabs[1]:
        st.subheader("Phase 1: 地盤（本来の原動力）")
        st.text_area("価値観・好奇心の源泉", key="b_in", value=st.session_state.data["bedrock"], height=250, on_change=lambda: st.session_state.data.update({"bedrock": st.session_state.b_in}))
    
    with tabs[2]:
        st.subheader("Phase 2: 堆積物（経験としがらみ）")
        st.text_area("スキル・役割・防衛本能", key="s_in", value=st.session_state.data["sediment"], height=250, on_change=lambda: st.session_state.data.update({"sediment": st.session_state.s_in}))
    
    with tabs[3]:
        st.subheader("Phase 3: 地形（崖から坂へ）")
        c1, c2 = st.columns(2)
        with c1: st.text_area("😱 崖に見えているもの", key="c_in", value=st.session_state.data["cliff"], height=200, on_change=lambda: st.session_state.data.update({"cliff": st.session_state.c_in}))
        with c2: st.text_area("🚶 坂への再定義", key="sl_in", value=st.session_state.data["slope"], height=200, on_change=lambda: st.session_state.data.update({"slope": st.session_state.sl_in}))
    
    with tabs[4]:
        st.subheader("Phase 4: 航路（具体的計画）")
        st.text_area("🏁 目的地 (3ヶ月後)", key="g_in", value=st.session_state.data["goal"], on_change=lambda: st.session_state.data.update({"goal": st.session_state.g_in}))
        st.text_area("👟 最初の一歩", key="a_in", value=st.session_state.data["action"], on_change=lambda: st.session_state.data.update({"action": st.session_state.a_in}))

elif app_mode == "🌋 構造プレビュー":
    st.title(f"🌋 {client_name} 様 の精神構造分析")
    
    # 地層スタックチャート
    fig = go.Figure()
    fig.add_trace(go.Bar(name="地表 (Surface)", x=[client_name], y=[15], marker_color="#E6D5B8", hovertext=st.session_state.data['cliff']))
    fig.add_trace(go.Bar(name="堆積岩 (Sediment)", x=[client_name], y=[40], marker_color="#A5A5A5", hovertext=st.session_state.data['sediment']))
    fig.add_trace(go.Bar(name="原始地盤 (Magma)", x=[client_name], y=[30], marker_color="#D17D6B", hovertext=st.session_state.data['bedrock']))
    
    fig.update_layout(barmode='stack', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', yaxis_title="深度 / 精神的重圧")
    st.plotly_chart(fig, use_container_width=True)

    if os.path.exists(FONT_FILE):
        pdf_out = generate_pdf(st.session_state.data)
        st.download_button("💾 レポートをPDFで出力", pdf_out, f"AnalysisReport_{client_name}.pdf")

elif app_mode == "📊 NotebookLM出力":
    st.title("📊 NotebookLM 連携用プロンプト")
    st.markdown("このプロンプトを NotebookLM にコピー＆ペーストしてください。柔らかいトーンでのレポート本文とインフォグラフィック案が生成されます。")
    st.code(get_notebooklm_prompt(st.session_state.data))