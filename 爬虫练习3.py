import sys
import io
import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random

# ======================
# 基础配置（解决乱码/代理）
# ======================
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
requests.packages.urllib3.disable_warnings()

# ======================
# 网站配置（你的目标站）
# ======================
BASE_URL = "https://netflav.com"
PAGE_URL_FORMAT = "https://netflav.com/chinese-sub?page={}"

# 请求头（极简防反爬）
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/130.0.0.0 Safari/537.36",
    "Referer": BASE_URL,
}

# 全局存储
video_list = []  # 先存列表数据
final_data = []  # 最终完整数据
session = requests.Session()

# ======================
# 【优化1】请求重试函数（解决详情页打不开）
# ======================
def get_with_retry(url, retries=2):
    for i in range(retries + 1):
        try:
            resp = session.get(url, headers=HEADERS, timeout=15, verify=False)
            resp.encoding = "utf-8"
            resp.raise_for_status()
            return resp
        except Exception as e:
            if i == retries:
                return None
            # 失败后等待，再重试
            time.sleep(random.uniform(2, 4))
    return None

# ======================
# 【优化2】第一步：只爬列表（超快、不触发反爬）
# ======================
def crawl_list_page(page_num):
    url = PAGE_URL_FORMAT.format(page_num)
    print(f"\n📄 爬列表第 {page_num} 页：{url}")
    
    resp = get_with_retry(url)
    if not resp:
        print(f"❌ 列表页 {page_num} 请求失败")
        return False

    soup = BeautifulSoup(resp.text, "html.parser")
    cards = soup.select("div.grid_0_cell")

    if not cards:
        print("❌ 本页无视频")
        return False

    count = 0
    for card in cards:
        try:
            # 提取标题+链接
            title = card.select_one(".grid_0_title").get_text(strip=True) if card.select_one(".grid_0_title") else "无标题"
            a_tag = card.select_one("a[href^='/video?id=']")
            link = BASE_URL + a_tag["href"] if a_tag else None

            if link:
                video_list.append({"标题": title, "链接": link})
                count += 1
        except:
            continue

    print(f"✅ 列表页 {page_num} 完成，抓取 {count} 个视频")
    # 防封延时（随机1.5~3秒，比固定1秒更安全）
    time.sleep(random.uniform(1.5, 3))
    return True

# ======================
# 【优化3】第二步：批量爬详情（自动重试+不重复爬）
# ======================
def crawl_detail_info(video):
    title = video["标题"]
    link = video["链接"]
    print(f"\n🎬 爬详情：{title}")

    resp = get_with_retry(link)
    if not resp:
        print(f"❌ 详情页打开失败，跳过")
        return None

    s = BeautifulSoup(resp.text, "html.parser")
    try:
        # 提取所有字段（兼容无数据情况）
        detail_title = s.select_one(".videodetail_2_title").get_text(strip=True) if s.select_one(".videodetail_2_title") else title
        views = s.select_one(".videodetail_2_views").get_text(strip=True).replace("觀看數 ：", "") if s.select_one(".videodetail_2_views") else ""
        code = s.select_one("div:-soup-contains('番號 :') + .videodetail_2_field_values").get_text(strip=True) if s.select_one("div:-soup-contains('番號 :') + .videodetail_2_field_values") else ""
        publish_date = s.select_one("div:-soup-contains('發行日期 :') + .videodetail_2_field_values").get_text(strip=True) if s.select_one("div:-soup-contains('發行日期 :') + .videodetail_2_field_values") else ""
        
        # 女优+标签
        actresses = [a.get_text(strip=True) for a in s.select("a.videodetail_2_field_values_clickable[href*='actress=']")]
        genres = [g.get_text(strip=True) for g in s.select("a.videodetail_2_field_values_clickable[href*='genre=']")]

        return {
            "标题": detail_title,
            "链接": link,
            "观看数": views,
            "番号": code,
            "发行日期": publish_date,
            "女优": "，".join(actresses),
            "类别": "，".join(genres)
        }
    except:
        return None

# ======================
# 【优化4】批量执行+自动保存
# ======================
def run_crawler(start_page, end_page):
    # 第一步：爬所有列表
    print("="*50)
    print("🚀 开始爬取列表页...")
    print("="*50)
    for page in range(start_page, end_page+1):
        crawl_list_page(page)

    print(f"\n🎉 列表爬取完成！共获取 {len(video_list)} 个视频")
    
    # 第二步：爬详情
    print("\n" + "="*50)
    print("🎥 开始爬取详情页（慢稳防封）...")
    print("="*50)
    
    success = 0
    for video in video_list:
        data = crawl_detail_info(video)
        if data:
            final_data.append(data)
            success += 1
        # 【关键】详情页加长延时，彻底解决打不开问题
        time.sleep(random.uniform(1, 2))

    # 保存结果
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
    path = "output/netflav_完整数据.xlsx"
    df.to_excel(path, index=False)
    print(f"\n📁 已保存到：{os.path.abspath(path)}")

# ======================
# 主程序
# ======================
if __name__ == "__main__":
    # 配置爬取页数（建议一次别爬10页，先爬3页测试）
    run_crawler(start_page=1, end_page=3)