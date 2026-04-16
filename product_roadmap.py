import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(page_title="Poros 产品路线图", layout="wide")
st.title("🚀 Poros 产品路线图 2026 Q2")
st.markdown("**左侧可多选产品，选中后对应时间轴会高亮显示**")

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
    
    df["产品名称"] = df["产品名称"].astype(str).str.strip()
    
    for col in ["起始日期", "中程日期", "结束日期"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
    return df

df = load_data()

# ====================== 左侧多选（默认全部未选） ======================
st.sidebar.header("📋 产品列表（可多选）")

selected_products = []
for product in df["产品名称"].dropna().unique().tolist():
    if st.sidebar.checkbox(product, value=False, key=product):   # 默认未选中
        selected_products.append(product)

# ====================== 主图绘制 ======================
fig = go.Figure()
colors = ['#1f77b4', '#9467bd', '#2ca02c', '#ff7f0e', '#d62728']

for i, row in df.iterrows():
    product = str(row.get("产品名称", "")).strip()
    if not product:
        continue
       
    is_highlighted = product in selected_products
    color = colors[i % len(colors)]
    opacity = 1.0 if is_highlighted else 0.35
    line_width = 13 if is_highlighted else 7

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

    # 起始节点
    if pd.notna(row.get("起始日期")):
        fig.add_trace(go.Scatter(
            x=[row["起始日期"]],
            y=[product],
            mode='markers+text',
            marker=dict(size=15, color='#1f77b4', symbol='circle'),
            text=["M1"],
            textposition="top center",
            opacity=opacity,
            hovertemplate=f"<b style='font-size:18px'>{product}</b><br><span style='font-size:18px'>{row.get('M1描述', '')}</span><extra></extra>"
        ))

    # 中程节点
    if pd.notna(row.get("中程日期")):
        fig.add_trace(go.Scatter(
            x=[row["中程日期"]],
            y=[product],
            mode='markers+text',
            marker=dict(size=15, color='#9467bd', symbol='circle'),
            text=["M2"],
            textposition="top center",
            opacity=opacity,
            hovertemplate=f"<b style='font-size:18px'>{product}</b><br><span style='font-size:18px'>{row.get('M2描述', '')}</span><extra></extra>"
        ))

    # 结束节点
    if pd.notna(row.get("结束日期")):
        fig.add_trace(go.Scatter(
            x=[row["结束日期"]],
            y=[product],
            mode='markers+text',
            marker=dict(size=15, color='#2ca02c', symbol='circle'),
            text=["M3"],
            textposition="top center",
            opacity=opacity,
            hovertemplate=f"<b style='font-size:18px'>{product}</b><br><span style='font-size:18px'>{row.get('M3描述', '')}</span><extra></extra>"
        ))

# ====================== 添加三条纵向参考线（稳定方式） ======================
today = pd.Timestamp(datetime.now().date())
three_days = today + timedelta(days=3)
seven_days = today + timedelta(days=7)

# 使用 shape 添加垂直线（更稳定，避免 add_vline 错误）
fig.add_shape(type="line", x0=today, x1=today, y0=0, y1=1,
              line=dict(color="#E74C3C", width=2, dash="dash"))
fig.add_shape(type="line", x0=three_days, x1=three_days, y0=0, y1=1,
              line=dict(color="#F39C12", width=2, dash="dash"))
fig.add_shape(type="line", x0=seven_days, x1=seven_days, y0=0, y1=1,
              line=dict(color="#3498DB", width=2, dash="dash"))

# 添加文字标注
fig.add_annotation(x=today, y=1.02, text="今天", showarrow=False, font=dict(size=14, color="#E74C3C"))
fig.add_annotation(x=three_days, y=1.02, text="三天后", showarrow=False, font=dict(size=14, color="#F39C12"))
fig.add_annotation(x=seven_days, y=1.02, text="七天后", showarrow=False, font=dict(size=14, color="#3498DB"))

fig.update_layout(
    title="Poros 产品路线图 2026 Q2",
    xaxis_title="时间轴",
    yaxis_title="",
    height=1050,
    showlegend=False,
    hovermode="closest",
    plot_bgcolor="white",
    xaxis=dict(type='date', tickformat='%Y-%m-%d'),
    margin=dict(l=320, r=50, t=140, b=100),
    font=dict(size=16)
)

st.plotly_chart(fig, use_container_width=True)

# ====================== 右侧详情 ======================
st.sidebar.markdown("---")
if selected_products:
    for prod in selected_products:
        detail = df[df["产品名称"] == prod].iloc[0]
        with st.sidebar.expander(f"📋 {prod} 详细信息", expanded=False):
            st.write(f"**负责人**：{detail.get('负责人', '未填写')}")
            st.write(f"**当前状态**：{detail.get('当前状态', '未填写')}")
            st.write(f"**🔵 起始**：{detail.get('起始日期', '')} | {detail.get('M1描述', '')}")
            st.write(f"**🟣 中程**：{detail.get('中程日期', '')} | {detail.get('M2描述', '')}")
            st.write(f"**🟢 结束**：{detail.get('结束日期', '')} | {detail.get('M3描述', '')}")

st.caption("数据来源：data.xlsx | 修改Excel后重新部署即可更新")