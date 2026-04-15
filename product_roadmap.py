import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="Poros 产品路线图", layout="wide")
st.title("🚀 Poros 产品路线图 2026 Q2")
st.markdown("**左侧点击产品名称，可高亮查看该产品的起始、中程、结束节点**")

# ====================== 加载数据 ======================
@st.cache_data
def load_data():
    file_path = "data.xlsx"
    df = pd.read_excel(file_path, sheet_name="产品信息与Milestone")
    
    df = df.rename(columns={
        "产品名称": "产品名称",
        "负责人": "负责人",
        "当前状态": "当前状态",
        "Milestone 起始": "M1描述",
        "起始日期": "起始日期",
        "Milestone 中程1": "M2描述",
        "中程日期1": "中程日期",
        "Milestone 结束": "M3描述",
        "结束日期": "结束日期"
    })
    
    for col in ["起始日期", "中程日期", "结束日期"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
    return df

df = load_data()

# ====================== 左侧菜单 ======================
st.sidebar.header("📋 产品列表")
product_list = df["产品名称"].dropna().unique().tolist()

if not product_list:
    st.error("未读取到产品数据，请确保 data.xlsx 已上传！")
    st.stop()

selected_product = st.sidebar.radio("选择产品查看详情", product_list)

# ====================== 主图绘制 ======================
fig = go.Figure()
colors = ['#1f77b4', '#9467bd', '#2ca02c', '#ff7f0e', '#d62728']

for i, row in df.iterrows():
    product = str(row.get("产品名称", "")).strip()
    if not product:
        continue
       
    color = colors[i % len(colors)]
    opacity = 1.0 if product == selected_product else 0.3
    line_width = 12 if product == selected_product else 7   # 高亮时加粗

    # 水平时间线
    if pd.notna(row.get("起始日期")) and pd.notna(row.get("结束日期")):
        fig.add_trace(go.Scatter(
            x=[row["起始日期"], row["结束日期"]],
            y=[product, product],
            mode='lines',
            line=dict(color=color, width=line_width),
            opacity=opacity,
            hoverinfo='skip'
        ))

    # 起始节点 (蓝色)
    if pd.notna(row.get("起始日期")):
        fig.add_trace(go.Scatter(
            x=[row["起始日期"]],
            y=[product],
            mode='markers+text',
            marker=dict(size=15, color='#1f77b4', symbol='circle'),
            text=["M1"],
            textposition="top center",
            opacity=opacity,
            hovertemplate=f"<b>{product}</b><br>起始: {row['起始日期'].strftime('%Y-%m-%d')}<br>{row.get('M1描述', '')}<extra></extra>"
        ))

    # 中程节点 (紫色)
    if pd.notna(row.get("中程日期")):
        fig.add_trace(go.Scatter(
            x=[row["中程日期"]],
            y=[product],
            mode='markers+text',
            marker=dict(size=15, color='#9467bd', symbol='circle'),
            text=["M2"],
            textposition="top center",
            opacity=opacity,
            hovertemplate=f"<b>{product}</b><br>中程: {row['中程日期'].strftime('%Y-%m-%d')}<br>{row.get('M2描述', '')}<extra></extra>"
        ))

    # 结束节点 (绿色)
    if pd.notna(row.get("结束日期")):
        fig.add_trace(go.Scatter(
            x=[row["结束日期"]],
            y=[product],
            mode='markers+text',
            marker=dict(size=15, color='#2ca02c', symbol='circle'),
            text=["M3"],
            textposition="top center",
            opacity=opacity,
            hovertemplate=f"<b>{product}</b><br>结束: {row['结束日期'].strftime('%Y-%m-%d')}<br>{row.get('M3描述', '')}<extra></extra>"
        ))

fig.update_layout(
    title="Poros 产品路线图（点击左侧菜单切换产品）",
    xaxis_title="时间轴",
    yaxis_title="",
    height=950,
    showlegend=False,
    hovermode="closest",
    plot_bgcolor="white",
    xaxis=dict(type='date', tickformat='%Y-%m-%d'),
    margin=dict(l=300, r=50, t=100, b=100),
    font=dict(size=18)   # 全局字体加大
)

st.plotly_chart(fig, use_container_width=True)

# ====================== 右侧详情 ======================
st.sidebar.markdown("---")
if selected_product:
    detail = df[df["产品名称"].str.strip() == selected_product].iloc[0]
    st.sidebar.subheader(f"📋 {selected_product} 详细信息")
    st.sidebar.write(f"**负责人**：{detail.get('负责人', '未填写')}")
    st.sidebar.write(f"**当前状态**：{detail.get('当前状态', '未填写')}")
   
    st.sidebar.markdown("**🔵 起始节点**")
    st.sidebar.write(f"日期：{detail.get('起始日期', '未填写')}")
    st.sidebar.write(f"描述：{detail.get('M1描述', '未填写')}")
   
    st.sidebar.markdown("**🟣 中程节点**")
    st.sidebar.write(f"日期：{detail.get('中程日期', '未填写')}")
    st.sidebar.write(f"描述：{detail.get('M2描述', '未填写')}")
   
    st.sidebar.markdown("**🟢 结束节点**")
    st.sidebar.write(f"日期：{detail.get('结束日期', '未填写')}")
    st.sidebar.write(f"描述：{detail.get('M3描述', '未填写')}")

st.caption("数据来源：data.xlsx | 修改Excel后重新部署即可更新")