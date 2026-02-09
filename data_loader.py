import akshare as ak
import pandas as pd
import yfinance as yf
from datetime import datetime
import json
import os
import requests

# 静态股票名称映射文件
STOCK_NAMES_FILE = 'stock_names.json'

def get_stock_data(stock_code: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    获取A股股票历史数据，优先使用 AkShare，失败则尝试 yfinance
    """
    # 尝试 AkShare
    try:
        print(f"正在尝试通过 AkShare 获取股票 {stock_code} 的数据...")
        df = ak.stock_zh_a_hist(symbol=stock_code, period="daily", start_date=start_date, end_date=end_date, adjust="qfq")
        
        if not df.empty:
            rename_map = {
                "日期": "Date", "开盘": "Open", "收盘": "Close", 
                "最高": "High", "最低": "Low", "成交量": "Volume", 
                "换手率": "Turnover"
            }
            df.rename(columns=rename_map, inplace=True)
            df['Date'] = pd.to_datetime(df['Date'])
            df.set_index('Date', inplace=True)
            
            numeric_cols = ['Open', 'Close', 'High', 'Low', 'Volume', 'Turnover']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            print(f"AkShare: 成功获取 {len(df)} 条数据。")
            return df
    except Exception as e:
        print(f"AkShare 获取失败: {e}")

    # 尝试 yfinance
    try:
        print(f"正在尝试通过 yfinance 获取股票 {stock_code} 的数据...")
        # 转换代码格式
        suffix = ".SS" if stock_code.startswith("6") else ".SZ"
        yf_code = stock_code + suffix
        
        # 转换日期格式 YYYYMMDD -> YYYY-MM-DD
        start_fmt = f"{start_date[:4]}-{start_date[4:6]}-{start_date[6:]}"
        end_fmt = f"{end_date[:4]}-{end_date[4:6]}-{end_date[6:]}"
        
        ticker = yf.Ticker(yf_code)
        df = ticker.history(start=start_fmt, end=end_fmt)
        
        if df.empty:
            print("yfinance 也未获取到数据。")
            return pd.DataFrame()
            
        # yfinance 返回的数据包含: Open, High, Low, Close, Volume, Dividends, Stock Splits
        # 需要计算 Turnover (换手率) = Volume / Float Shares * 100
        # 尝试获取流通股本
        try:
            shares = ticker.info.get('floatShares')
            if not shares:
                shares = ticker.info.get('sharesOutstanding')
        except:
            shares = None
            
        if shares:
            df['Turnover'] = (df['Volume'] / shares) * 100
        else:
            print("无法获取流通股本信息，将使用成交量代替换手率展示，或者换手率设为0。")
            df['Turnover'] = 0 # 或者不设置，但在 plotter 里需要处理
            
        # yfinance 的索引已经是 Date (datetime64)
        # 确保列名一致
        df = df[['Open', 'High', 'Low', 'Close', 'Volume', 'Turnover']]
        
        print(f"yfinance: 成功获取 {len(df)} 条数据。")
        return df
        
    except Exception as e:
        print(f"yfinance 获取失败: {e}")
        return pd.DataFrame()

def get_stock_name(stock_code: str) -> str:
    """
    获取股票名称，优先级:
    1. 本地静态映射 (stock_names.json)
    2. AkShare
    3. yfinance
    """
    # 1. 尝试从本地静态文件读取
    try:
        if os.path.exists(STOCK_NAMES_FILE):
            with open(STOCK_NAMES_FILE, 'r', encoding='utf-8') as f:
                stock_dict = json.load(f)
                if stock_code in stock_dict:
                    return stock_dict[stock_code]
    except Exception:
        pass

    # 2. 尝试 AkShare
    try:
        # stock_individual_info_em 获取个股信息
        df = ak.stock_individual_info_em(symbol=stock_code)
        # df 结构为 item (项目) 和 value (值)
        name_row = df[df['item'] == '股票简称']
        if not name_row.empty:
            return name_row.iloc[0]['value']
    except Exception:
        pass # 静默失败，尝试下一方法

    # 3. 尝试新浪财经接口 (Sina Finance)
    # 这是一个非常稳定且轻量级的 HTTP 接口，适合作为 AkShare 的备选
    try:
        if stock_code.startswith('6'):
            full_code = f"sh{stock_code}"
        else:
            full_code = f"sz{stock_code}"
            
        url = f"http://hq.sinajs.cn/list={full_code}"
        headers = {'Referer': 'http://finance.sina.com.cn'}
        
        resp = requests.get(url, headers=headers, timeout=3)
        if resp.status_code == 200:
            text = resp.text
            # 格式: var hq_str_sh600519="贵州茅台,..."
            if '="' in text:
                content = text.split('="')[1]
                if content:
                    name = content.split(',')[0]
                    if name:
                        return name
    except Exception:
        pass

    # 4. 尝试 yfinance
    try:
        suffix = ".SS" if stock_code.startswith("6") else ".SZ"
        ticker = yf.Ticker(stock_code + suffix)
        info = ticker.info
        name = info.get('shortName') or info.get('longName')
        if name:
            return name
    except:
        pass
        
    # 如果都失败，返回代码本身
    return stock_code

if __name__ == "__main__":
    # 测试代码
    test_code = "600519"
    test_start = "20230101"
    test_end = "20231231"
    data = get_stock_data(test_code, test_start, test_end)
    print(data.head())
