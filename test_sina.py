import requests

def get_name_sina(code):
    """
    通过新浪财经接口获取股票名称
    """
    try:
        # 补全前缀
        if code.startswith('6'):
            full_code = f"sh{code}"
        else:
            full_code = f"sz{code}"
            
        url = f"http://hq.sinajs.cn/list={full_code}"
        headers = {'Referer': 'http://finance.sina.com.cn'}
        
        resp = requests.get(url, headers=headers, timeout=5)
        if resp.status_code == 200:
            # 响应格式: var hq_str_sh600519="贵州茅台,..."
            text = resp.text
            if '="' in text:
                content = text.split('="')[1]
                name = content.split(',')[0]
                return name
    except Exception as e:
        print(f"Sina API error: {e}")
    return None

if __name__ == "__main__":
    code = "600519"
    print(f"Testing Sina API for {code}...")
    name = get_name_sina(code)
    print(f"Result: {name}")
