import sys
import io
import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random

# 基础配置
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
requests.packages.urllib3.disable_warnings()

BASE_URL = "https://jable.tv"
PAGE_URL_FORMAT = "https://jable.tv/tags/creampie/{}/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": BASE_URL,
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

video_list = []
final_data = []
session = requests.Session()

def get_with_retry(url, retries=1):
    for i in range(retries):
        try:
            resp = session.get(url, headers=HEADERS, timeout=3, verify=False)
            if resp.status_code == 200: return resp
            if resp.status_code == 403:
                print(f"⚠️ 触发403反爬，请检查网络或增加延时")
        except Exception:
            time.sleep(random.uniform(1, 2))
    return None

# 1. 第一阶段：扫列表
def crawl_list(page_num):
    url = PAGE_URL_FORMAT.format(page_num)
    print(f"\n📄 正在扫描列表页: {url}")
    
    resp = get_with_retry(url)
    if not resp: return False

    soup = BeautifulSoup(resp.text, "html.parser")
    # print("=== 抓到的内容前500字符 ===\n", resp.text[:500])
    items = soup.select(".video-img-box") # 每一个视频块

    if not items:
        print("❌ 未发现视频")
        return False

    count = 0
    for item in items:
        try:
            title_tag = item.select_one(".title a")
            title = title_tag.get_text(strip=True)
            link = title_tag['href']
            
            # --- 修正点：从 item (当前块) 提取 sub-title ---
            meta_area = item.select_one(".sub-title")
            # print("=== sub-title 内容 ===\n", meta_area)
            if meta_area:
                # separator=' ' 保证标签间有空格，方便 split
                meta_parts = meta_area.get_text(separator=' ', strip=True).split()
                print(meta_parts)
                # 逻辑：最后一位是收藏，其余合并为观看
                if len(meta_parts) >= 2:
                    favs = meta_parts[-1]
                    views = "".join(meta_parts[:-1])
                else:
                    views = meta_parts[0] if meta_parts else "0"
                    favs = meta_parts[1] if len(meta_parts) >= 1 else "0"
            else:
                views, favs = "0", "0"

            video_list.append({
                "标题": title,
                "链接": link,
                "观看数": views,
                "收藏数": favs
            })
            count += 1
            # print(video_list)
        except Exception as e:
            continue

    print(f"✅ 第 {page_num} 页抓取成功：{count} 条")
    return True

# 2. 第二阶段：抓详情
def crawl_detail(video):
    link = video["链接"]
    print(f"🎬 正在深入: {video['标题'][:15]}...")

    resp = get_with_retry(link)
    if not resp: return None

    soup = BeautifulSoup(resp.text, "html.parser")
    try:
        # 提取演员
        models_list = []
        model_tags = soup.select("div.models a.model")
        for tag in model_tags:
            # 兼容 img 或 span
            target = tag.find(["img", "span"])
            name = ""
            if target:
                name = target.get('data-original-title') or target.get('title') or target.get_text(strip=True)
            if name and name not in models_list:
                models_list.append(name)
        
        # 提取标签
        tags = [t.get_text(strip=True) for t in soup.select("h5.tags a")]

        return {
            "标题": video["标题"],
            "链接": link,
            "观看数": video["观看数"],
            "收藏数": video["收藏数"],
            "演员": " / ".join(models_list),
            "标签": " / ".join(tags)
        }
    except Exception as e:
        return None

def run(start, end):
    for p in range(start, end + 1):
        if not crawl_list(p): break
        time.sleep(random.uniform(1, 2))

    print(f"\n🚀 开始抓取详情（共 {len(video_list)} 条）...")
    for video in video_list:
        data = crawl_detail(video)
        if data:
            final_data.append(data)
        time.sleep(random.uniform(1.5, 3)) # 保护IP

    save_to_excel()

def save_to_excel():
    if not final_data: return
    if not os.path.exists("output"): os.mkdir("output")
    df = pd.DataFrame(final_data)
    df.to_excel("output/结果.xlsx", index=False)
    print(f"\n📊 导出成功！")

if __name__ == "__main__":
    # run(start=1, end=1)
    crawl_list(1)
