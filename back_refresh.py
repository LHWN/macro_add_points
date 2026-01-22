from appium import webdriver
# from appium.options.ios import XCUITestOptions
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import quote_plus
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import subprocess, platform, time
from control_chrome import search_answer 
from selenium import webdriver
from time import sleep
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from appium.options.ios import XCUITestOptions
from appium import webdriver
from selenium.webdriver.common.options import ArgOptions




# 1. 껍데기만 있는 옵션 객체 생성
options = ArgOptions()

# 2. 모든 capability를 직접 'appium:' 접두사와 함께 추가
# 이 방식은 automationName이 중복으로 생기는 것을 방지합니다.
caps = {
    "platformName": "iOS",
    "appium:automationName": "XCUITest",
    "appium:platformVersion": "18.7.2",
    "appium:deviceName": "iPhone",
    "appium:udid": "00008110-000179163A89A01E",
    "appium:bundleId": "com.cashwalk.cashdoc",
    "appium:noReset": True,
    "appium:useNewWDA": False,
    "autoDismissAlerts": False,
}

for key, value in caps.items():
    options.set_capability(key, value)

# 3. 실행
driver = webdriver.Remote("http://127.0.0.1:4723", options=options)


## 충돌나면 실행
## rm -rf ~/Library/Developer/Xcode/DerivedData/*
# driver = webdriver.Remote("http://localhost:4723", options=options)

wait = WebDriverWait(driver, 10)
def back_refresh():
# while True:

    previous_btn = wait.until(
        EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, 'BackButton'))
    )
    previous_btn.click()
    # 용돈퀴즈 버튼 클릭
    money_quiz_button = wait.until(
    lambda d: d.find_element(AppiumBy.ACCESSIBILITY_ID, "용돈퀴즈 용돈퀴즈")  # Accessibility ID 정확히 확인
    )
    money_quiz_button.click()

    print("용돈퀴즈 클릭")

    text_field = wait.until(
        EC.element_to_be_clickable((AppiumBy.XPATH, "//XCUIElementTypeCollectionView/XCUIElementTypeCell[1]//XCUIElementTypeStaticText"))
    )
    quiz_text = text_field.get_attribute("label")
    print(quiz_text)

    # target_words = ["광명점"]

    # if not any(word in quiz_text for word in target_words):
    #     break

    sleep(2)