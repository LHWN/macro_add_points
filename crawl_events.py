import time, os
from selenium import webdriver
# 바로 아래 줄이 핵심입니다!
from selenium.webdriver.chrome.options import Options 
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By  # 나중에 요소를 찾을 때 필요합니다.
from urllib.parse import urljoin, urlparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def get_chrome_driver():
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--remote-allow-origins=*")
    # 메모리 부족으로 인한 충돌 방지
    chrome_options.add_argument("--disable-gpu")
    # chrome_options.add_argument("--headless") # 창 없이 실행하려면 주석 해제
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def get_chrome_service():
    try:
        # webdriver-manager가 설치되어 있으면 자동으로 드라이버 설치/사용
        from webdriver_manager.chrome import ChromeDriverManager
        return Service(ChromeDriverManager().install())
    except Exception:
        # 로컬 chromedriver 후보 경로 (Mac)
        candidates = [
            "/opt/homebrew/bin/chromedriver",
            "/usr/local/bin/chromedriver",
            "/usr/bin/chromedriver",
        ]
        for p in candidates:
            if os.path.exists(p):
                return Service(p)
        raise RuntimeError("chromedriver를 찾을 수 없습니다. webdriver-manager 설치하거나 chromedriver를 설치하세요.")

def get_chrome_binary():
    # macOS 기본 Chrome 경로들
    candidates = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    return None

def crawl_events(wait_seconds=20, keep_open=False):
    opts = webdriver.ChromeOptions()
    opts.add_argument("--start-maximized")

    chrome_bin = get_chrome_binary()
    if chrome_bin:
        opts.binary_location = chrome_bin

    service = get_chrome_service()
    driver = webdriver.Chrome(service=service, options=opts)
    driver.get("https://cashdoc.me/hospitalevent/eventlist?tab_id=400")

    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        # 2. 브라우저의 맨 아래로 스크롤 이동
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # 3. 새로운 콘텐츠가 로드될 때까지 대기 (네트워크 속도에 따라 조절)
        time.sleep(2)

        # 4. 스크롤 후 새로운 페이지 높이를 측정
        new_height = driver.execute_script("return document.body.scrollHeight")

        # 5. 이전 높이와 새로운 높이가 같다면 (더 이상 내려갈 곳이 없다면) 종료
        if new_height == last_height:
            print("✅ 모든 콘텐츠 로드 완료")
            break
            
        last_height = new_height
        print("⏳ 추가 콘텐츠 로딩 중...")

    # 필요시 세션 유지하려면 아래 주석 해제하고 경로 변경
    # opts.add_argument("--user-data-dir=/Users/<you>/Library/Application Support/Google/Chrome")

    try:
        wait = WebDriverWait(driver, wait_seconds)
        container_xpath = '//*[@id="__next"]/div/div/div/div[2]/div/div[3]/div[2]/div'

        try:
            wait.until(EC.presence_of_element_located((By.XPATH, container_xpath)))
        except Exception as e:
            print("컨테이너 로드 실패:", e)
            return False

        # 부모 컨테이너 아래의 각 아이템 요소 선택
        items = driver.find_elements(By.XPATH, f"{container_xpath}//div[contains(@class,'mui-css-1ofqig9')]")
        if not items:
            print("결과 아이템이 없습니다.")
            return False

        # 각 아이템에서 제목 추출 (우선 내부 div 텍스트, 없으면 img@alt 사용)
        titles = []
        for i, item in enumerate(items):
            
            try:
                anchor = item.find_element(By.CSS_SELECTOR, "a")
                title_el = anchor.find_element(By.XPATH, ".//div[contains(@style,'font-size:15px') or contains(@style,'font-size: 15px')]")
                title = title_el.text.strip()

                # title_el = item.find_element(By.XPATH, ".//a//div/div[1]/div[1]/div")
                # title = title_el.text.strip()
                # link_href = item.find_element(By.XPATH, '//*[@id="__next"]/div/div/div/div/div/div[2]/div[3]/div/div[2]/div[1]/a').get_attribute("href")
                link_href = anchor.get_attribute("href")
            except Exception:
                title = ""

            # if not title:
            #     # fallback: 이미지 alt 속성
            #     try:
            #         img = item.find_element(By.XPATH, ".//a//img")
            #         title = (img.get_attribute("alt") or "").strip()
            #     except Exception:
            #         title = ""

            # 이벤트 제목만 뽑음
            title = " ".join(line.strip() for line in title.splitlines() if line.strip())
            # print(f"[{i}] {title}")

            
            path = urlparse(link_href).path
            parts = [p for p in path.split('/') if p]
            
            
            try:
                idx = parts.index('eventdetail')
                event_id2 = parts[idx + 1]
            except ValueError:
                pass
            url = "https://cashdoc.me/hospitalevent/eventdetail/" + event_id2

            
            
            print(f"\"{title}\": \"{url}\",")

    finally:
        if not keep_open:
            driver.quit()
    

if __name__ == "__main__":
    ok = crawl_events(wait_seconds=20, keep_open=False)
    print("done:", ok)

