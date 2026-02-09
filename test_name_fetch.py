import yfinance as yf
import akshare as ak

code = "600519"
print(f"Testing fetching name for {code}")

# Test yfinance
try:
    print("\n--- yfinance ---")
    suffix = ".SS" if code.startswith("6") else ".SZ"
    ticker = yf.Ticker(code + suffix)
    # 强制获取 info
    info = ticker.info
    print(f"shortName: {info.get('shortName')}")
    print(f"longName: {info.get('longName')}")
except Exception as e:
    print(f"yfinance error: {e}")

# Test AkShare
try:
    print("\n--- AkShare ---")
    df = ak.stock_individual_info_em(symbol=code)
    print(df)
except Exception as e:
    print(f"AkShare error: {e}")
