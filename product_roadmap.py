import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

st.set_page_config(page_title="Poros 产品路线图", layout="wide")
st.title("🚀 Poros 产品路线图 2026 Q2")
st.markdown("**左侧选择产品（支持多选 + 查看全部），右侧高亮显示对应时间线**")

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

# ====================== 左侧菜单（支持多选 + 查看全部） ======================
st.sidebar.header("📋 产品列表")

# 添加“查看全部”选项
show_all = st.sidebar.checkbox("查看全部产品", value=True)

if show_all:
    selected_products = df["产品名称"].dropna().unique().tolist()
else:
    selected_products = st.sidebar.multiselect(
        "选择要查看的产品（可多选）",
        options=df["产品名称"].dropna().unique().tolist(),
        default=df["产品名称"].dropna().unique().tolist()[:3]  # 默认显示前3个
    )

# ====================== 按负责人分配柔和颜色 ======================
# 提取负责人（取第一个负责人作为主色）
df['主负责人'] = df['负责人'].astype(str).str.split('@').str[0].str.strip()

unique_owners = df['主负责人'].unique()
soft_colors = ['#4a90e2', '#7b68ee', '#50c878', '#f4a261', '#e76f51', '#2a9d8f']

owner_color_map = {owner: soft_colors[i % len(soft_colors)] for i, owner in enumerate(unique_owners)}

# ====================== 主图绘制 ======================
fig = go.Figure()

for i, row in df.iterrows():
    product = str(row.get("产品名称", "")).strip()
    if not product or product not in selected_products:
        continue
        
    owner = row['主负责人']
    color = owner_color_map.get(owner, '#6b7280')
    opacity = 1.0 if len(selected_products) <= 5 else 0.85   # 产品多时略微透明

    # 水平时间线
    if pd.notna(row.get("起始日期")) and pd.notna(row.get("结束日期")):
        fig.add_trace(go.Scatter(
            x=[row["起始日期"], row["结束日期"]],
            y=[product, product],
            mode='lines',
            line=dict(color=color, width=8),
            opacity=opacity,
            hoverinfo='skip'
        ))

    # 起始节点 + 日期
    if pd.notna(row.get("起始日期")):
        fig.add_trace(go.Scatter(
            x=[row["起始日期"]],
            y=[product],
            mode='markers+text',
            marker=dict(size=16, color='#1f77b4', symbol='circle'),
            text=[f"M1 {row['起始日期'].strftime('%m-%d')}"],
            textposition="top center",
            opacity=opacity,
            hovertemplate=f"<b>{product}</b><br>起始: {row['起始日期'].strftime('%Y-%m-%d')}<br>{row.get('M1描述', '')}<extra></extra>"
        ))

    # 中程节点 + 日期
    if pd.notna(row.get("中程日期")):
        fig.add_trace(go.Scatter(
            x=[row["中程日期"]],
            y=[product],
            mode='markers+text',
            marker=dict(size=16, color='#9467bd', symbol='circle'),
            text=[f"M2 {row['中程日期'].strftime('%m-%d')}"],
            textposition="top center",
            opacity=opacity,
            hovertemplate=f"<b>{product}</b><br>中程: {row['中程日期'].strftime('%Y-%m-%d')}<br>{row.get('M2描述', '')}<extra></extra>"
        ))

    # 结束节点 + 日期
    if pd.notna(row.get("结束日期")):
        fig.add_trace(go.Scatter(
            x=[row["结束日期"]],
            y=[product],
            mode='markers+text',
            marker=dict(size=16, color='#2ca02c', symbol='circle'),
            text=[f"M3 {row['结束日期'].strftime('%m-%d')}"],
            textposition="top center",
            opacity=opacity,
            hovertemplate=f"<b>{product}</b><br>结束: {row['结束日期'].strftime('%Y-%m-%d')}<br>{row.get('M3描述', '')}<extra></extra>"
        ))

fig.update_layout(
    title="Poros 产品路线图 2026 Q2",
    xaxis_title="时间轴",
    yaxis_title="",
    height=1000,
    showlegend=False,
    hovermode="closest",
    plot_bgcolor="#f8fafc",
    xaxis=dict(type='date', tickformat='%Y-%m-%d'),
    margin=dict(l=300, r=50, t=100, b=100),
    font=dict(size=14)   # 字体加大
)

st.plotly_chart(fig, use_container_width=True)

# ====================== 右侧详情 ======================
st.sidebar.markdown("---")
if selected_products:
    for prod in selected_products:
        detail = df[df["产品名称"] == prod].iloc[0]
        with st.sidebar.expander(f"📋 {prod} 详细信息", expanded=(len(selected_products) <= 3)):
            st.write(f"**负责人**：{detail.get('负责人', '未填写')}")
            st.write(f"**当前状态**：{detail.get('当前状态', '未填写')}")
            st.write(f"**🔵 起始**：{detail.get('起始日期', '')} | {detail.get('M1描述', '')}")
            st.write(f"**🟣 中程**：{detail.get('中程日期', '')} | {detail.get('M2描述', '')}")
            st.write(f"**🟢 结束**：{detail.get('结束日期', '')} | {detail.get('M3描述', '')}")

st.caption("数据来源：data.xlsx | 修改后重新部署即可更新")