# 간단 사용법:
# 간단 사용법:
# 1) 필요한 패키지: python3 -m pip install selenium webdriver-manager
# 2) macOS에서 실행
from urllib.parse import urljoin, urlparse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time


def get_chrome_service():
    try:
        # webdriver-manager가 설치되어 있으면 자동으로 드라이버 설치/사용
        from webdriver_manager.chrome import ChromeDriverManager
        return ChromeService(ChromeDriverManager().install())
    except Exception:
        # 로컬 chromedriver 후보 경로 (Mac)
        candidates = [
            "/opt/homebrew/bin/chromedriver",
            "/usr/local/bin/chromedriver",
            "/usr/bin/chromedriver",
        ]
        for p in candidates:
            if os.path.exists(p):
                return ChromeService(p)
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

def search_answer(wait_seconds=20, keep_open=False, quiz_name=None):
    event_id2 = "pass"
    search_url = "https://cashdoc.me/hospitalevent/search?keyword=" + quiz_name
    opts = webdriver.ChromeOptions()
    # opts.add_argument("--start-maximized")
    opts.add_argument("--window-size=400,300")
    opts.add_argument("--window-position=1500,900")

    # 필요시 세션 유지하려면 아래 주석 해제하고 경로 변경
    # opts.add_argument("--user-data-dir=/Users/<you>/Library/Application Support/Google/Chrome")

    chrome_bin = get_chrome_binary()
    if chrome_bin:
        opts.binary_location = chrome_bin

    service = get_chrome_service()
    driver = webdriver.Chrome(service=service, options=opts)

    try:
        driver.set_page_load_timeout(30)
        driver.get(search_url)

        wait = WebDriverWait(driver, wait_seconds)
        container_xpath = '//*[@id="__next"]/div/div/div/div/div/div[2]/div[3]/div'

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
                # 상대 XPath로 제목 div 선택 (구조: .../a/.../div[1]/div[1]/div)
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
                print(f"[{i}] {title}")
                titles.append(title)

                # 돌면서 찾는 이벤트랑 비교
                if quiz_name and title == quiz_name:
                    print(f"정답 발견! item[{i}] 제목:", title)

                    path = urlparse(link_href).path
                    parts = [p for p in path.split('/') if p]
                    
                    try:
                        idx = parts.index('eventdetail')
                        event_id2 = parts[idx + 1]
                    except ValueError:
                        pass
                    
                    # time.sleep(1)
                    break
                    # try:
                    #     driver.execute_script("window.location.href = arguments[0];", link)
                    #     time.sleep(3)
                    #     print("링크 이동 완료")

                    # except Exception as e:
                    #     print("정답 항목 클릭 실패:", e)
                    # break
            except Exception as e:
                print(f"item[{i}] 추출 실패:", e)
                titles.append("")
    finally:
        if not keep_open:
            driver.quit()
    return event_id2

if __name__ == "__main__":
    ok = search_answer(wait_seconds=20, keep_open=False)
    print("done:", ok)

