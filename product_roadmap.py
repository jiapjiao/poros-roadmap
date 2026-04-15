import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Poros 产品路线图", layout="wide")
st.title("🚀 Poros 产品路线图 2026 Q2")
st.markdown("**左侧勾选产品（可多选），选中后对应时间轴会明显高亮**")

# ====================== 加载数据 ======================
@st.cache_data
def load_data():
    df = pd.read_excel("data.xlsx", sheet_name="产品信息与Milestone")
    
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

# ====================== 左侧多选 ======================
st.sidebar.header("📋 产品列表（可多选）")

selected_products = []
for product in df["产品名称"].dropna().unique().tolist():
    if st.sidebar.checkbox(product, value=True, key=product):
        selected_products.append(product)

# ====================== 高亮颜色 ======================
highlight_colors = ['#E74C3C', '#F39C12', '#F1C40F', '#3498DB', '#9B59B6', '#1ABC9C']

# ====================== 主图 ======================
fig = go.Figure()

for i, row in df.iterrows():
    product = str(row.get("产品名称", "")).strip()
    if not product:
        continue
        
    is_highlighted = product in selected_products
    opacity = 1.0 if is_highlighted else 0.25
    line_width = 16 if is_highlighted else 5.5   # 明显加粗

    color = highlight_colors[i % len(highlight_colors)] if is_highlighted else '#95a5a6'

    # 时间线
    if pd.notna(row.get("起始日期")) and pd.notna(row.get("结束日期")):
        fig.add_trace(go.Scatter(
            x=[row["起始日期"], row["结束日期"]],
            y=[product, product],
            mode='lines',
            line=dict(color=color, width=line_width),
            opacity=opacity,
            hoverinfo='skip'
        ))

    # 节点（只显示日期，不显示M1/M2/M3标签）
    if pd.notna(row.get("起始日期")):
        fig.add_trace(go.Scatter(
            x=[row["起始日期"]],
            y=[product],
            mode='markers+text',
            marker=dict(size=18, color='#2c7da0'),
            text=[row['起始日期'].strftime('%m-%d')],
            textposition="top center",
            textfont=dict(size=14),
            opacity=opacity,
            hovertemplate=f"<b>{product}</b><br>{row.get('M1描述', '无描述')}<extra></extra>"
        ))

    if pd.notna(row.get("中程日期")):
        fig.add_trace(go.Scatter(
            x=[row["中程日期"]],
            y=[product],
            mode='markers+text',
            marker=dict(size=18, color='#8b6fb8'),
            text=[row['中程日期'].strftime('%m-%d')],
            textposition="top center",
            textfont=dict(size=14),
            opacity=opacity,
            hovertemplate=f"<b>{product}</b><br>{row.get('M2描述', '无描述')}<extra></extra>"
        ))

    if pd.notna(row.get("结束日期")):
        fig.add_trace(go.Scatter(
            x=[row["结束日期"]],
            y=[product],
            mode='markers+text',
            marker=dict(size=18, color='#4a9b6e'),
            text=[row['结束日期'].strftime('%m-%d')],
            textposition="top center",
            textfont=dict(size=14),
            opacity=opacity,
            hovertemplate=f"<b>{product}</b><br>{row.get('M3描述', '无描述')}<extra></extra>"
        ))

fig.update_layout(
    title="Poros 产品路线图 2026 Q2",
    xaxis_title="时间轴",
    yaxis_title="",
    height=1100,
    showlegend=False,
    hovermode="closest",
    plot_bgcolor="#f8fafc",
    xaxis=dict(type='date', tickformat='%Y-%m-%d'),
    margin=dict(l=340, r=60, t=120, b=100),
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

st.caption("数据来源：data.xlsx | 修改后重新部署即可更新")