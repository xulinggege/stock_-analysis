import akshare as ak
import json
import time
from pypinyin import lazy_pinyin
import os

STOCK_INFO_FILE = 'stock_info_full.json'

def get_pinyin_initials(name):
    """
    获取中文名称的拼音首字母
    例如: "贵州茅台" -> "gzmt"
    """
    try:
        # lazy_pinyin 返回 list，如 ['gui', 'zhou', 'mao', 'tai']
        pinyin_list = lazy_pinyin(name)
        # 取每个拼音的首字母并连接
        initials = ''.join([p[0] for p in pinyin_list if p])
        return initials.lower()
    except:
        return ""

def fetch_and_save_stocks():
    print("正在尝试获取全量A股数据...")
    
    df = None
    # 尝试多次，防止网络波动
    for i in range(3):
        try:
            # 接口: stock_info_a_code_name (沪深京A股代码和名称)
            # 相比 stock_zh_a_spot_em (实时行情)，这个接口数据量小，更稳定
            df = ak.stock_info_a_code_name()
            if not df.empty:
                print(f"成功获取 {len(df)} 条数据。")
                break
        except Exception as e:
            print(f"第 {i+1} 次尝试失败: {e}")
            time.sleep(2)
            
    if df is None or df.empty:
        print("无法获取数据，生成仅包含常用股的列表...")
        # 如果失败，使用一个内置的常用股票列表作为保底
        base_stocks = [
            ("600519", "贵州茅台"), ("000001", "平安银行"), ("000002", "万科A"),
            ("600036", "招商银行"), ("601318", "中国平安"), ("300750", "宁德时代"),
            ("000858", "五粮液"), ("002594", "比亚迪"), ("601012", "隆基绿能"),
            ("300059", "东方财富"), ("600276", "恒瑞医药"), ("300760", "迈瑞医疗"),
            ("601888", "中国中免"), ("603288", "海天味业"), ("601988", "中国银行"),
            ("601398", "工商银行"), ("601939", "建设银行"), ("601288", "农业银行")
        ]
        stock_list = []
        for code, name in base_stocks:
            stock_list.append({
                "code": code,
                "name": name,
                "pinyin": get_pinyin_initials(name)
            })
    else:
        # 处理全量数据
        print("正在生成拼音索引...")
        stock_list = []
        # df 列: code, name
        for index, row in df.iterrows():
            code = str(row['code'])
            name = str(row['name'])
            # 过滤非A股代码（简单过滤）
            if not (code.startswith('60') or code.startswith('00') or code.startswith('30') or code.startswith('68')):
                continue
                
            pinyin = get_pinyin_initials(name)
            stock_list.append({
                "code": code,
                "name": name,
                "pinyin": pinyin
            })
            
    # 保存文件
    with open(STOCK_INFO_FILE, 'w', encoding='utf-8') as f:
        json.dump(stock_list, f, ensure_ascii=False, indent=None) # indent=None 减小体积
        
    print(f"已保存 {len(stock_list)} 条股票信息到 {STOCK_INFO_FILE}")

if __name__ == "__main__":
    fetch_and_save_stocks()
