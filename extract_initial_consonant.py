from urllib.parse import urljoin, urlparse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

category_map = {
    "맛집・카페": "90",
    "취미생활": "50",
    "놀거리": "30",
    "명소": "100",
    "아이와함께": "60"
}

def get_event_store(quiz_contents):
    match = re.search(r'\d+\.\s+(.*?)\s+클릭', quiz_contents)

    if match:
        # 그룹(1) 즉, (.*?) 부분만 가져옵니다.
        event_store = match.group(1)
        print(f"추출 성공: {event_store}")
    else:
        # 패턴이 맞지 않을 경우 (예: "클릭"이 없거나 형식이 다를 때)
        print("패턴을 찾을 수 없습니다.")
    return event_store
    
    
def get_event_category(quiz_contents):
    match = re.search(r'\[([^\]]+)\]\s*카테고리', quiz_contents)

    if match:
        # 그룹(1) 즉, (.*?) 부분만 가져옵니다.
        category = match.group(1)
        print(f"추출 성공: {category}")
    else:
        # 패턴이 맞지 않을 경우 (예: "클릭"이 없거나 형식이 다를 때)
        print("패턴을 찾을 수 없습니다.")
    return category

def get_event_initial_consonant(quiz_contents):
    match = re.search(r'\[([ㄱ-ㅎ]+)\]', quiz_contents.split('4.')[-1])

    if match:
        target_initials = match.group(1)
        print(f"🎯 추출 초성: {target_initials}")
    else:
        print("초성을 찾지 못했습니다.")
    return target_initials


def get_chosung(text):
    INITIAL_CONSONANT_LIST = [
        'ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 
        'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ'
    ]
    
    result = []
    for char in text:
        # 한글 음절의 유니코드 시작은 0xAC00(가), 끝은 0xD7A3(힣)
        if '가' <= char <= '힣':
            # 한글 유니코드 공식: (초성 * 21 + 중성) * 28 + 종성 + 0xAC00
            char_code = ord(char) - 0xAC00
            chosung_index = char_code // 588
            result.append(INITIAL_CONSONANT_LIST[chosung_index])
        else:
            # 한글이 아닌 경우(숫자, 영어, 공백 등) 그대로 유지
            result.append(char)
            
    return "".join(result)

def get_naver_places(event_store, event_category):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    try:
        # 네이버 검색창으로 이동 (검색어가 포함된 URL)
        url = f"https://search.naver.com/search.naver?query={event_store}"
        driver.get(url)
        time.sleep(2) # 로딩 대기

        # 2. 검색 결과에서 장소 제목 클릭 
        # (보통 플레이스 결과의 제목은 'L_v_Y' 또는 관련 클래스명을 가집니다. 
        # 가장 확실한 건 텍스트로 찾는 것입니다.)
        try:
            # 검색 결과 중 해당 장소 이름을 가진 요소를 찾아 클릭
            wait = WebDriverWait(driver, 10)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-loc_plc-doc-id]")))

            # 2. 모든 요소를 리스트로 가져오기 (1개여도 리스트로 들어옴)
            place_items = driver.find_elements(By.CSS_SELECTOR, "div[data-loc_plc-doc-id]")

            print(f"발견된 장소 개수: {len(place_items)}")
            place_ids = []

            for item in place_items:
                # 2. 항목 내에서 장소 이름이 적힌 요소의 텍스트 추출
                # .YwYLL 클래스나 mark 태그 등을 활용
                try:
                    place_name = item.find_element(By.CSS_SELECTOR, ".place_bluelink").text
                    print(place_name)
                    # 3. 변수 event_store와 일치하는지 비교 (공백 제거 후 비교 추천)
                    if place_name.strip() == event_store.strip():
                        target_id = item.get_attribute("data-loc_plc-doc-id")
                        print(f"✅ 일치하는 장소 발견! ID: {target_id}")
                        break
                except:
                    continue
                
            if not target_id:
                print(f"❌ '{event_store}'와 일치하는 요소를 찾지 못했습니다.")

        except Exception as e:
            print(f"place 검색 불가: {e}")
            return None
        
        filter = category_map.get(event_category, "unknown")
        # place 에서 검색
        url = f"https://m.place.naver.com/place/{target_id}/around?filter={filter}"   
        driver.get(url)
        time.sleep(2) # 로딩 대기
        elements = driver.find_elements(By.CSS_SELECTOR, "span.xBZDS")

        # 2. 텍스트만 추출하여 리스트로 만듭니다.
        place_names = [el.text.strip() for el in elements if el.text.strip()]
        print(place_names)

    finally:
        driver.quit()

    return place_names



def get_initial_consonant(naver_place):
    INITIAL_CONSONANT_LIST = [
        'ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 
        'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ'
    ]

    result = []
    for char in naver_place:
        # 한글 음절의 유니코드 시작은 0xAC00(가), 끝은 0xD7A3(힣)
        if '가' <= char <= '힣':
            # 한글 유니코드 공식: (초성 * 21 + 중성) * 28 + 종성 + 0xAC00
            char_code = ord(char) - 0xAC00
            chosung_index = char_code // 588
            result.append(INITIAL_CONSONANT_LIST[chosung_index])
        else:
            # 한글이 아닌 경우(숫자, 영어, 공백 등) 그대로 유지
            result.append(char)
            
    return ("".join(result)).replace(" ", "")

    
def solve_quiz_by_initial_consonant(quiz_contents, event_store):
    # event_store = get_event_store(quiz_contents)
    event_category = get_event_category(quiz_contents)
    event_initial_consonant = get_event_initial_consonant(quiz_contents)
    place_names = get_naver_places(event_store, event_category)

    for name in place_names:
        # 각 이름의 초성을 추출 (함수 호출)
        current_initials = get_initial_consonant(name)
        print(f"비교 중: {name} ({current_initials})") # 디버깅용 출력
        
        # 3. 추출된 초성이 내가 찾는 것과 일치하면
        if current_initials == event_initial_consonant:
            found_place = name
            print(f"🎯 찾았습니다! 일치하는 장소: {found_place}")
            return found_place


if __name__ == "__main__":
    quiz_contents = '1. 좋은아침한의원 구로디지털점 클릭 2. [주변] 탭 클릭 3. [놀거리] 카테고리 클릭 4. [ㄲㅁㅇㄷㅅㄱ]인 장소를 찾아 정답 입력(띄어쓰기X) '
    event_store = get_event_store(quiz_contents)
    event_category = get_event_category(quiz_contents)
    event_initial_consonant = get_event_initial_consonant(quiz_contents)
    place_names = get_naver_places(event_store, event_category)

    print("테스트")
    test = event_store+event_initial_consonant
    print(test)
    for name in place_names:
        # 각 이름의 초성을 추출 (함수 호출)
        current_initials = get_initial_consonant(name)
        
        print(f"비교 중: {name} ({current_initials})") # 디버깅용 출력
        
        # 3. 추출된 초성이 내가 찾는 것과 일치하면
        if current_initials == event_initial_consonant:
            found_place = name
            print(f"🎯 찾았습니다! 일치하는 장소: {found_place}")
            break

# # 실행 결과
# word = "중앙공원"
# print(get_initial_consonant(word))  # 출력: ㅈㅇㄱㅇ
