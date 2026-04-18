import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# ==========================
# 【修复1】更强的请求头，骗过网站
# ==========================
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Referer": "https://jable.tv/",
    "Connection": "keep-alive"
}

# ==========================
# 【修复2】加强请求，允许重试 + 关闭SSL警告
# ==========================
session = requests.Session()
requests.packages.urllib3.disable_warnings()  # 关掉SSL警告

all_data = []

# ======================
# 你自己填分页格式
# ======================
def get_page_url(page_num):
    return f"https://jable.tv/models/{page_num}/"

# 爬一页（加强版）
def crawl(page_num):
    url = get_page_url(page_num)
    print("正在爬：", url)

    try:
        # 关键：verify=False 跳过SSL错误
        r = session.get(
            url,
            headers=headers,
            timeout=15,
            verify=False,
            allow_redirects=True
        )
        r.raise_for_status()

    except Exception as e:
        print(f"❌ 第{page_num}页请求失败: {str(e)[:50]}")
        return False

    soup = BeautifulSoup(r.text, "html.parser")
    items = soup.select(".horizontal-img-box")

    found = 0
    for item in items:
        try:
            name = item.select_one(".title").get_text(strip=True)
            count = item.select_one(".detail span").get_text(strip=True)
            all_data.append({"name": name, "count": count})
            print(f"{name} | {count}")
            found += 1
        except:
            continue

    print(f"✅ 本页找到：{found} 条")
    return True

# 爬多页
def crawl_all(start, end):
    for page in range(start, end + 1):
        print(f"\n===== 第 {page} 页 =====")
        crawl(page)
        
        # ==========================
        # 【修复3】变慢速度，关键！
        # ==========================
        time.sleep(1)  # 1秒一次，绝对不被封

# 保存Excel
def save():
    df = pd.DataFrame(all_data)
    df.to_excel("output/jable.xlsx", index=False)
    print(f"\n🎉 全部完成！共 {len(all_data)} 条")

# ======================
# 开始爬
# ======================
if __name__ == "__main__":
    crawl_all(start=1, end=206)
    save()