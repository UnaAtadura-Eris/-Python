# 强制编码（解决终端乱码）
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
"""**********************************************************************************************************"""
#确认你的 driver 是否成功接管并能控制网页：

# 运行后观察 Chrome 页面上方是否出现弹窗
#driver.execute_script("alert('Selenium 连接成功！正在由 Python 接管控制权。');")
# 打印当前窗口标题
#print(f"当前受控网页标题是: {driver.title}", flush=True)
"""**********************************************************************************************************"""
# 打开新浏览器
from selenium import webdriver
if __name__ == "__main__":
    # 确保chromedriver在PATH中，或者在同一目录下
    driver = webdriver.Chrome()
    driver.get("https://www.baidu.com")
    print(driver.title)
    driver.quit()


"""**********************************************************************************************************"""
#调试模式
#打开cmd输入： "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="D:\selenium_user_data" 
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# 创建一个"点餐单"
chrome_options = Options()
# 添加一些"要求"
chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
# 把"点餐单"给服务员（浏览器）
driver = webdriver.Chrome(options=chrome_options)

if __name__ == "__main__":
    # 确保chromedriver在PATH中，或者在同一目录下
    driver.get("https://www.baidu.com")
    print(driver.title)
    driver.quit()
"""**********************************************************************************************************"""

#调试模式  自动下一页抓取标题、链接。
#打开cmd输入： "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="D:\selenium_user_data" 
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# 配置接管参数
chrome_options = Options()
chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
# 此时 driver 指向的就是你已经登录好的那个窗口
driver = webdriver.Chrome(options=chrome_options)
def scrape_to_excel(url,page_num=5): 
    """第一个参数：网址；第二个参数：要采集的页数"""           
    try:
        print(f"🌐 正在访问: {url}")
        driver.get(url)
        time.sleep(5)  # 等待页面加载，特别是 Cloudflare 验证       
        video_data = []
        seen_urls = set() # 用于去重
        for page in range(0,page_num):
                # 2. 模拟滚动加载（确保加载出动态内容）
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            # 3. 定位标题元素并提取数据
            # 针对 <div class="grid_0_title"> 优化的选择器
            titles = driver.find_elements(By.CSS_SELECTOR, "div[class*='grid_0_title']")       
            print(f"检测到 {len(titles)} 个潜在标题，开始提取...")        
            for item in titles:
                title_text = item.text.strip()
                try:
                    # 核心逻辑：通常 div 里的标题是通过父级 a 标签跳转的
                    # 我们寻找它最近的父级 <a> 标签来获取链接
                    link_element = item.find_element(By.XPATH, "./ancestor::a")
                    video_url = link_element.get_attribute("href")
                    
                    if title_text and video_url not in seen_urls:
                        video_data.append({
                            "视频标题": title_text,
                            "视频链接": video_url
                        })
                        seen_urls.add(video_url)
                        print(f"已捕获: {title_text[:20]}...")
                except:
                    # 如果没找到链接，只存标题
                    if title_text:
                        video_data.append({"视频标题": title_text, "视频链接": "未找到链接"})              
            if turn_to_next_page():
                print(f"正在采集第 {page+2} 页的数据...")
            else:
                print(f"没有点击到第 {page+2} 页...")        
                

        # 4. 使用 Pandas 保存为 Excel
        if video_data:
            df = pd.DataFrame(video_data)
            filename = f"video_list_{int(time.time())}.xlsx"
            # 保存到当前文件夹
            df.to_excel(filename, index=False)
            import os
            print(f"\n✅ 数据已成功导出到 Excel！")
            print(f"📂 文件路径: {os.path.abspath(filename)}")
        else:
            print("❌ 未抓取到有效数据。")

    finally:
        # 5. 确保关闭浏览器资源
        print("结束采集数据...")
        driver.quit()

# 专门处理这种图标按钮的翻页
def turn_to_next_page():
    try:
        # 寻找下一页图标
        btn = driver.find_element(By.CSS_SELECTOR, "a[type='nextItem']")
        if btn:
            print("找到下一页按钮")
        # 检查是否到了最后一页 (aria-disabled 会变成 "true")
        if btn.get_attribute("aria-disabled") == "true":
            print("已经到最后一页了")
            return False
            
        # 滚动到按钮位置，防止被遮挡
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
        time.sleep(1)
        
        # 执行点击
        driver.execute_script("arguments[0].click();", btn)
        return True
    except:
        return False
    

if __name__ == "__main__":
    scrape_to_excel("https://netflav.com/all?genre=%E6%83%85%E4%BE%B6",3)
    #turn_to_next_page()


    




"""**********************************************************************************************************"""
#爬网页,标题文本、链接地址
"""
a[href*='/videos/']
“选择所有 <a>（链接）标签，且其 href 属性中包含 /videos/ 这个字符串的片段。”
这里的关键是 *= 操作符，它表示“包含”。

--------------------------------------------------------jable.tv--------------------------------------------------------

# 通过h6的class定位到h6，再找到里面的a标签，然后获取文本
title = driver.find_element(By.CSS_SELECTOR, "h6.title a").text

# 如果你有多个这样的h6，需要批量获取：
titles = driver.find_elements(By.CSS_SELECTOR, "h6.title a")
for title_element in titles:
    print(title_element.text)

 # 批量获取页面上所有此类标题文本、链接地址
titles = driver.find_elements(By.CSS_SELECTOR, "h6.title a")

for item in titles:
    # 获取标题文本
    title_text = item.text
    # 获取链接地址（如果需要）
    link_url = item.get_attribute("href")
    print(f"标题: {title_text}, 链接: {link_url}")  




--------------------------------------------------------netflav--------------------------------------------------------

先找到外层的 grid_0_cell 容器（通常一个容器包含一个完整视频项）
    video_cells = driver.find_elements(By.CLASS_NAME, "grid_0_cell")

    for cell in video_cells:
        # 在单个容器内查找标题和链接
        title_text = cell.find_element(By.CLASS_NAME, "grid_0_title").text
        
        # 获取链接（两个a标签的href相同，取其中一个即可）
        video_link = cell.find_element(By.TAG_NAME, "a").get_attribute("href")
        # 如果需要完整的绝对URL，可以拼接
        # video_link = "https://网站域名" + cell.find_element(By.TAG_NAME, "a").get_attribute("href")
        
        print(f"标题: {title_text}, 链接: {video_link}")   



from selenium.webdriver.common.by import By
# 方法1：直接通过标题div的类名定位（最直接、推荐）
title_element = driver.find_element(By.CLASS_NAME, "grid_0_title")
title_text = title_element.text  # 获取文本

# 方法2：通过CSS选择器定位（精确）
title_element = driver.find_element(By.CSS_SELECTOR, "div.grid_0_title")
# 或者更具体一点（通过父级a标签限定）
title_element = driver.find_element(By.CSS_SELECTOR, "a > div.grid_0_title")

# 方法3：通过XPath定位（灵活性高）
title_element = driver.find_element(By.XPATH, "//div[@class='grid_0_title']")
# 或者从外层div开始
title_element = driver.find_element(By.XPATH, "//div[@class='grid_0_cell']//div[@class='grid_0_title']")
"""

