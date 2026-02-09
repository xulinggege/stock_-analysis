import mplfinance as mpf
import pandas as pd

def plot_stock_analysis(data: pd.DataFrame, stock_code: str, **kwargs):
    """
    绘制股票价格走势和换手率分析图
    
    Args:
        data (pd.DataFrame): 包含 Open, High, Low, Close, Turnover 列的数据
        stock_code (str): 股票代码
        **kwargs: 额外参数，支持 savefig
    """
    if data.empty:
        print("数据为空，无法绘图。")
        return

    # 设置绘图风格
    # binance, nightclouds, charles, blueskies, etc.
    style = mpf.make_mpf_style(base_mpf_style='charles', rc={'font.family': 'SimHei'}) # SimHei 用于显示中文 (如果系统有)

    # 准备换手率的副图 (addplot)
    # panel=1 表示在主图下方的第一个副图绘制
    # type='bar' 绘制柱状图
    # secondary_y=False 使用独立的Y轴
    ap = [
        mpf.make_addplot(data['Turnover'], panel=1, color='orange', secondary_y=False, type='bar', ylabel='Turnover(%)'),
    ]

    # 标题
    title = f"Stock Analysis: {stock_code}"

    # 绘图
    # type='candle': K线图
    # mav=(5, 10, 20): 绘制 5, 10, 20 日均线
    # volume=False: 不使用默认的成交量图 (我们用换手率代替)
    # show_nontrading=False: 隐藏非交易日空隙
    # savefig: 如果提供路径，则保存图片
    save_args = {}
    if 'savefig' in kwargs:
        save_args['savefig'] = kwargs['savefig']

    mpf.plot(
        data,
        type='candle',
        mav=(5, 10, 20),
        addplot=ap,
        volume=False, 
        title=title,
        style=style,
        ylabel='Price',
        ylabel_lower='Turnover', # 这个参数可能只在 volume=True 时有效，但我们自定义了 addplot
        figratio=(12, 8),
        figscale=1.2,
        panel_ratios=(2, 1), # 主图和副图的高度比例
        show_nontrading=False,
        datetime_format='%Y-%m-%d',
        **save_args
    )
    if 'savefig' in kwargs:
        print(f"图表已保存至: {kwargs['savefig']}")
    else:
        print(f"图表绘制完成: {title}")

if __name__ == "__main__":
    # 测试代码 (需要先有数据，这里仅作语法检查)
    pass
