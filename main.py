import data_loader
import plotter
from datetime import datetime, timedelta

def main():
    print("=== A股股票换手率与股价走势分析工具 ===")
    
    # 获取当前日期和半年前的日期作为默认范围
    today = datetime.now().strftime('%Y%m%d')
    six_months_ago = (datetime.now() - timedelta(days=180)).strftime('%Y%m%d')
    
    # 用户输入
    stock_code = input("请输入股票代码 (例如 600519): ").strip()
    if not stock_code:
        stock_code = "600519" # 默认贵州茅台
        print(f"使用默认股票代码: {stock_code}")
        
    start_date = input(f"请输入开始日期 (YYYYMMDD, 默认 {six_months_ago}): ").strip()
    if not start_date:
        start_date = six_months_ago
        
    end_date = input(f"请输入结束日期 (YYYYMMDD, 默认 {today}): ").strip()
    if not end_date:
        end_date = today
        
    # 获取数据
    df = data_loader.get_stock_data(stock_code, start_date, end_date)
    
    if not df.empty:
        # 绘图并保存
        filename = f"{stock_code}_analysis.png"
        # 这里默认保存图片，方便查看结果
        plotter.plot_stock_analysis(df, stock_code, savefig=filename)
        print(f"\n分析完成！图表已保存为 {filename}")
        print("您也可以在支持图形界面的环境中运行此脚本以直接查看交互式窗口。")
    else:
        print("未获取到数据，流程终止。")

if __name__ == "__main__":
    main()