# 点击
"""
这个 <h2> 标签比较特殊，它没有使用标准的 <a> 链接，而是通过 onclick 事件（JavaScript）来实现页面跳转。
  #使用 CSS 选择器，通过类名定位
    h2_btn = driver.find_element(By.CSS_SELECTOR, "h2.another-text")
    h2_btn.click()
    print("成功点击 h2 标题")

    # 定位元素
    h2_element = driver.find_element(By.CSS_SELECTOR, "h2.another-text")
    # 强制触发点击事件
    driver.execute_script("arguments[0].click();", h2_element)


点击第N个标题
    h2_btn = driver.find_elements(By.CSS_SELECTOR, "h2")
    h2_btn[3].click()
    print("成功点击 h2 第4个标题")
"""




"""**********************************************************************************************************"""
#爬网页 下一页
import time
import os
import re
import random
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
import logging
from urllib.parse import urljoin, urlparse
import sys
import io
# 设置编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('video_crawler.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
class VideoCrawler:
    def __init__(self, headless=False, chrome_driver_path=None):
        """初始化浏览器驱动"""
        self.chrome_options = Options()
        
        # 添加常用配置
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        self.chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # 设置用户代理
        self.chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        if headless:
            self.chrome_options.add_argument('--headless')
            self.chrome_options.add_argument('--window-size=1920,1080')
        
        # 初始化驱动
        try:
            if chrome_driver_path:
                service = Service(executable_path=chrome_driver_path)
                self.driver = webdriver.Chrome(service=service, options=self.chrome_options)
            else:
                self.driver = webdriver.Chrome(options=self.chrome_options)
            
            # 注入JavaScript以绕过检测
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            logger.info("Chrome浏览器初始化成功")
        except Exception as e:
            logger.error(f"浏览器初始化失败: {e}")
            raise
    
    def extract_video_data(self, page_url, max_pages=1, scroll_pause_time=2):
        """从网页提取视频数据，支持多页和滚动加载"""
        all_results = []
        current_page = 1
        
        try:
            while current_page <= max_pages:
                logger.info(f"正在处理第 {current_page} 页: {page_url}")
                
                # 访问页面
                self.driver.get(page_url)
                
                # 等待页面加载
                time.sleep(3)
                
                # 滚动页面以加载所有内容（针对懒加载）
                self.scroll_page(scroll_pause_time)
                
                # 提取当前页数据
                page_results = self._extract_current_page()
                
                if page_results:
                    all_results.extend(page_results)
                    logger.info(f"第 {current_page} 页提取到 {len(page_results)} 个视频")
                else:
                    logger.warning(f"第 {current_page} 页未找到视频数据")
                
                # 尝试查找下一页
                if current_page < max_pages:
                    next_page_url = self._find_next_page()
                    if next_page_url:
                        # 确保下一页URL是完整的
                        if next_page_url.startswith('/'):
                            from urllib.parse import urlparse
                            parsed_url = urlparse(page_url)
                            next_page_url = f"{parsed_url.scheme}://{parsed_url.netloc}{next_page_url}"
                        page_url = next_page_url
                        current_page += 1
                    else:
                        logger.info("没有更多页面")
                        break
                else:
                    break
                
                # 添加随机延迟，避免被封
                time.sleep(2 + random.random() * 2)
        
        except Exception as e:
            logger.error(f"提取数据时出错: {e}")
        
        return all_results
    
    def scroll_page(self, pause_time=2):
        """滚动页面以加载所有内容"""
        try:
            # 获取页面高度
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            
            while True:
                # 滚动到底部
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(pause_time)
                
                # 计算新的滚动高度
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                
                # 如果高度没有变化，结束滚动
                if new_height == last_height:
                    break
                
                last_height = new_height
        
        except Exception as e:
            logger.warning(f"滚动页面时出错: {e}")
    
    def _extract_current_page(self):
        """提取当前页面的视频数据"""
        results = []
        seen_urls = set()
        
        try:
            # 等待视频元素加载
            wait = WebDriverWait(self.driver, 10)
            
            # 尝试多种选择器定位视频元素
            selectors = [
                "a[href*='/videos/']:not([class*='time']):not([class*='duration'])",
                ".video-item a[href*='/videos/']",
                ".item a[href*='/videos/']",
                ".post a[href*='/videos/']",
                ".thumbnail a[href*='/videos/']",
                "a.video-link[href*='/videos/']"
            ]
            
            video_elements = []
            for selector in selectors:
                try:
                    elements = wait.until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector))
                    )
                    if elements:
                        video_elements = elements
                        logger.info(f"使用选择器 '{selector}' 找到 {len(elements)} 个元素")
                        break
                except TimeoutException:
                    continue
            
            if not video_elements:
                logger.warning("未找到视频元素，尝试备用选择器")
                # 备用选择器
                video_elements = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/videos/']")
            
            # 提取每个元素的数据
            for el in video_elements:
                try:
                    # 获取视频URL
                    video_url = el.get_attribute("href")
                    if not video_url or video_url in seen_urls:
                        continue
                    
                    # 获取标题 - 多种方式尝试
                    title = None
                    
                    # 1. 从title属性获取
                    title = el.get_attribute("title")
                    
                    # 2. 从文本获取
                    if not title or len(title.strip()) < 2:
                        title_text = el.text.strip()
                        # 过滤掉时间格式的文本
                        if title_text and not self._is_time_format(title_text):
                            title = title_text
                    
                    # 3. 从相邻元素获取
                    if not title or len(title.strip()) < 2:
                        title = self._get_title_from_siblings(el)
                    
                    # 清理标题
                    if title:
                        title = self._clean_title(title)
                    
                    # 获取缩略图（如果存在）
                    thumbnail = self._get_thumbnail_url(el)
                    
                    # 获取时长（如果存在）
                    duration = self._get_duration(el)
                    
                    # 获取其他信息（演员、观看数等）
                    extra_info = self._get_extra_info(el)
                    
                    # 添加到结果
                    if title and video_url:
                        results.append({
                            "标题": title,
                            "网址": video_url,
                            "时长": duration,
                            "缩略图": thumbnail,
                            "演员": extra_info.get("actor", ""),
                            "观看数": extra_info.get("views", ""),
                            "发布时间": extra_info.get("date", ""),
                            "采集时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        })
                        seen_urls.add(video_url)
                        
                        logger.debug(f"提取到: {title[:50]}...")
                
                except Exception as e:
                    logger.warning(f"提取单个元素时出错: {e}")
                    continue
            
            logger.info(f"成功提取 {len(results)} 个视频")
        
        except Exception as e:
            logger.error(f"提取页面数据时出错: {e}")
        
        return results
    
    def _is_time_format(self, text):
        """检查文本是否为时间格式"""
        time_patterns = [
            r'^\d{1,2}:\d{2}$',
            r'^\d{1,2}:\d{2}:\d{2}$',
            r'^\d+h\d+m$',
            r'^\d+分钟$',
            r'^\d+ min$',
            r'^[\d:]+$'  # 纯数字和冒号
        ]
        
        text = text.strip()
        for pattern in time_patterns:
            if re.match(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def _clean_title(self, title):
        """清理标题文本"""
        # 移除多余空格
        title = re.sub(r'\s+', ' ', title).strip()
        
        # 移除常见的时间前缀/后缀
        time_patterns = [
            r'^\d{1,2}:\d{2}\s*[-–—]\s*',
            r'\s*[-–—]\s*\d{1,2}:\d{2}$',
            r'\s*\(\d+分钟\)$',
            r'\s*\[\d+\]$',
            r'^[▶►]+\s*',
        ]
        
        for pattern in time_patterns:
            title = re.sub(pattern, '', title)
        
        return title.strip()
    
    def _get_title_from_siblings(self, element):
        """从相邻元素获取标题"""
        try:
            # 尝试获取父元素
            parent = element.find_element(By.XPATH, "./..")
            
            # 在父元素中查找可能的标题元素
            title_selectors = [
                ".title", ".video-title", ".name", "h2", "h3", "h4",
                ".card-title", ".post-title", ".item-title",
                '[data-title]', '[title]', 'strong', 'b'
            ]
            
            for selector in title_selectors:
                try:
                    title_el = parent.find_element(By.CSS_SELECTOR, selector)
                    if title_el and title_el != element:
                        text = title_el.text.strip()
                        if text and not self._is_time_format(text):
                            return text
                except:
                    continue
            
            # 如果没找到，获取父元素的文本
            parent_text = parent.text.strip()
            lines = parent_text.split('\n')
            for line in lines:
                line = line.strip()
                if line and not self._is_time_format(line) and len(line) > 5:
                    return line
        
        except Exception as e:
            logger.debug(f"从相邻元素获取标题失败: {e}")
        
        return None
    
    def _get_thumbnail_url(self, element):
        """获取缩略图URL"""
        try:
            # 查找img元素
            img = element.find_element(By.TAG_NAME, "img")
            return img.get_attribute("src") or img.get_attribute("data-src")
        except:
            return ""
    
    def _get_duration(self, element):
        """获取视频时长"""
        try:
            # 查找时长元素
            duration_selectors = [
                ".duration", ".time", ".length",
                ".video-duration", ".item-duration"
            ]
            
            for selector in duration_selectors:
                try:
                    duration_el = element.find_element(By.CSS_SELECTOR, selector)
                    text = duration_el.text.strip()
                    if text:
                        return text
                except:
                    continue
        except:
            pass
        
        return ""
    
    def _get_extra_info(self, element):
        """获取额外信息（演员、观看数等）"""
        info = {}
        
        try:
            # 查找可能的父容器
            parent = element.find_element(By.XPATH, "./ancestor::div[contains(@class, 'item') or contains(@class, 'video')][1]")
            
            # 演员信息
            actor_selectors = [".actor", ".star", ".model", ".name"]
            for selector in actor_selectors:
                try:
                    actor_el = parent.find_element(By.CSS_SELECTOR, selector)
                    info['actor'] = actor_el.text.strip()
                    break
                except:
                    continue
            
            # 观看数
            views_selectors = [".views", ".view-count", ".count"]
            for selector in views_selectors:
                try:
                    views_el = parent.find_element(By.CSS_SELECTOR, selector)
                    info['views'] = views_el.text.strip()
                    break
                except:
                    continue
            
            # 发布时间
            date_selectors = [".date", ".time", ".posted", ".upload-time"]
            for selector in date_selectors:
                try:
                    date_el = parent.find_element(By.CSS_SELECTOR, selector)
                    info['date'] = date_el.text.strip()
                    break
                except:
                    continue
        
        except:
            pass
        
        return info
    
    def _find_next_page(self):
        """查找下一页链接 - 简化版"""
        try:
            # 1. 先查找明确的"下一页"链接
            try:
                # 使用XPath查找包含"下一页"或"Next"的链接
                next_link = self.driver.find_element(By.XPATH, 
                    "//a[contains(text(), '下一页') or contains(text(), 'Next') or contains(text(), 'next')]")
                href = next_link.get_attribute("href")
                if href and next_link.is_displayed():
                    logger.info("找到'下一页'按钮")
                    return href
            except:
                pass
            
            # 2. 查找常见的下一页选择器
            next_selectors = [
                "a[rel='next']",
                ".next a",
                ".next-page",
                "a.next",
                ".page-next a",
                ".pagination .next a",
            ]
            
            for selector in next_selectors:
                try:
                    link = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if link.is_displayed():
                        href = link.get_attribute("href")
                        if href:
                            logger.info(f"找到下一页链接: {selector}")
                            return href
                except:
                    continue
            
            # 3. 处理数字分页：当前页是span，找它后面的a标签
            try:
                # 先找到当前页元素（span.page-link.active.disabled）
                current_page_elem = self.driver.find_element(By.CSS_SELECTOR, 
                    ".page-link.active, .active.page-link, .page-item.active .page-link")
                
                if current_page_elem:
                    # 查找当前页元素的下一个兄弟a标签
                    try:
                        # 方法1: 使用XPath查找当前元素的下一个兄弟a标签
                        next_a = self.driver.execute_script("""
                            var elem = arguments[0];
                            var nextSibling = elem.nextElementSibling;
                            while(nextSibling) {
                                if(nextSibling.tagName.toLowerCase() === 'a') {
                                    return nextSibling;
                                }
                                nextSibling = nextSibling.nextElementSibling;
                            }
                            return null;
                        """, current_page_elem)
                        
                        if next_a:
                            href = next_a.getAttribute("href")
                            if href:
                                logger.info("找到下一个分页链接(兄弟a标签)")
                                return href
                    except:
                        pass
                    
                    # 方法2: 使用XPath查找当前页后面的第一个a标签
                    try:
                        next_num_link = current_page_elem.find_element(By.XPATH, 
                            "./following-sibling::a[1]")
                        href = next_num_link.get_attribute("href")
                        if href:
                            logger.info("找到下一个分页链接(following-sibling)")
                            return href
                    except:
                        pass
                    
                    # 方法3: 如果当前页在li中，找下一个li中的a标签
                    try:
                        parent_li = current_page_elem.find_element(By.XPATH, "./ancestor::li[1]")
                        next_li = parent_li.find_element(By.XPATH, "./following-sibling::li[1]")
                        next_a = next_li.find_element(By.TAG_NAME, "a")
                        href = next_a.get_attribute("href")
                        if href:
                            logger.info("找到下一个分页链接(相邻li)")
                            return href
                    except:
                        pass
            except:
                pass
            
            # 4. 查找所有分页链接，尝试取最后一个或最大的数字
            try:
                # 查找所有分页a标签
                all_page_links = self.driver.find_elements(By.CSS_SELECTOR, 
                    ".pagination a, .page-numbers a, .page-link")
                
                if all_page_links:
                    # 获取当前URL和可能的页码
                    current_url = self.driver.current_url
                    current_page_num = 1
                    
                    # 从URL中提取当前页码
                    patterns = [r'page=(\d+)', r'p=(\d+)', r'/page/(\d+)', r'/(\d+)/$']
                    for pattern in patterns:
                        match = re.search(pattern, current_url)
                        if match:
                            current_page_num = int(match.group(1))
                            break
                    
                    # 尝试找到比当前页码大的链接
                    page_links_with_numbers = []
                    for link in all_page_links:
                        try:
                            href = link.get_attribute("href")
                            text = link.text.strip()
                            
                            if href and href != current_url:
                                # 从href中提取页码
                                for pattern in patterns:
                                    match = re.search(pattern, href)
                                    if match:
                                        page_num = int(match.group(1))
                                        if page_num > current_page_num:
                                            page_links_with_numbers.append((page_num, href))
                                        break
                                # 或者从文本中提取页码
                                    elif text.isdigit():
                                        page_num = int(text)
                                    if page_num > current_page_num:
                                        page_links_with_numbers.append((page_num, href))
                        except:
                            continue
                    
                    # 如果有比当前页大的页码，取最小的那个
                    if page_links_with_numbers:
                        page_links_with_numbers.sort()
                        logger.info(f"找到下一页，页码: {page_links_with_numbers[0][0]}")
                        return page_links_with_numbers[0][1]
                    
                    # 如果没有找到更大的页码，尝试最后一个链接
                    last_link = all_page_links[-1]
                    href = last_link.get_attribute("href")
                    if href and href != current_url:
                        logger.info("使用最后一个分页链接作为下一页")
                        return href
            except:
                pass
            
            # 5. 从URL中推断下一页
            current_url = self.driver.current_url
            # 匹配常见的分页模式
            patterns = [
                (r'(page=)(\d+)', lambda m: f"{m.group(1)}{int(m.group(2))+1}"),
                (r'(p=)(\d+)', lambda m: f"{m.group(1)}{int(m.group(2))+1}"),
                (r'/page/(\d+)', lambda m: f"/page/{int(m.group(1))+1}"),
                (r'/(\d+)/$', lambda m: f"/{int(m.group(1))+1}/"),
            ]
            
            for pattern, replace_func in patterns:
                match = re.search(pattern, current_url)
                if match:
                    next_url = re.sub(pattern, replace_func(match), current_url)
                    logger.info(f"通过URL模式构造下一页: {next_url}")
                    return next_url
            
            # 6. 查找"加载更多"按钮
            try:
                more_buttons = [
                    ".load-more", ".more-button", ".show-more", 
                    ".btn-more", ".btn-load-more"
                ]
                
                for selector in more_buttons:
                    try:
                        button = self.driver.find_element(By.CSS_SELECTOR, selector)
                        if button.is_displayed():
                            # 点击按钮加载更多内容（不是真正的分页）
                            logger.info("找到'加载更多'按钮，但这不是分页链接")
                            return None  # 返回None表示需要特殊处理
                    except:
                        continue
            except:
                pass
        
        except Exception as e:
            logger.debug(f"查找分页失败: {e}")
        
        logger.info("未找到下一页链接")
        return None

    def save_to_excel(self, results, filename=None):
        """保存结果到Excel"""
        if not results:
            logger.warning("没有数据可保存")
            return None
        
        try:
            # 创建输出目录
            output_dir = "output"
            os.makedirs(output_dir, exist_ok=True)
            
            # 生成文件名
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"video_data_{timestamp}.xlsx"
            
            filepath = os.path.join(output_dir, filename)
            
            # 创建DataFrame
            df = pd.DataFrame(results)
            
            # 保存到Excel
            df.to_excel(filepath, index=False, engine='openpyxl')
            
            logger.info(f"✅ 数据保存成功！共 {len(results)} 条记录")
            logger.info(f"📁 文件路径: {filepath}")
            
            return filepath
        
        except Exception as e:
            logger.error(f"保存Excel文件时出错: {e}")
            return None
        
    def save_to_csv(self, results, filename=None):
        """保存结果到CSV"""
        if not results:
            logger.warning("没有数据可保存")
            return None
        
        try:
            output_dir = "output"
            os.makedirs(output_dir, exist_ok=True)
            
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"video_data_{timestamp}.csv"
            
            filepath = os.path.join(output_dir, filename)
            
            df = pd.DataFrame(results)
            df.to_csv(filepath, index=False, encoding='utf-8-sig')
            
            logger.info(f"✅ CSV文件保存成功！")
            logger.info(f"📁 文件路径: {filepath}")
            
            return filepath
        
        except Exception as e:
            logger.error(f"保存CSV文件时出错: {e}")
            return None
    
    def close(self):
        """关闭浏览器"""
        try:
            self.driver.quit()
            logger.info("浏览器已关闭")
        except:
            pass
# 使用示例
if __name__ == "__main__":
    # 配置参数
    config = {
        "headless": False,  # 是否无头模式
        "target_url": "https://jable.tv/hot/",  # 目标网址
        "max_pages": 3,  # 最大爬取页数
        "output_format": "excel",  # 输出格式: excel 或 csv
    }
    
    crawler = None
    
    try:
        # 初始化爬虫
        crawler = VideoCrawler(headless=config["headless"])
        
        # 提取数据
        logger.info("开始爬取视频数据...")
        video_data = crawler.extract_video_data(
            page_url=config["target_url"],
            max_pages=config["max_pages"]
        )
        
        # 保存数据
        if video_data:
            if config["output_format"].lower() == "excel":
                crawler.save_to_excel(video_data)
            else:
                crawler.save_to_csv(video_data)
            
            # 显示统计信息
            print("\n" + "="*50)
            print(f"📊 爬取完成！统计信息：")
            print(f"   总视频数: {len(video_data)}")
            print(f"   采集时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("="*50)
            
            # 显示前5条数据
            print("\n📋 前5条数据预览：")
            for i, item in enumerate(video_data[:5], 1):
                print(f"{i}. {item['标题'][:60]}...")
                print(f"   时长: {item['时长']} | 演员: {item['演员'][:30]}")
                print()
        
        else:
            logger.error("没有提取到任何视频数据")
    
    except KeyboardInterrupt:
        logger.info("用户中断了程序")
    
    except Exception as e:
        logger.error(f"程序执行出错: {e}")
    
    finally:
        # 确保关闭浏览器
        if crawler:
            crawler.close()
"""**********************************************************************************************************"""
#爬网页 图片链接
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
def extract_lazyload_images(driver, url):
    """专门提取懒加载图片"""
    
    print(f"🌐 访问: {url}")
    driver.get(url)
    
    # 等待页面加载
    time.sleep(3)
    
    # 模拟滚动，确保懒加载图片加载
    print("📜 滚动页面以加载懒加载图片...")
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    for i in range(3):
        # 滚动到页面底部
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        
        # 计算新的滚动高度
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    
    # 等待图片加载
    time.sleep(2)
    
    # 方法1：查找所有img标签
    img_elements = driver.find_elements(By.TAG_NAME, 'img')
    print(f"找到 {len(img_elements)} 个img标签")
    
    images = []
    processed_urls = set()  # 用于去重
    
    for idx, img in enumerate(img_elements, 1):
        try:
            # 获取各种属性
            src = img.get_attribute('src') or ''
            data_src = img.get_attribute('data-src') or ''
            data_original = img.get_attribute('data-original') or ''
            alt = img.get_attribute('alt') or ''
            img_class = img.get_attribute('class') or ''
            
            # 优先使用data-src（懒加载图片）
            img_url = data_src if data_src else (data_original if data_original else src)
            
            # 清理URL
            if img_url:
                # 移除URL中的空格和引号
                img_url = img_url.strip().strip('"').strip("'")
                
                # 确保URL完整
                if img_url.startswith('//'):
                    img_url = 'https:' + img_url
                elif img_url.startswith('/'):
                    img_url = 'https://jable.tv' + img_url
                
                # 去重
                if img_url in processed_urls:
                    continue
                processed_urls.add(img_url)
                
                # 获取其他信息
                width = img.get_attribute('width') or ''
                height = img.get_attribute('height') or ''
                title = img.get_attribute('title') or ''
                data_preview = img.get_attribute('data-preview') or ''
                
                # 提取可能的视频ID
                video_id = ''
                if 'videos_screenshots' in img_url:
                    # 从URL中提取视频ID，如：/55000/55958/
                    parts = img_url.split('/')
                    try:
                        # 查找包含数字的部分
                        for i, part in enumerate(parts):
                            if part.isdigit() and i+1 < len(parts) and parts[i+1].isdigit():
                                video_id = f"{part}/{parts[i+1]}"
                                break
                    except:
                        pass
                
                images.append({
                    '序号': idx,
                    '图片URL': img_url,
                    'ALT文本': alt,
                    'Class类名': img_class,
                    '宽度': width,
                    '高度': height,
                    '标题': title,
                    'data-preview': data_preview,
                    '视频ID': video_id,
                    '来源属性': 'data-src' if data_src else ('data-original' if data_original else 'src')
                })
                
        except Exception as e:
            print(f"处理第 {idx} 个img标签时出错: {e}")
            continue
    
    return images

def filter_jable_images(images):
    """过滤出jable.tv的特定图片"""
    
    jable_patterns = [
        'assets-cdn.jable.tv',
        'videos_screenshots',
        '320x180',
        '1.jpg'
    ]
    
    filtered_images = []
    for img in images:
        img_url = img.get('图片URL', '').lower()
        
        # 检查是否匹配jable.tv的图片
        is_jable = any(pattern in img_url for pattern in jable_patterns)
        
        if is_jable:
            # 添加额外信息
            img['类型'] = '视频截图'
            img['尺寸'] = '320x180'
            
            # 尝试提取更多信息
            if 'videos_screenshots' in img_url:
                parts = img_url.split('/')
                try:
                    idx_55000 = parts.index('55000') if '55000' in parts else -1
                    if idx_55000 != -1 and idx_55000 + 2 < len(parts):
                        img['视频编号'] = parts[idx_55000 + 1]
                except:
                    pass
            
            filtered_images.append(img)
    
    return filtered_images

# 主函数
def main():
    # 设置Selenium
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    
    # 初始化驱动
    driver = webdriver.Chrome(options=options)
    
    try:
        # 目标URL
        url = "https://jable.tv/hot/"
        
        # 提取图片
        all_images = extract_lazyload_images(driver, url)
        
        print(f"\n📊 统计信息:")
        print(f"  总共找到图片: {len(all_images)}")
        
        if all_images:
            # 保存所有图片
            df_all = pd.DataFrame(all_images)
            df_all.to_excel('all_images.xlsx', index=False)
            print(f"  所有图片已保存到: all_images.xlsx")
            
            # 过滤出jable.tv的特定图片
            jable_images = filter_jable_images(all_images)
            
            if jable_images:
                print(f"  jable.tv特定图片: {len(jable_images)}")
                
                # 保存jable.tv图片
                df_jable = pd.DataFrame(jable_images)
                df_jable.to_excel('jable_specific_images.xlsx', index=False)
                print(f"  jable.tv图片已保存到: jable_specific_images.xlsx")
                
                # 显示前10个
                print(f"\n🔗 前10个jable.tv图片:")
                for i, img in enumerate(jable_images[:10], 1):
                    img_url = img.get('图片URL', '')
                    alt = img.get('ALT文本', '无标题')
                    print(f"  {i:2d}. {alt[:30]:30} | {img_url[:60]:60}...")
            else:
                print("  未找到jable.tv特定图片模式")
        else:
            print("  未找到任何图片")
            
    except Exception as e:
        print(f"❌ 错误: {e}")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    main()

"""**********************************************************************************************************"""
#下载图片、预览视频 jable.TV

#打开cmd输入： "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="D:\selenium_user_data" 

# --- 设置开关：'image' 为下载封面图，'video' 为下载预览视频 ---
DOWNLOAD_TYPE = 'image' 
# ---------------------------------------------------------
import time
import requests
import os
import sys
import io
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# 强制编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 配置接管参数
chrome_options = Options()
chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
driver = webdriver.Chrome(options=chrome_options)

def download_files(names, urls, file_type):
    # 根据类型选择文件夹
    save_dir = "downloaded_videos" if file_type == 'video' else "downloaded_images"
    ext = ".mp4" if file_type == 'video' else ".jpg"
    
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    for name, url in zip(names, urls):
        if not url: continue
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                # 过滤掉文件名中的非法字符（防止报错）
                clean_name = "".join([c for c in name if c.isalnum() or c in (' ', '_')]).strip()
                file_path = os.path.join(save_dir, f"{clean_name}{ext}")
                
                with open(file_path, "wb") as f:
                    f.write(response.content)
                print(f"成功下载 [{file_type}]: {clean_name}")
            else:
                print(f"下载失败 {url}，状态码: {response.status_code}")
        except Exception as e:
            print(f"处理 {url} 时出错: {e}")

if __name__ == "__main__": 
    names = []
    urls = []
    
    # 1. 获取标题
    title_elements = driver.find_elements(By.CSS_SELECTOR, "h6.title a")
    names = [el.text for el in title_elements]
    
    # 2. 获取内容地址
    img_elements = driver.find_elements(By.CSS_SELECTOR, "div.img-box img")
    
    for img in img_elements:
        if DOWNLOAD_TYPE == 'video':
            # 获取预览视频地址
            src = img.get_attribute('data-preview')
        else:
            # 获取封面图片地址
            src = img.get_attribute('data-src')
        urls.append(src)
    
    print(f"准备下载 {len(urls)} 个文件类型为: {DOWNLOAD_TYPE}")
    download_files(names, urls, DOWNLOAD_TYPE)




"""**********************************************************************************************************"""
#列表、字典用法
# 存放视频 ID 的列表
video_list = ["MIDA-460", "DASS-610", "MILK-166"]
# 1. 打印第一个元素（索引从 0 开始）
print(video_list[0])  # 输出: MIDA-460

# 2. 在末尾添加新数据
video_list.append("SNIS-123")

# 3. 统计长度（多少个数据）
print(len(video_list))  # 输出: 4

# 4. 循环打印：
for video in video_list:
    print(f"当前视频: {video}")


# 一个视频的详细字典
video_info = {
    "序号": 1,
    "标题": "MIDA-460 中出",
    "图片URL": "assets-cdn.jable.tv..."
}

# 1. 打印特定的数据（根据“键”取“值”）
print(video_info["标题"])  # 输出: MIDA-460 中出

# 2. 修改或增加数据
video_info["时长"] = "120:00"

# 3. 安全获取数据（防止键不存在导致报错）
print(video_info.get("ALT文本", "无描述")) # 如果找不到返回“无描述”

# 4. 循环打印：
for key, value in video_info.items():
    print(f"{key}: {value}")


"""**********************************************************************************************************"""
import requests
import os

# 1. 假设这是你取得的字典
item = {
    '序号': 1, 
    '图片URL': 'assets-cdn.jable.tv', 
    '标题': '示例图片'
}

def download_img(data):
    url = data.get('图片URL')
    if not url:
        print("字典中没有图片URL")
        return

    # 2. 建立保存文件夹
    save_dir = "downloaded_images"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # 3. 确定文件名 (使用序号或者从URL截取)
    # 建议加上 .png 或 .jpg 后缀
    file_name = f"{data['序号']}.png" 
    save_path = os.path.join(save_dir, file_name)

    try:
        # 4. 发送请求并下载
        # 对于某些网站（如Jable），建议加上 headers 模拟浏览器，防止被拦截
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Referer": "jable.tv"  # 某些防盗链网站必须加这个
        }
        
        print(f"正在下载: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                f.write(response.content)
            print(f"✅ 下载成功！保存在: {os.path.abspath(save_path)}")
        else:
            print(f"❌ 下载失败，状态码: {response.status_code}")

    except Exception as e:
        print(f"发生错误: {e}")

# 执行下载
download_img(item)
"""**********************************************************************************************************"""   
#视频标题改名图片
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import sys
import os
import requests
import io
import re
import urllib.parse
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def extract_lazyload_images(driver, url):
    """提取图片及其对应的视频标题 - 改进版"""
    print(f"🌐 访问: {url}")
    driver.get(url)
    
    # 增加等待时间，确保页面完全加载
    time.sleep(5)
    
    # 模拟滚动加载更多内容
    for i in range(5):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        
        # 随机滚动到中间位置
        if i % 2 == 0:
            driver.execute_script(f"window.scrollBy(0, {i * 200});")
            time.sleep(1)
    
    # 滚动回顶部，确保所有元素可见
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(2)
    
    # --- 关键修复点：使用更通用的选择器 ---
    # 方法1：查找所有包含/videos/的链接（通常是视频链接）
    try:
        video_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/videos/']")
        print(f"找到 {len(video_links)} 个视频链接")
    except Exception as e:
        print(f"查找视频链接失败: {e}")
        video_links = []
    
    # 方法2：如果方法1失败，尝试其他选择器
    if not video_links:
        try:
            video_links = driver.find_elements(By.CSS_SELECTOR, 
                ".item a, .video-item a, .post a, .thumbnail a, .card a")
            print(f"备用选择器找到 {len(video_links)} 个链接")
        except:
            video_links = []
    
    images = []
    processed_urls = set()
    processed_titles = set()  # 防止重复标题

    for idx, link in enumerate(video_links, 1):
        try:
            # 跳过没有href的链接
            href = link.get_attribute("href")
            if not href:
                continue
            
            # 1. 获取标题 - 多种方式尝试
            title = None
            
            # 方式1：从title属性获取
            title = link.get_attribute("title")
            
            # 方式2：从文本获取
            if not title or len(title.strip()) < 2:
                link_text = link.text.strip()
                # 过滤掉时间格式的文本（如 01:23:45）
                if link_text and not re.match(r'^\d{1,2}:\d{2}(:\d{2})?$', link_text):
                    title = link_text
            
            # 方式3：从img的alt属性获取
            if not title or len(title.strip()) < 2:
                try:
                    img = link.find_element(By.TAG_NAME, "img")
                    alt_text = img.get_attribute("alt")
                    if alt_text and len(alt_text.strip()) > 2:
                        title = alt_text
                except:
                    pass
            
            # 方式4：从相邻元素获取
            if not title or len(title.strip()) < 2:
                try:
                    # 查找父元素中的标题元素
                    parent = link.find_element(By.XPATH, "./..")
                    title_selectors = [".title", ".video-title", ".name", "h2", "h3", "h4"]
                    for selector in title_selectors:
                        try:
                            title_elem = parent.find_element(By.CSS_SELECTOR, selector)
                            text = title_elem.text.strip()
                            if text and len(text) > 2:
                                title = text
                                break
                        except:
                            continue
                except:
                    pass
            
            # 如果还是没有标题，使用默认标题
            if not title or len(title.strip()) < 2:
                title = f"视频_{idx}"
            
            # 2. 清理标题：移除Windows文件名不允许的特殊字符
            clean_title = re.sub(r'[\\/:*?"<>|\n\r\t]', '_', title).strip()
            # 移除开头和结尾的下划线
            clean_title = re.sub(r'^_+|_+$', '', clean_title)
            # 限制标题长度（避免文件名过长）
            if len(clean_title) > 100:
                clean_title = clean_title[:100] + "..."
            
            # 3. 检查标题是否重复，如果重复则添加序号
            base_title = clean_title
            counter = 1
            while clean_title in processed_titles:
                clean_title = f"{base_title}_{counter}"
                counter += 1
            
            processed_titles.add(clean_title)
            
            # 4. 获取图片
            img_url = None
            try:
                img = link.find_element(By.TAG_NAME, "img")
                # 优先使用data-src（懒加载图片）
                img_url = img.get_attribute("data-src") or img.get_attribute("src")
                
                # 如果没有找到，尝试其他属性
                if not img_url:
                    img_url = img.get_attribute("data-original") or img.get_attribute("data-lazy-src")
                
                # 处理相对路径
                if img_url and img_url.startswith('//'):
                    img_url = 'https:' + img_url
                elif img_url and img_url.startswith('/'):
                    img_url = urllib.parse.urljoin(url, img_url)
            except:
                # 如果没有找到图片，跳过这个链接
                continue
            
            if img_url and img_url not in processed_urls:
                processed_urls.add(img_url)
                
                # 5. 收集信息
                images.append({
                    '序号': idx,
                    '图片URL': img_url,
                    '原始标题': title,  # 保留原始标题用于显示
                    '文件名': clean_title,
                    '视频链接': href,
                    'ALT文本': img.get_attribute("alt") if img_url else ""
                })
                print(f"✅ [{idx}] 提取: {clean_title[:50]}...")
                print(f"   图片: {img_url[:80]}...")
                
        except Exception as e:
            print(f"⚠️  处理第 {idx} 个链接时出错: {e}")
            continue
    
    print(f"\n📊 提取统计:")
    print(f"  成功提取: {len(images)} 个视频")
    print(f"  去重后图片: {len(processed_urls)} 个")
    
    return images

def filter_jable_images(images):
    """过滤出jable.tv的特定图片 - 改进版"""
    jable_patterns = [
        'assets-cdn.jable.tv',
        'videos_screenshots',
        '320x180',
        '.jpg',
        '.png',
        '.webp'
    ]
    
    filtered_images = []
    for img in images:
        img_url = img.get('图片URL', '').lower()
        
        # 检查是否匹配jable.tv的图片
        is_jable = any(pattern in img_url for pattern in jable_patterns)
        
        if is_jable:
            # 添加额外信息
            img['类型'] = '视频截图'
            
            # 尝试提取尺寸信息
            if '320x180' in img_url:
                img['尺寸'] = '320x180'
            elif '640x360' in img_url:
                img['尺寸'] = '640x360'
            elif '1280x720' in img_url:
                img['尺寸'] = '1280x720'
            else:
                img['尺寸'] = '未知'
            
            # 尝试提取视频编号
            if 'videos_screenshots' in img_url:
                # 例如: /contents/videos_screenshots/55000/55908/320x180/1.jpg
                match = re.search(r'videos_screenshots/(\d+)/(\d+)/', img_url)
                if match:
                    img['分类ID'] = match.group(1)
                    img['视频ID'] = match.group(2)
            
            filtered_images.append(img)
    
    return filtered_images

def download_img(data_list):
    """下载图片 - 改进版"""
    save_dir = "downloaded_images"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    # 创建统计信息
    success_count = 0
    skip_count = 0
    fail_count = 0
    
    print(f"\n📥 开始下载图片到: {os.path.abspath(save_dir)}")
    
    for idx, item in enumerate(data_list, 1):
        url = item.get('图片URL')
        title = item.get('文件名', f"unknown_{item['序号']}")
        video_id = item.get('视频ID', '')
        
        if not url:
            print(f"⚠️  [{idx}] 跳过: 无图片URL")
            continue
        
        # 确定文件扩展名
        if '.jpg' in url.lower() or 'jpeg' in url.lower():
            file_extension = ".jpg"
        elif '.png' in url.lower():
            file_extension = ".png"
        elif '.webp' in url.lower():
            file_extension = ".webp"
        elif '.gif' in url.lower():
            file_extension = ".gif"
        else:
            file_extension = ".jpg"  # 默认
        
        # 如果标题过长，使用视频ID或序号
        if len(title) > 150:
            if video_id:
                title = f"video_{video_id}"
            else:
                title = f"video_{item['序号']}"
        
        # 生成文件名
        file_name = f"{title}{file_extension}"
        save_path = os.path.join(save_dir, file_name)
        
        # 如果文件已存在，添加时间戳
        counter = 1
        while os.path.exists(save_path):
            file_name = f"{title}_{counter}{file_extension}"
            save_path = os.path.join(save_dir, file_name)
            counter += 1
            if counter > 100:  # 防止无限循环
                break
        
        try:
            # 设置请求头
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Referer": "https://jable.tv/",
                "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            }
            
            print(f"\n[{idx}/{len(data_list)}] 下载: {title[:50]}...")
            print(f"   来源: {url[:80]}...")
            
            # 下载图片
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                with open(save_path, 'wb') as f:
                    f.write(response.content)
                
                # 检查文件是否成功写入
                if os.path.exists(save_path) and os.path.getsize(save_path) > 0:
                    success_count += 1
                    print(f"   ✅ 保存为: {file_name}")
                else:
                    fail_count += 1
                    print(f"   ❌ 保存失败")
            else:
                fail_count += 1
                print(f"   ❌ HTTP错误: {response.status_code}")
        
        except requests.exceptions.Timeout:
            fail_count += 1
            print(f"   ❌ 请求超时")
        except requests.exceptions.ConnectionError:
            fail_count += 1
            print(f"   ❌ 连接错误")
        except Exception as e:
            fail_count += 1
            print(f"   ❌ 错误: {str(e)}")
        
        # 添加延迟，避免被封
        time.sleep(0.5)
    
    # 打印统计信息
    print(f"\n📊 下载统计:")
    print(f"  成功: {success_count}")
    print(f"  失败: {fail_count}")
    print(f"  跳过: {skip_count}")
    print(f"  保存路径: {os.path.abspath(save_dir)}")

def save_to_excel(data_list, filename=None):
    """保存结果到Excel"""
    if not data_list:
        print("❌ 没有数据可保存")
        return
    
    # 创建输出目录
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    # 生成文件名
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"video_images_{timestamp}.xlsx"
    
    filepath = os.path.join(output_dir, filename)
    
    try:
        # 创建DataFrame
        df = pd.DataFrame(data_list)
        
        # 保存到Excel
        df.to_excel(filepath, index=False, engine='openpyxl')
        
        print(f"\n💾 Excel文件保存成功！")
        print(f"   文件路径: {filepath}")
        print(f"   记录数量: {len(data_list)}")
        
        return filepath
    
    except Exception as e:
        print(f"❌ 保存Excel文件时出错: {e}")
        return None

# 主函数
def main(url):
    print("=" * 60)
    print("🎬 Jable.tv 视频封面下载器")
    print("=" * 60)
    
    # 设置Selenium
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    
    # 初始化驱动
    driver = webdriver.Chrome(options=options)
    
    try:
        # 提取图片
        print("\n🔍 正在提取图片信息...")
        all_images = extract_lazyload_images(driver, url)
        
        if not all_images:
            print("❌ 没有找到任何图片")
            return
        
        # 过滤jable图片
        jable_images = filter_jable_images(all_images)
        
        print(f"\n🎯 Jable图片筛选结果:")
        print(f"  总共找到: {len(all_images)} 个图片")
        print(f"  Jable图片: {len(jable_images)} 个")
        
        # 保存到Excel
        excel_file = save_to_excel(jable_images)
        
        
            # 执行下载
        download_img(jable_images)
        
        
        print("\n✨ 程序执行完成！")
        
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断了程序")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        driver.quit()
        print("✅ 浏览器已关闭")

if __name__ == "__main__":
    # 示例URL
    # url = "https://jable.tv/models/akari-niimura/"
    # url = "https://jable.tv/categories/pov/"
    
    # 从用户输入获取URL
    
    
    
    print("使用默认URL: https://jable.tv/models/akari-niimura/")
    url = "https://jable.tv/models/akari-niimura/"
    
    main(url)

"""**********************************************************************************************************"""
#调试模式  依次打开并关闭课程
#打开cmd输入： "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="D:\selenium_user_data" 
import time
import sys
import io
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

chrome_options = Options()
chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
driver = webdriver.Chrome(options=chrome_options)

def auto_process():
    # 1. 记录当前主窗口
    main_window = driver.current_window_handle
    
    # 2. 获取初始数量
    initial_elements = driver.find_elements(By.CSS_SELECTOR, "a img.com_img.jet_img")
    count = len(initial_elements)
    print(f"发现 {count} 个链接")

    for i in range(count):
        try:
            # 【重要修正】每次循环都重新获取一次列表，并根据索引取元素
            items = driver.find_elements(By.CSS_SELECTOR, "a img.com_img.jet_img")
            target_btn = items[i]
            
            # 记录点击前的窗口数量
            pre_windows_count = len(driver.window_handles)
            
            # 点击
            driver.execute_script("arguments[0].click();", target_btn) # 使用JS点击更稳
            print(f"正在处理第 {i+1} 个链接...")

            # 3. 等待新窗口出现（判断窗口总数增加）
            WebDriverWait(driver, 10).until(lambda d: len(d.window_handles) > pre_windows_count)
            
            # 4. 识别并锁定新窗口
            new_window = [h for h in driver.window_handles if h != main_window][-1]
            # 5. 切换控制权
            driver.switch_to.window(new_window)
            # 6. 获取标题与等待
            print(f"已进入新页面: {driver.title}")
            time.sleep(random.uniform(1.2, 2.5)) # 停留1秒
            
            # 7. 关闭新窗口并切回
            driver.close()
            driver.switch_to.window(main_window)
            
            # 给主页一点反应时间
            time.sleep(1) 
            
        except Exception as e:
            print(f"第 {i+1} 个处理失败: {e}")
            # 确保出错也能切回主窗口继续下一个
            driver.switch_to.window(main_window)
            continue
    print("程序结束")
if __name__ == "__main__":
    auto_process()



    

"""**********************************************************************************************************"""
# 切换到标题含“淘宝”的窗口
def switch_to_window_by_title(driver, target_title):
    """根据窗口标题切换，匹配部分标题即可"""
    for handle in driver.window_handles:
        driver.switch_to.window(handle)
        if target_title in driver.title:
            return True
    return False

# 调用示例
switch_to_window_by_title(driver, "淘宝") 
print("切回后窗口标题：", driver.title)  


"""**********************************************************************************************************"""




"""**********************************************************************************************************"""





"""**********************************************************************************************************"""





"""**********************************************************************************************************"""
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AutoExam:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
        self.question_bank = {}  # 题库：{qid: correct_answer_value}
    
    def take_exam(self):
        """参加考试"""
        logger.info("开始考试...")
        
        try:
            # 等待页面加载
            time.sleep(2)
            
            # 查找所有题目
            question_tables = self.driver.find_elements(By.CLASS_NAME, "tablestyle")
            
            # 遍历每个题目
            for table in question_tables:
                try:
                    # 获取题目ID
                    q_label = table.find_element(By.CLASS_NAME, "q_name")
                    qid = q_label.get_attribute("data-qid")
                    question_text = q_label.text.strip()
                    
                    # 获取所有选项
                    options = table.find_elements(By.CSS_SELECTOR, "input.qo_name[type='radio']")
                    
                    # 如果题库中有正确答案，就选择正确答案
                    if qid in self.question_bank:
                        correct_value = self.question_bank[qid]
                        for option in options:
                            if option.get_attribute("value") == correct_value:
                                option.click()
                                logger.info(f"选择已知正确答案: {question_text[:30]}...")
                                break
                    else:
                        # 随机选择一个答案（第一次考试）
                        if options:
                            random.choice(options).click()
                            logger.info(f"随机选择答案: {question_text[:30]}...")
                    
                    time.sleep(0.5)  # 短暂等待
                    
                except Exception as e:
                    logger.warning(f"处理题目时出错: {e}")
                    continue
            
            # 提交考试
            submit_button = self.driver.find_element(By.ID, "btn_submit")
            submit_button.click()
            logger.info("提交考试")
            
            # 等待页面跳转
            time.sleep(3)
            
            return True
            
        except Exception as e:
            logger.error(f"考试过程中出错: {e}")
            return False
    
    def analyze_result(self):
        """分析考试结果，记录正确答案"""
        logger.info("分析考试结果...")
        
        try:
            # 等待结果页面加载
            time.sleep(2)
            
            # 检查是否通过
            result_text = ""
            try:
                tips_img = self.driver.find_element(By.CSS_SELECTOR, ".state_tips .tips_img")
                tips_src = tips_img.get_attribute("src")
                if "fail" in tips_src:
                    logger.info("考试未通过")
                    result_text = "fail"
                elif "success" in tips_src or "pass" in tips_src:
                    logger.info("考试通过！")
                    return True
            except:
                pass
            
            # 如果没有找到结果图片，检查是否有"考试通过"等文字
            page_text = self.driver.page_source
            if "考试通过" in page_text or "恭喜" in page_text:
                logger.info("考试通过！")
                return True
            
            # 获取所有题目结果
            question_items = self.driver.find_elements(By.CSS_SELECTOR, ".state_cour_lis")
            
            for item in question_items:
                try:
                    # 获取题目文本
                    question_elem = item.find_element(By.CSS_SELECTOR, ".state_lis_text[title]")
                    question_text = question_elem.get_attribute("title")
                    
                    # 获取用户答案
                    answer_elem = item.find_element(By.CSS_SELECTOR, ".state_lis_text:not([title])")
                    user_answer = answer_elem.text.replace("【您的答案： ", "").replace("】", "")
                    
                    # 检查是否正确（通过图片判断）
                    img_elem = item.find_element(By.CSS_SELECTOR, "img.state_error")
                    img_src = img_elem.get_attribute("src")
                    
                    # 如果图片是bar_img.png，表示正确，记录这个答案
                    if "bar_img.png" in img_src:
                        # 我们需要找到这个题目的qid和正确答案的value
                        # 由于结果页面没有显示qid，我们需要在下次考试时通过题目文本来匹配
                        # 这里我们先记录题目文本和正确答案的映射
                        logger.info(f"题目正确: {question_text[:30]}... - 答案: {user_answer}")
                        
                        # 在下次考试中，我们需要通过题目文本来匹配正确答案
                        # 由于题目顺序会打乱，我们需要记录完整的题目文本
                        # 但这里我们暂时不处理，因为我们有qid映射
                        
                    elif "error_icon.png" in img_src:
                        logger.info(f"题目错误: {question_text[:30]}... - 用户答案: {user_answer}")
                        
                except Exception as e:
                    logger.debug(f"分析题目结果时出错: {e}")
            
            # 如果没有通过，点击重新考试
            if result_text == "fail" or not question_items:
                retry_button = self.driver.find_element(By.XPATH, "//input[@value='重新考试']")
                retry_button.click()
                logger.info("点击重新考试")
                time.sleep(3)
            
            return False
            
        except Exception as e:
            logger.error(f"分析结果时出错: {e}")
            return False
    
    def build_question_bank(self):
        """通过多次尝试构建题库"""
        logger.info("开始构建题库...")
        
        max_attempts = 10  # 最多尝试10次
        attempt = 0
        
        while attempt < max_attempts:
            attempt += 1
            logger.info(f"第 {attempt} 次尝试考试...")
            
            # 参加考试
            if not self.take_exam():
                logger.error("考试失败")
                return False
            
            # 分析结果
            if self.analyze_result():
                logger.info("考试通过！")
                return True
            
            # 更新题库（这里需要实现根据结果更新题库的逻辑）
            # 由于结果页面没有正确答案，我们需要在下次考试时尝试不同的答案
            # 我们可以记录每个题目的错误答案，然后排除它们
            
            time.sleep(1)
        
        logger.error(f"超过最大尝试次数 ({max_attempts})")
        return False

def main():
    # 初始化浏览器
    driver = webdriver.Chrome()
    
    try:
        # 假设已经登录并打开了考试页面
        # driver.get("考试页面URL")
        
        auto_exam = AutoExam(driver)
        
        # 开始自动考试
        success = auto_exam.build_question_bank()
        
        if success:
            logger.info("自动考试成功完成！")
        else:
            logger.error("自动考试失败")
            
    finally:
        # driver.quit()
        pass

if __name__ == "__main__":
    main()