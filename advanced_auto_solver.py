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
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException
from datetime import datetime
from extract_initial_consonant import solve_quiz_by_initial_consonant, get_event_store, get_event_initial_consonant
import signal
import sys
from constants_event import LINK_QUIZ_MAPPING
from constants_store import INITIAL_CONSONANT_QUIZ_MAPPING

##
## 연결 끊겼을 떄
## 1. rm -rf /Users/lhwn/Library/Developer/Xcode/DerivedData/WebDriverAgent-*
## 2. 빌드 클린
## 3. 빌드
##

## 가상환경 on
# source venv/bin/activate

## cron kill
# pkill -f advanced_auto_solver.py

# 1. 껍데기만 있는 옵션 객체 생성
options = XCUITestOptions()
options.platform_name = "iOS"
options.automation_name = "XCUITest"
options.udid = "00008110-000179163A89A01E" # 사용자님의 UDID
options.bundle_id = "com.cashwalk.cashdoc"

# 꼬임 방지 핵심 옵션 3개
options.set_capability("appium:usePrebuiltWDA", True)
options.set_capability("appium:useNewWDA", False)
options.set_capability("appium:platformVersion", "18.7")
options.set_capability("appium:wdaLocalPort", 8100)

driver = webdriver.Remote("http://127.0.0.1:4723", options=options)

## 충돌나면 실행
## rm -rf ~/Library/Developer/Xcode/DerivedData/*
# driver = webdriver.Remote("http://localhost:4723", options=options)

wait = WebDriverWait(driver, 3)


# # 용돈퀴즈 버튼 클릭
# money_quiz_button = wait.until(
#     lambda d: d.find_element(AppiumBy.ACCESSIBILITY_ID, "용돈퀴즈 용돈퀴즈")  # Accessibility ID 정확히 확인
# )
# money_quiz_button.click()

# 퀴즈 목록
# (//XCUIElementTypeImage[@name="imgLivequiz"])[1]

