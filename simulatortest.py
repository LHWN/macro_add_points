from appium import webdriver
from appium.options.ios import XCUITestOptions
import time
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import quote_plus
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import subprocess
import platform
from control_chrome import search_answer 

options = XCUITestOptions()
options.platform_name = "iOS"
options.platform_version = "18.7.2"   # ← simctl list runtimes 결과에 맞춰라
options.device_name = "iPhone 13"
options.automation_name = "XCUITest"
options.udid = "00008110-000179163A89A01E"
options.automation_name = "XCUITest"
options.bundle_id = "com.cashwalk.cashdoc"
options.no_reset = True
options.use_new_wda = False

driver = webdriver.Remote("http://localhost:4723", options=options)

wait = WebDriverWait(driver, 10)

# # 용돈퀴즈 버튼 클릭
# money_quiz_button = wait.until(
#     lambda d: d.find_element(AppiumBy.ACCESSIBILITY_ID, "용돈퀴즈 용돈퀴즈")  # Accessibility ID 정확히 확인
# )
# money_quiz_button.click()

try:
    while True:
        # 제일 위에 있는 버튼 클릭
        quiz_button = wait.until(
            EC.element_to_be_clickable((AppiumBy.XPATH, "//XCUIElementTypeCollectionView/XCUIElementTypeCell[1]"))
        )
        quiz_button.click()

        # 이벤트 이름 가져오기
        quiz_contents = driver.find_element(AppiumBy.XPATH, "//XCUIElementTypeScrollView/XCUIElementTypeOther[1]/XCUIElementTypeOther/XCUIElementTypeOther[2]/XCUIElementTypeTextView").text
        print(quiz_contents)
        # "" 사이 텍스트만 추출 (항상 큰따옴표로 감싸져 있다고 가정)
        import re
        match = re.search(r'"([^"]+)"', quiz_contents)
        quiz_name = match.group(1).strip() if match else ""
        print(quiz_name)

        # 이벤트 링크 검색 - 방법 1
        if quiz_name == "":
            quiz_answer = 100
        elif quiz_name == "":
            quiz_answer = 0
        elif quiz_name == "":
            quiz_answer = -1
        else:
            quiz_answer = None

        # 브라우저 검색 - 방법 2
        # Chrome으로 앱 전환
        # driver.activate_app("com.google.chrome.ios")
        # time.sleep(2)

        # search_url = f"https://cashdoc.me/hospitalevent/search?keyword={quote_plus(quiz_name)}"

        # print("search_url" , search_url)

        # PC의 로컬 Chrome을 열어 search_url로 이동
        def open_in_local_chrome(url):
            system = platform.system()
            if system == "Darwin":  # macOS
                subprocess.run(["open", "-a", "Google Chrome", url])
            elif system == "Windows":
                subprocess.Popen([r"C:\Program Files\Google\Chrome\Application\chrome.exe", url])
            else:  # Linux
                subprocess.Popen(["google-chrome", url])

        # open_in_local_chrome(search_url)

        # 정답 입력하기 버튼 클릭
        insert_answer = wait.until(
            EC.element_to_be_clickable((AppiumBy.XPATH, "//XCUIElementTypeStaticText[@name='정답 입력하기']"))
        )
        insert_answer.click()


        # 키워드 복사 후 정답 찾으러 가기 클릭
        go_find_answer = wait.until(
            EC.element_to_be_clickable((AppiumBy.XPATH, '//XCUIElementTypeStaticText[@name="키워드 복사 후 정답 찾으러 가기"]'))
        )
        go_find_answer.click()



        driver.activate_app("com.cashwalk.cashdoc")

        # 정답 입력하기 버튼 클릭
        insert_answer = wait.until(
            EC.element_to_be_clickable((AppiumBy.XPATH, "//XCUIElementTypeStaticText[@name='정답 입력하기']"))
        )
        insert_answer.click()

        # 정답 찾아오기
        event_id = search_answer(wait_seconds=20, keep_open=False, quiz_name=quiz_name)
        answer = "https://cashdoc.me/hospitalevent/eventdetail/" + event_id

        print("정답 URL:", answer)

        # 이벤트 정답 입력
        # 이벤트 정답 입력 (텍스트 필드에 answer 넣기)
        try:
            text_field = wait.until(
                EC.element_to_be_clickable((AppiumBy.XPATH, "//XCUIElementTypeTextField[@value='띄어쓰기 없이 입력해 주세요.']"))
            )
            # 포커스 및 내용 삭제
            text_field.click()
            try:
                text_field.clear()
            except Exception:
                pass

            # 입력 시도 (send_keys 우선, 실패하면 set_value)
            try:
                text_field.send_keys(answer)
            except Exception:
                try:
                    text_field.set_value(answer)
                except Exception as e:
                    print("입력 실패:", e)

            time.sleep(0.3)

            from selenium.webdriver.common.keys import Keys
            text_field.send_keys(Keys.RETURN)
            
            # 정답 확인 버튼 클릭
            confirm_btn = wait.until(
                EC.element_to_be_clickable((AppiumBy.XPATH, '//XCUIElementTypeStaticText[@name="정답 확인"]'))
            )
            confirm_btn.click()
            
        except Exception as e:
            print("정답 입력/제출 실패:", e)

        # X 버튼 클릭 (accessibility id)
        x_btn = wait.until(
                EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, 'icCloseBlack'))
            )
        x_btn.click()


        # <- 버튼 클릭
        previous_btn = wait.until(
                EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, 'icCPQBackBlack'))
            )
        previous_btn.click()
finally:
    # 안전 종료
    try:
        driver.quit()
    except Exception:
        pass




