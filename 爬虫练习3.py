import sys
import io
import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# 解决中文乱码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 配置（你只改这里！）
def get_page_url(page_num):
    # 示例格式：return f"https://你的域名/actors?page={page_num}"
    # 你把上面换成你真实的分页网址格式
    return f"https://netflav.com/chinese-sub?page={page_num}"  # ← 改这里！

# 防反爬配置
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Referer": "https://netflav.com/",  # ← 填你网站首页
    "Connection": "keep-alive"
}

# 初始化会话（稳定请求）
requests.packages.urllib3.disable_warnings()  # 关闭SSL警告
session = requests.Session()

# 存储结果
all_videos = []

# 爬取单页
def crawl_single_page(page_num):
    url = get_page_url(page_num)
    print(f"\n===== 正在爬第 {page_num} 页：{url} =====")

    try:
        # 发送请求（跳过SSL验证，解决请求失败）
        response = session.get(
            url,
            headers=headers,
            timeout=10,
            verify=False,
            allow_redirects=True
        )
        response.raise_for_status()  # 检测请求是否成功

    except Exception as e:
        print(f"❌ 第{page_num}页请求失败：{str(e)[:60]}")
        return False

    # 解析HTML（精准匹配你给的结构）
    soup = BeautifulSoup(response.text, "html.parser")
   
    video_cards = soup.select("div.grid_0_cell")

    if not video_cards:
        print("❌ 本页未找到视频卡片")
        return False

    # 提取每个视频的信息
    for card in video_cards:
        try:
            # 视频名字（匹配 class="grid_0_title" 的第一个元素）
            name = card.select_one(".grid_0_title").get_text(strip=True)
            # 【新增】提取视频链接（取第一个a标签，避免重复）
            a_tag = card.select_one("a[href^='/video?id=']")
            if a_tag:
                video_href = a_tag.get("href", "")
                # 拼接完整URL（替换成你的域名）
                full_url = f"https://netflav.com{video_href}"
            else:
                full_url = "无链接"
            
            # ======================
            # 2. 自动进入视频详情页
            # ======================
            print(f"  → 进入详情页：{full_url}")

            resp_detail = session.get(
                full_url,
                headers=headers,
                timeout=15,
                verify=False
            )
            s = BeautifulSoup(resp_detail.text, "html.parser")

            # ----------------------
            # 第三步：爬你想要的内容（举例，你可以自己加）
            # ----------------------
             # 标题
            title = s.select_one(".videodetail_2_title")
            title = title.get_text(strip=True) if title else name

            # 观看数
            views = s.select_one(".videodetail_2_views")
            views = views.get_text(strip=True).replace("觀看數 ：", "") if views else ""

            # 番号
            code = s.select_one("div:-soup-contains('番號 :') + .videodetail_2_field_values")
            code = code.get_text(strip=True) if code else ""

            # 发行日期
            publish_date = s.select_one("div:-soup-contains('發行日期 :') + .videodetail_2_field_values")
            publish_date = publish_date.get_text(strip=True) if publish_date else ""

            # 女优（多个女优自动拼接）
            actress_tags = s.select("a.videodetail_2_field_values_clickable[href*='actress=']")
            actresses = [a.get_text(strip=True) for a in actress_tags]
            actresses_str = "，".join(actresses)

            # 类别（标签）
            genre_tags = s.select("a.videodetail_2_field_values_clickable[href*='genre=']")
            genres = [g.get_text(strip=True) for g in genre_tags]
            genres_str = "，".join(genres)


            all_videos.append({
                "视频名字": name,
                "视频链接": full_url,
                "观看数": views,
                "番号": code,
                "发行日期": publish_date,
                "女优": actresses_str,
                "类别标签": genres_str
            })
            print(f"✅ {name} ")

        except Exception as e:
            print(f"⚠️  解析单张卡片失败：{str(e)}")
            continue

    print(f"✅ 第{page_num}页完成，共抓取 {len(video_cards)} 个视频")
    return True

# 批量爬多页
def crawl_all_pages(start_page=1, end_page=10):
    for page in range(start_page, end_page + 1):
        crawl_single_page(page)
        time.sleep(1)  

# 保存到Excel（自动创建文件夹）
def save_to_excel():
    if not all_videos:
        print("❌ 没有可保存的数据")
        return

    # 自动创建output文件夹
    if not os.path.exists("output"):
        os.mkdir("output")

    # 保存Excel
    df = pd.DataFrame(all_videos)
    excel_path = "output/netflav_videos.xlsx"
    df.to_excel(excel_path, index=False)
    print(f"\n🎉 全部完成！共抓取 {len(all_videos)} 个视频数据")
    print(f"📁 数据已保存到：{os.path.abspath(excel_path)}")

# 主程序入口
if __name__ == "__main__":
    # 你可以改这里的起始页和结束页
    crawl_all_pages(start_page=1, end_page=10)  # 比如爬1-5页
    save_to_excel()