
def get_initial_consonant(text):
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


# 실행 결과
word = "중앙공원"
print(get_initial_consonant(word))  # 출력: ㅈㅇㄱㅇ
