import akshare as ak
import json
import pandas as pd

def generate_stock_names_json():
    print("正在获取所有A股实时行情以提取名称（这可能需要几秒钟）...")
    try:
        # 获取所有A股实时行情，包含代码和名称
        # 接口: stock_zh_a_spot_em
        df = ak.stock_zh_a_spot_em()
        
        if df.empty:
            print("获取失败：数据为空")
            return

        # 提取代码和名称
        # df 列名通常包含 "代码", "名称"
        stock_dict = {}
        for index, row in df.iterrows():
            code = str(row['代码'])
            name = str(row['名称'])
            stock_dict[code] = name
            
        # 保存为 JSON
        with open('stock_names.json', 'w', encoding='utf-8') as f:
            json.dump(stock_dict, f, ensure_ascii=False, indent=2)
            
        print(f"成功保存 {len(stock_dict)} 条股票名称到 stock_names.json")
        
    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":
    generate_stock_names_json()