def solve_quiz():
    start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    answer = None
    sequence = 1
    find_count = 0
    search_count = 0

    try:
        while True:
            rohasel = False
            try:
                result = check_quiz_isAvailabe()
            except Exception as e:
                print(f"퀴즈 확인 중 오류 발생: {e}")
                continue
            print(f"목록에서 가져온 이벤트명 : {result}")



            if result:
                try:
                    quiz_button = wait.until(
                            EC.element_to_be_clickable((AppiumBy.XPATH, f"//XCUIElementTypeCollectionView/XCUIElementTypeCell[{sequence}]/XCUIElementTypeOther"))
                            # 순서 지정
                            # EC.element_to_be_clickable((AppiumBy.XPATH, f"//XCUIElementTypeCollectionView/XCUIElementTypeCell[2]"))
                    )
                    quiz_button.click()
                except Exception:
                    # 퀴즈 상세 못빠져나가면 빠져나가기
                    previous_btn = driver.find_elements(AppiumBy.ACCESSIBILITY_ID, "icCPQBackBlack")
                    if previous_btn:
                        previous_btn[0].click()
            
                # 이벤트 내용 전체
                quiz_contents = driver.find_element(AppiumBy.XPATH, "//XCUIElementTypeScrollView/XCUIElementTypeOther[1]/XCUIElementTypeOther/XCUIElementTypeOther[2]/XCUIElementTypeTextView").text
                
                # "" 사이 이벤트 이름만 추출
                import re
                match = re.search(r'"([^"]+)"', quiz_contents)
                quiz_name = match.group(1).strip() if match else ""

                print("퀴즈 내용 전체:", quiz_contents)
                print("[", sequence, "] quiz_name", quiz_name)   

                # if quiz_name == "":
                #     print("이벤트 퀴즈 아님 sequence : ", sequence, " quiz_name : ", quiz_name)
                    
                #     previous_btn = driver.find_elements(AppiumBy.ACCESSIBILITY_ID, "icCPQBackBlack")
                #     if previous_btn:
                #         previous_btn[0].click()

                #     try:
                #         alert = driver.switch_to.alert
                #         alert_text = alert.text
                #         alert.accept()
                #         print(f"✅ 시스템 알림창 해결: {alert_text}")

                #         previous_btn = wait.until(
                #             EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, 'icCPQBackBlack'))
                #         )
                #         previous_btn.click()
                #     except Exception:
                #         # 시스템 알림이 없으면 조용히 통과
                #         pass
                #     # 1번 못풀면 2번으로 바꾸고, 2번 못풀면 1번으로 바꾸면서 계속 확인
                #     if sequence == 1:
                #         sequence = 2
                #     elif sequence == 2:
                #         sequence = 1
                #     continue


                    # 네트워크 오류 나면 처리
                    # try:
                    #     alert = driver.switch_to.alert
                    #     alert_text = alert.text  # 텍스트를 먼저 가져옴
                    #     alert.accept()
                    #     print(f"✅ 시스템 알림창 해결: {alert_text}")
                    #     previous_btn = driver.find_elements(AppiumBy.ACCESSIBILITY_ID, "icCPQBackBlack")
                    #     if previous_btn:
                    #         previous_btn[0].click()

                    # except NoAlertPresentException:
                    #     # 알림창이 없으면 그냥 아무것도 안 하고 넘어감
                    #     pass


                        

                    
                try:
                    # 정답 입력하기 버튼 클릭
                    print("정답 입력하기 버튼 클릭")
                    insert_answer = wait.until(
                        EC.element_to_be_clickable((AppiumBy.XPATH, "//XCUIElementTypeStaticText[@name='정답 입력하기']"))
                    )
                    insert_answer.click()
                except Exception:
                    print("이미 풀었음")
                    if sequence == 1:
                        previous_btn = driver.find_elements(AppiumBy.ACCESSIBILITY_ID, "icCPQBackBlack")
                        if previous_btn:
                            previous_btn[0].click()
                    elif sequence == 2:
                        print("이미 다 풀고 2번임")
                        previous_btn = driver.find_elements(AppiumBy.ACCESSIBILITY_ID, "icCPQBackBlack")
                        if previous_btn:
                            previous_btn[0].click()
                        # back_refresh()

                    if sequence == 1:
                        sequence = 2
                    elif sequence == 2:
                        sequence = 1    

                    try:
                        alert = driver.switch_to.alert
                        alert_text = alert.text
                        alert.accept()
                        print(f"✅ 알림창 감지 및 해결: {alert_text}")

                        previous_btn = driver.find_elements(AppiumBy.ACCESSIBILITY_ID, "icCPQBackBlack")
                        if previous_btn:
                            previous_btn[0].click()

                        continue
                    except:
                        continue

                print("키워드 복사 후 정답 찾으러 가기 클릭")
                try:
                    # 키워드 복사 후 정답 찾으러 가기 클릭
                    go_find_answer = wait.until(
                        EC.element_to_be_clickable((AppiumBy.XPATH, '//XCUIElementTypeStaticText[@name="키워드 복사 후 정답 찾으러 가기"]'))
                    )
                    go_find_answer.click()
                except Exception as e:
                    print(e)

                # handles = driver.window_handles
                # driver.switch_to.window(handles[-1])  # 마지막 윈도우 핸들로 전환
                # driver.close()  # 현재 윈도우 닫기
                
                try:
                    sleep(2)
                    driver.activate_app("com.cashwalk.cashdoc")

                    # 유효한 문제면 풀기
                    # 정답 입력하기 버튼 클릭
                    insert_answer = wait.until(
                        EC.element_to_be_clickable((AppiumBy.XPATH, "//XCUIElementTypeStaticText[@name='정답 입력하기']"))
                    )
                    insert_answer.click()
                except Exception as e:
                    print(e)

                answer = LINK_QUIZ_MAPPING.get(quiz_name)

                # 정답 찾아오기
                if answer is not None:
                    print("바로 찾기:", quiz_name)
                    print("바로 찾기 결과 : ", answer)
                    find_count += 1
                elif answer is None and "카테고리" in quiz_contents:
                    event_store = get_event_store(quiz_contents)
                    # event_store = result        

                    print(event_store)
                    quiz_initial_consonant = get_event_initial_consonant(quiz_contents)
                    print(quiz_initial_consonant)
                    answer = INITIAL_CONSONANT_QUIZ_MAPPING.get(event_store+quiz_initial_consonant)
                    if answer is None:
                        answer = solve_quiz_by_initial_consonant(quiz_contents)
                else:
                    print("[", sequence, "] 검색 찾기:", quiz_name)
                    # 빡치게 하는 퀴즈면
                    if quiz_name == "로하셀한의원 다이어트 뺄타임 처방":
                        event_ids = ["6431", "6479", "6433", "6435", "6478", "6660", "6432", "6478"]
                        # for event_id in enumerate(event_ids):
                        for event_id in event_ids:
                            answer = "https://cashdoc.me/hospitalevent/eventdetail/" + event_id
                            print(f"로하셀 {event_id} 시도")
                            try:
                                text_field = wait.until(
                                    EC.element_to_be_clickable((AppiumBy.XPATH, "//XCUIElementTypeTextField"))
                                )
                                text_field.click()
                                
                                # 입력 시도 (send_keys 우선, 실패하면 set_value)
                                print(answer)
                                text_field.clear()
                                text_field.send_keys(answer)
                                text_field.send_keys(Keys.RETURN)
                                # 정답이면
                                try:
                                    # X 버튼 클릭 (accessibility id)
                                    print("정답임")
                                    x_btn = wait.until(
                                            EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, 'icCloseBlack'))
                                        )
                                    x_btn.click()
                                    
                                    # <- 버튼 클릭
                                    previous_btn = wait.until(
                                            EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, 'icCPQBackBlack'))
                                        )
                                    previous_btn.click()
                                    rohasel = True 
                                except Exception as e: 
                                    # for 문만 빠져나가기 
                                    print("로하셀 정답 아님")
                                    continue
                            except Exception as e:
                                # 입력창 자체를 못 찾는 경우 (TimeoutException 등)
                                print(f"⚠️ 화면에 입력창이 없습니다. 팝업이 떠있는지 확인하세요: {e}")
                                # 여기서 팝업을 강제로 닫는 로직을 넣으면 다음 루프가 살아납니다.
                               
                        # 로하셀 찾았으면 다음 턴
                        if rohasel:
                            continue
                    else:
                        event_id = search_answer(wait_seconds=20, keep_open=False, quiz_name=quiz_name)
                        answer = "https://cashdoc.me/hospitalevent/eventdetail/" + event_id
                        print("검색 찾기 결과 : ", answer)
                    search_count += 1
                   

                print("정답:", answer)


                # 이벤트 정답 입력
                # 이벤트 정답 입력 (텍스트 필드에 answer 넣기)
                try:
                    text_field = wait.until(
                        EC.element_to_be_clickable((AppiumBy.XPATH, "//XCUIElementTypeTextField[@value='띄어쓰기 없이 입력해 주세요.']"))
                    )
                    # 포커스 및 내용 삭제
                    # text_field.click()
                    # try:
                    #     text_field.clear()
                    # except Exception:
                    #     pass

                    # 입력 시도 (send_keys 우선, 실패하면 set_value)
                    try:
                        text_field.send_keys(answer)
                    except Exception:
                        previous_btn = driver.find_elements(AppiumBy.ACCESSIBILITY_ID, "icCPQBackBlack")
                        if previous_btn:
                            previous_btn[0].click()
                        
                        try:
                            text_field.set_value(answer)
                        except Exception as e:
                            print("입력 실패:", e)

                    
                    text_field.send_keys(Keys.RETURN)


                    
                    # 정답 확인 버튼 클릭
                    # confirm_btn = wait.until(
                    #     EC.element_to_be_clickable((AppiumBy.XPATH, '//XCUIElementTypeStaticText[@name="정답 확인"]'))
                    # )
                    # confirm_btn.click()
                except Exception as e:
                    print("정답 입력/제출 실패:", e)

                # X 버튼 클릭 (accessibility id)
                x_btn = wait.until(
                        EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, 'icCloseBlack'))
                    )
                x_btn.click()

                try:
                    # <- 버튼 클릭
                    previous_btn = wait.until(
                            EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, 'icCPQBackBlack'))
                        )
                    previous_btn.click()
                except Exception:
                    # X 버튼 클릭 (accessibility id)
                    x_btn = wait.until(
                            EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, 'icCloseBlack'))
                        )
                    x_btn.click()

            # 목록에서 성형 이벤트 아니면 나갔다가 다시 들어오기
            else:
                back_refresh()
    finally:
        # 안전 종료
        try:
            print(f"바로 찾기 성공 총 {find_count}회")
            print(f"검색 찾기 성공 총 {search_count}회")
            print(f"정답 제출 성공 총 {find_count + search_count}회")
            print(f"시작 시간 : {start_time}")
            print(f"종료 시간 : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            driver.quit()
            # sleep(10)
            # continue
        except Exception:
            pass

def graceful_exit(signum, frame):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n[{now}] 외부 신호(SIGTERM/SIGINT)에 의해 프로그램이 강제 종료되었습니다.", flush=True)
    # 여기에 종료 전 수행할 작업(예: 브라우저 닫기, 파일 저장 등)을 추가할 수 있습니다.
    sys.exit(0)

signal.signal(signal.SIGTERM, graceful_exit)
signal.signal(signal.SIGINT, graceful_exit)

# 목록에서 미리 성형 이벤트인지 확인 
def check_quiz_isAvailabe():
    # 목록에서 퀴즈명 가져오기
    # text_field = wait.until(
    #     EC.element_to_be_clickable((AppiumBy.XPATH, "//XCUIElementTypeCollectionView/XCUIElementTypeCell[1]//XCUIElementTypeStaticText"))
    # )
    # quiz_text = text_field.get_attribute("label")
    for _ in range(3):  # 최대 3번 재시도
        try:
            text_field = wait.until(
                EC.element_to_be_clickable((AppiumBy.XPATH, "//XCUIElementTypeCollectionView/XCUIElementTypeCell[1]//XCUIElementTypeStaticText"))
            )
            quiz_text = text_field.get_attribute("label")
            if quiz_text:
                break  # 성공하면 루프 탈출
        except StaleElementReferenceException:
            time.sleep(0.5)  # 잠시 대기 후 다시 시도
            continue
        
    # 해당 요소의 name 속성(실제 텍스트)을 가져와서 변수에 저장
    
    print(f"찾은 텍스트는: {quiz_text}")

    return quiz_text
    
    # 목록만 보고 성형 이벤트인지 판단 힘듦
    # if "이벤트" in quiz_text:
    #     print("이벤트 포함 확인")
    #     return True
    # else:
    #     return False

def back_refresh():
    print("back_refresh 진입")

    previous_btn = wait.until(
        EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, 'icCPQBackBlack'))
    )
    previous_btn.click()
    # 용돈퀴즈 버튼 클릭
    money_quiz_button = wait.until(
    lambda d: d.find_element(AppiumBy.ACCESSIBILITY_ID, "용돈퀴즈 용돈퀴즈")  # Accessibility ID 정확히 확인
    )
    money_quiz_button.click()

    print("용돈퀴즈 클릭")

    # text_field = wait.until(
    #     EC.element_to_be_clickable((AppiumBy.XPATH, "//XCUIElementTypeCollectionView/XCUIElementTypeCell[1]//XCUIElementTypeStaticText"))
    # )
    # quiz_text = text_field.get_attribute("label")
    # print(quiz_text)

    # target_words = ["카복시", "더원츠의원", "발지압"]

    # if not any(word in quiz_text for word in target_words):
    #     break

    sleep(5)

