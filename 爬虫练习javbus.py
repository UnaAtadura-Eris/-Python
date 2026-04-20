import sys
import io
import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random

# ======================
# 基础配置
# ======================
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
requests.packages.urllib3.disable_warnings()

# ======================
# 网站配置（你给的结构）
# ======================
BASE_URL = "https://www.javbus.com"
PAGE_URL_FORMAT = "https://www.javbus.com/page/{}"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/130.0.0.0 Safari/537.36",
    "Referer": BASE_URL,
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Cookie": "existmag=all"
}

video_list = []
final_data = []
session = requests.Session()

# ======================
# 带重试的请求
# ======================
def get_with_retry(url, retries=2):
    for i in range(retries + 1):
        try:
            resp = session.get(url, headers=HEADERS, timeout=3, verify=False)
            resp.encoding = "utf-8"
            resp.raise_for_status()
            return resp
        except Exception as e:
            if i == retries:
                return None
            time.sleep(random.uniform(1, 2))
    return None

# ======================
# 爬列表（匹配你的结构：item masonry-brick）
# ======================
def crawl_list_page(page_num):
    url = PAGE_URL_FORMAT.format(page_num)
    print(f"\n📄 爬列表第 {page_num} 页：{url}")
    
    resp = get_with_retry(url)
    if not resp:
        print(f"❌ 列表页 {page_num} 请求失败")
        return False

    soup = BeautifulSoup(resp.text, "html.parser")
    cards = soup.select("div.item")

    if not cards:
        print("❌ 本页无视频")
        return False

    count = 0
    for card in cards:
        try:
            a_tag = card.select_one("a.movie-box")
            title = a_tag.img.get("title", "") if a_tag and a_tag.img else ""
            link = a_tag["href"] if a_tag else None

            if link:
                video_list.append({
                    "标题": title,
                    "链接": link
                })
                count += 1
        except:
            continue

    print(f"✅ 列表页 {page_num} 完成，抓取 {count} 个视频")
    time.sleep(random.uniform(1.5, 2.5))
    return True

# ======================
# 爬详情（匹配你给的 info 结构）
# ======================
def crawl_detail_info(video):
    title = video["标题"]
    link = video["链接"]
    print(f"\n🎬 爬详情：{title[:20]}")

    resp = get_with_retry(link)
    if not resp:
        return None

    s = BeautifulSoup(resp.text, "html.parser")
    info = s.select_one("div.col-md-3.info")

    if not info:
        return None

    try:
        # 所有 p 标签，方便提取
        p_list = info.find_all("p")

        code = ""
        publish_date = ""
        length = ""
        director = ""
        studio = ""
        label = ""
        series = ""

        for p in p_list:
            text = p.get_text(strip=True)

            # 識別碼
            if "識別碼:" in text:
                code_span = p.find("span", style="color:#CC0000;")
                code = code_span.get_text(strip=True) if code_span else ""

            # 發行日期
            elif "發行日期:" in text:
                publish_date = text.replace("發行日期:", "").strip()

            # 長度
            elif "長度:" in text:
                length = text.replace("長度:", "").strip()

            # 導演
            elif "導演:" in text:
                a_tag = p.find("a")
                director = a_tag.get_text(strip=True) if a_tag else ""

            # 製作商
            elif "製作商:" in text:
                a_tag = p.find("a")
                studio = a_tag.get_text(strip=True) if a_tag else ""

            # 發行商
            elif "發行商:" in text:
                a_tag = p.find("a")
                label = a_tag.get_text(strip=True) if a_tag else ""

            # 系列
            elif "系列:" in text:
                a_tag = p.find("a")
                series = a_tag.get_text(strip=True) if a_tag else ""

        # 类别
        genres = [a.get_text(strip=True) for a in info.select("span.genre a")]
        genres_str = "，".join(genres)

        # 演员
        actors = [a.get_text(strip=True) for a in info.select("div.star-box a")]
        actors_str = "，".join(actors)

        return {
            "标题": title,
            "链接": link,
            "識別碼": code,
            "發行日期": publish_date,
            "長度": length,
            "導演": director,
            "製作商": studio,
            "發行商": label,
            "系列": series,
            "演員": actors_str,
            "類別": genres_str
        }
    except Exception as e:
        print(f"解析失败：{e}")
        return None
# ======================
# 批量执行
# ======================
def run_crawler(start_page, end_page):
    print("="*50)
    print("🚀 开始爬取列表页...")
    print("="*50)
    
    for page in range(start_page, end_page+1):
        crawl_list_page(page)

    print(f"\n🎉 列表爬取完成！共获取 {len(video_list)} 个视频")

    print("\n" + "="*50)
    print("🎥 开始爬取详情页...")
    print("="*50)
    
    success = 0
    for video in video_list:
        data = crawl_detail_info(video)
        if data:
            final_data.append(data)
            success += 1
        time.sleep(random.uniform(1, 2))

    save_to_excel()
    print(f"\n🏁 全部完成！成功爬取 {success}/{len(video_list)} 个视频")

# ======================
# 保存Excel
# ======================
def save_to_excel():
    if not final_data:
        print("❌ 无数据可保存")
        return
    
    if not os.path.exists("output"):
        os.mkdir("output")
    
    df = pd.DataFrame(final_data)
    path = "output/javbus_data.xlsx"
    df.to_excel(path, index=False)
    print(f"\n📁 已保存到：{os.path.abspath(path)}")

# ======================
# 主程序
# ======================
if __name__ == "__main__":
    run_crawler(start_page=2, end_page=2)