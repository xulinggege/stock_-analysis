import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timedelta
import data_loader

# 设置页面配置
st.set_page_config(
    page_title="A股股票分析",
    page_icon="📈",
    layout="wide"
)

# 侧边栏配置
st.sidebar.header("参数设置")

# 股票代码输入
stock_code = st.sidebar.text_input("股票代码", value="600519", help="请输入6位股票代码，如 600519")

# 日期范围选择
today = datetime.now()
half_year_ago = today - timedelta(days=180)

col1, col2 = st.sidebar.columns(2)
with col1:
    start_date = st.date_input("开始日期", value=half_year_ago)
with col2:
    end_date = st.date_input("结束日期", value=today)

# 分析按钮
if st.sidebar.button("开始分析", type="primary"):
    with st.spinner("正在获取数据并生成图表..."):
        # 格式化日期为 YYYYMMDD
        s_date_str = start_date.strftime('%Y%m%d')
        e_date_str = end_date.strftime('%Y%m%d')
        
        # 获取数据
        try:
            df = data_loader.get_stock_data(stock_code, s_date_str, e_date_str)
            
            if df.empty:
                st.error("未获取到数据，请检查股票代码或日期范围。")
            else:
                # 页面主标题
                st.title(f"📈 {stock_code} 股价与换手率分析")
                
                # 创建子图：K线图 (row=1) 和 换手率图 (row=2)
                fig = make_subplots(
                    rows=2, cols=1, 
                    shared_xaxes=True, 
                    vertical_spacing=0.05,
                    row_heights=[0.7, 0.3],
                    subplot_titles=('K线图 (K-Line)', '换手率 (Turnover Rate)')
                )

                # 1. 绘制 K 线图
                # 计算移动平均线
                df['MA5'] = df['Close'].rolling(window=5).mean()
                df['MA10'] = df['Close'].rolling(window=10).mean()
                df['MA20'] = df['Close'].rolling(window=20).mean()

                # K线
                fig.add_trace(go.Candlestick(
                    x=df.index,
                    open=df['Open'],
                    high=df['High'],
                    low=df['Low'],
                    close=df['Close'],
                    name='K线'
                ), row=1, col=1)

                # 均线
                fig.add_trace(go.Scatter(x=df.index, y=df['MA5'], line=dict(color='blue', width=1), name='MA5'), row=1, col=1)
                fig.add_trace(go.Scatter(x=df.index, y=df['MA10'], line=dict(color='orange', width=1), name='MA10'), row=1, col=1)
                fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], line=dict(color='green', width=1), name='MA20'), row=1, col=1)

                # 2. 绘制换手率图
                # 颜色区分：上涨红，下跌绿 (中国习惯：红涨绿跌)
                colors = ['red' if row['Close'] >= row['Open'] else 'green' for i, row in df.iterrows()]
                
                fig.add_trace(go.Bar(
                    x=df.index,
                    y=df['Turnover'],
                    name='换手率',
                    marker_color=colors
                ), row=2, col=1)

                # 更新布局
                fig.update_layout(
                    height=800,
                    xaxis_rangeslider_visible=False,
                    title_text=f"股票代码: {stock_code} ({start_date} - {end_date})",
                    hovermode='x unified' # 统一显示 hover 信息
                )
                
                # 更新坐标轴标签
                fig.update_yaxes(title_text="价格", row=1, col=1)
                fig.update_yaxes(title_text="换手率 (%)", row=2, col=1)

                # 在 Streamlit 中展示 Plotly 图表
                st.plotly_chart(fig, use_container_width=True)

                # 展示原始数据 (可选)
                with st.expander("查看原始数据"):
                    st.dataframe(df.sort_index(ascending=False))

        except Exception as e:
            st.error(f"发生错误: {str(e)}")

else:
    st.info("请在左侧设置参数并点击“开始分析”按钮。")