def solve_effective_quiz(quiz_name, sequence):
    # 정답 입력하기 버튼 클릭
    insert_answer = wait.until(
        EC.element_to_be_clickable((AppiumBy.XPATH, "//XCUIElementTypeStaticText[@name='정답 입력하기']"))
    )
    insert_answer.click()

    answer = LINK_QUIZ_MAPPING.get(quiz_name)

    # 정답 찾아오기
    if answer is None:
        print("[", sequence, "] 검색 찾기:", quiz_name)
        # 빡치게 하는 퀴즈면
        if quiz_name == "로하셀한의원 다이어트 뺄타임 처방":
            
            answer = ""
        else:
            event_id = search_answer(wait_seconds=20, keep_open=False, quiz_name=quiz_name)
            answer = "https://cashdoc.me/hospitalevent/eventdetail/" + event_id
            print("검색 찾기 결과 : ", answer)
        search_count += 1
    else:
        print("바로 찾기:", quiz_name)
        print("바로 찾기 결과 : ", answer)
        find_count += 1

    print("정답 URL:", answer)

    # 이벤트 정답 입력
    # 이벤트 정답 입력 (텍스트 필드에 answer 넣기)
    try:
        text_field = wait.until(
            EC.element_to_be_clickable((AppiumBy.XPATH, "//XCUIElementTypeTextField[@value='띄어쓰기 없이 입력해 주세요.']"))
        )
        # 포커스 및 내용 삭제
        # text_field.click()
        # try:
        #     text_field.clear()
        # except Exception:
        #     pass

        # 입력 시도 (send_keys 우선, 실패하면 set_value)
        try:
            text_field.send_keys(answer)
        except Exception:
            previous_btn = driver.find_elements(AppiumBy.ACCESSIBILITY_ID, "icCPQBackBlack")
            if previous_btn:
                previous_btn[0].click()
            
            try:
                text_field.set_value(answer)
            except Exception as e:
                print("입력 실패:", e)

        
        text_field.send_keys(Keys.RETURN)


        
        # 정답 확인 버튼 클릭
        # confirm_btn = wait.until(
        #     EC.element_to_be_clickable((AppiumBy.XPATH, '//XCUIElementTypeStaticText[@name="정답 확인"]'))
        # )
        # confirm_btn.click()
    except Exception as e:
        print("정답 입력/제출 실패:", e)

    # X 버튼 클릭 (accessibility id)
    x_btn = wait.until(
            EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, 'icCloseBlack'))
        )
    x_btn.click()

    try:
        # <- 버튼 클릭
        previous_btn = wait.until(
                EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, 'icCPQBackBlack'))
            )
        previous_btn.click()
    except Exception:
        x_btn = driver.find_elements(AppiumBy.ACCESSIBILITY_ID, "icCloseBlack")
        if x_btn:
            x_btn.click()


if __name__ == "__main__":
    driver.terminate_app('com.cashwalk.cashdoc')
    time.sleep(2)
    driver.activate_app('com.cashwalk.cashdoc')

    try:
        # 최대 3초 동안만 기다려보고 있으면 클릭
        index_popup = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((AppiumBy.XPATH, '//XCUIElementTypeStaticText[@name="오늘 그만보기"]'))
        )
        index_popup.click()
        print("'오늘 그만보기' 클릭 완료")
    except TimeoutException:
        # 3초 안에 안 나타나면 그냥 무시하고 넘어감
        print("'오늘 그만보기' 버튼이 화면에 없습니다.")

    money_quiz_button = wait.until(
        lambda d: d.find_element(AppiumBy.ACCESSIBILITY_ID, "용돈퀴즈 용돈퀴즈")  # Accessibility ID 정확히 확인
    )
    money_quiz_button.click()
    # driver.get("cashdoc://moneyquiz")

    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} 프로그램 시작", flush=True)

    solve_quiz()
    