# 메뉴, 베너 스크래퍼가 각각의 함수로 분리되어 있음
# 분리 이유 : 데이터 구조의 차이
  # 메뉴 수집기: 결과가 [메뉴명, 카테고리번호] 이렇게 2개씩 묶여 나옵니다.
  # 배너 수집기: 결과가 [제목, 내용, 카테고리번호] 이렇게 3개씩 묶여 나옵니다.
  # 나중에 엑셀에 저장할 때 2개, 3개 혼란 방지 


import datetime # 달력느낌 now=datetime.datetime.now()
import time # 시간제어, time.sleep(10) # 10초 동안 프로그램을 멈추기
from selenium import webdriver # 브라우저 컨트롤 핵심
from selenium.webdriver.chrome.options import Options 
# 브라우저 초기옵션 : headless, 창크기, 보안 경고창의 점멸등

from selenium.webdriver.common.by import By
# 찾는 기준을 설정
# By.ID: 아이디 이름으로 찾기
# By.CSS_SELECTOR: 디자인 경로로 찾기
# By.TAG_NAME: HTML 태그 이름(p, div, a)으로 찾기

# 쿼리스트링의 데이터 
from urllib.parse import urlparse, parse_qs
# URL을 단어별로 쪼개는 역할

# url = "https://example.com/search?cate_no=123&item=book"
# parsed = urlparse(url)
# print(parsed.query) # 결과: "cate_no=123&item=book" (쿼리인 ? 뒤의 내용만 쏙 추출)

# parse_qs : 쿼리를 딕셔너리 형태로 정리
# query = "cate_no=123&item=book"
# params = parse_qs(query)
# print(params) # 결과: {'cate_no': ['123'], 'item': ['book']}



# 쇼핑몰 사이트에 접속해서 특정 메뉴 영역을 찾아간 뒤, 
# 그 안에 있는 모든 메뉴 아이템을 하나씩 확인하며 
# **[메뉴 이름, 카테고리 번호]**의 리스트를 만들어 반환합니다.

# 4. 이 함수의 핵심 로직 흐름
# 브라우저를 켭니다. (설정에 따라 숨기거나 보여줌)
# 입력받은 url로 접속합니다.
# parent_selector로 메뉴 뭉치를 찾고, 그 안에서 item_selector로 메뉴들을 나열합니다.
# 각 메뉴의 링크(href)에서 cate_no(카테고리 번호)를 분석해서 뽑아냅니다.
# 메뉴 이름(navitxt)과 번호를 묶어서 결과 리스트에 담습니다.


def scrape_menu_cafe24(            # :str :int = type hint
    url: str,                      
    parent_selector: str,          
    item_selector: str,
    a_tag = "a",                   # 셀레니움에서 <>는 빼는게 기본
    content_tag = "span, strong",
    
    wait_time: int = 10,
    headless: bool = True
):

# 2. 매개변수(입력값)의 의미
# 이 부분은 함수에게 "어디서, 무엇을, 어떻게 가져올지" 지시하는 가이드라인입니다.
# url: str: 수집할 쇼핑몰의 주소입니다. (예: https://myshop.com)
# parent_selector: 메뉴들을 감싸고 있는 **큰 울타리(부모 요소)**의 주소입니다. (예: #category, .menu_wrap)
# item_selector: 그 울타리 안에 있는 개별 메뉴 칸의 이름입니다. (예: li, .item)
# a_tag = "a": 클릭할 수 있는 링크 태그입니다. 보통 <a> 태그를 씁니다.
# content_tag = "span, strong": 메뉴 이름이 적혀 있는 태그입니다. 
# 보통 글자를 강조하기 위해 <span>이나 <strong>을 쓰기 때문에 기본값으로 설정되어 있습니다.
# wait_time: int = 10: 사이트가 느릴 수 있으니, 접속 후 최대 10초 동안 기다려라는 뜻입니다.
# headless: bool = True: 브라우저 창을 눈에 보이게 띄울지(False), 아니면 백그라운드에서 몰래 실행할지(True) 결정합니다.



    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")
        # head : 실제 브라우저 창, 자원소모, popup등 위험
        # "headless 옵션이 True라면, 
        # **'창 띄우지 말라는 (headless)명령어를 브라우저 설정에 추가지시"

    # 안전장치 (안멈추게)
    chrome_options.add_argument("--no-sandbox")
    # 서버가 보안용 sandbox거부 많이함 --> 아예 안씀
    chrome_options.add_argument("--disable-dev-shm-usage")
    # 공유 메모리( /dev/shm, 보통 64MB = 램부족시 스톱됨)가 아닌, SSD의 가상메모리 사용지시

    driver = webdriver.Chrome(options=chrome_options)
    results = []

    # 설계도 (Class): Options (크롬 설정은 이렇게 하는 거야! 라고 적힌 문서)
    # 실제 바구니 (Object/Instance): chrome_options (내가 지금 쓸 진짜 설정 바구니)
    # 행동 (Method): add_argument (바구니에 옵션을 추가하는 동작)

    # --headless : 브라우저 창을 띄우지 않음 (백그라운드 실행)
    # --window-size=1920,1080 : 브라우저 창의 크기를 특정 해상도로 고정
    # --start-maximized : 브라우저를 전체 화면으로 시작
    # --incognito : 시크릿 모드로 실행 (쿠키/기록 남기지 않음)
    # --disable-gpu : 그래픽 가속을 끔 (저사양 서버에서 에러 방지용)
    # --user-agent=... : 브라우저의 이름표를 바꿔서 로봇이 아닌 척함

    try:
        print(f"🌐 접속: {url}")
        driver.get(url) 
        # .get의 의미
        # 셀레니움 : driver.get(url)    브라우저를 해당 주소로 이동시켜라 (지금)
        # 딕셔너리 : params.get('key')	데이터 뭉치에서 특정 값을 꺼내와라
        # Requests 라이브러리 : requests.get(url)	화면은 안 띄우고 HTML 코드만 슥 긁어와라

        print(f"⏳ 로딩 대기: {wait_time}초")
        time.sleep(wait_time)
        # .get으로 html은 다 가져왔어도, 아직 자바스크립트가 덜 오거나, 덜 로딩되어 기다림



# --- [다음 단계 예고 메모] ---
        # 1. parent_selector로 메뉴 전체를 담고 있는 '큰 울타리' 요소 찾기 ---> # 메뉴바 #
        # 2. 그 안에서 item_selector로 '개별 메뉴'들 다 긁어오기 (find_elements)
        # 3. for 반복문 돌리면서 각 메뉴의 글자(text)와 링크(href) 추출하기
        # 4. 링크 안에서 cate_no 번호만 쏙 뽑아내기 (parse_qs 사용)


    # 목표 : 메뉴 이름, 링크, 카테고리 번호 모으기! 
    
    # 메뉴 덩어리를 잡고 (item)
    # 이름을 캐고 (navitxt)
    # 링크를 따고 (navihref)
    # 그 링크에서 (cate_no) 취득


        parent = driver.find_element(By.CSS_SELECTOR, parent_selector)
        # parent_selector를 사람이 F12등으로 찾아서 실행모듈에서 지정해 주면, 
        # driver가 css_selector로 찾아서 parent 변수에 넣음
        
        # print("--- 부모 요소 HTML ---")
        # print(parent.get_attribute('outerHTML'))
      
        # --> 디버깅 코드
        # parent라고 이름 붙인 그 구역의 **"HTML 소스코드 전체"**를 문자열로 가져오라.
        # 출력된 내용이 내가 원한 것이 아니면 ? → parent_selector 주소를 다시 따야함을 알게됨.

        # 주석을 풀면 이렇게 출력됩니다.
        # <div id="category" class="menu_wrap">
        #    <ul>
        #        <li><a href="...">상의</a></li>   <--- 이거임 
        #        <li><a href="...">하의</a></li>   <--- 이거임
        #    </ul>
        # </div>

        items = parent.find_elements(By.TAG_NAME, item_selector)
        # 실행 모듈에서 item_selector 지정해주면, TAG_NAME 기준으로 driver가 찾아옴.
        ### driver가 아니라 parent임
        # --> 이미 parent가 된 메뉴바등에서만 찾으라는 의미.
        # parent: <nav> ... </nav> (커다란 상자 1개)

        ### element가 아니라 elements임.
        # --> 메뉴바는 1개지만, 내용은 여러개라서 결과는 리스트가 됨.
        # 하나도 못찾으면 error발생이 아닌 빈리스트[]를 반환 
        # items: [ <li>1</li>, <li>2</li>, <li>3</li> ]

        # print(items) --> 디버깅 코드

        print(f"🔍 네비 요소 개수: {len(items)}")
        # --> 결과로 몇개를 찾았는지를 알려줌. 0이면 ? --> 다시 !!

        for item in items:
            # Swiper duplicate 필터링 : (양말(복제)-상의-하의-양말-상의(복제))
            class_name = item.get_attribute("class")
            if "d-none" in class_name:
                continue

            # item.get_attribute("class")를 했을 때, 
            # 해당 요소에 클래스가 아예 없으면 None을 반환할 수 있습니다.

            # 안전한 코드: class_name = item.get_attribute("class") or "" 
            # (클래스가 없으면 빈 글자로 취급)

            ## class 속성값 가져와서 중복된게 있으면 아래코드 실행없이 for-in문으로 복귀 

            # d-none이나 swiper-slide-duplicate 같은 클래스가 붙어 숨겨져 있습니다
            # 중복 방지위해서 걸러냄
            # 크롤링하려면 F12로 "이 사이트는 숨겨진 애들한테 어떤 이름표를 붙여줬지?"를 먼저 확인

            # .get_attribute("속성명")
            # 1. 출처: 셀레니움이 제공하는 웹 요소의 속성정보 추출 기능.
            # 2. 기능: 태그 안에 숨겨진 속성(class, id, href, title 등)의 실제 값을 읽어옴.
            # 3. 목적: 이 메뉴가 숨겨진 메뉴인지(d-none), 
            #         링크 주소는 무엇인지(href) 등을 판단하는 근거로 사용함.


            # id : 고유한 이름표, 한 페이지에 한번만 사용, 메뉴바(parent) 같은 큰 구역을 찾을 때 최고!
            #      CSS 기호: # (예: #category, #login-btn)
            # class: 그룹/상태이름, d-none 같은 **필터링(가짜 거르기)**에 필수!
            #      CSS 기호: . (예: .menu_item, .d-none)
            # href : 이동할 주소, 카테고리의 실제 상세 URL을 수집할 때 필수!
            #      주로 <a> (Anchor) 태그에서 사용
            # title : 보조 설명, 메뉴 이름이 이미지일 때 글자 정보를 대신 캘 때 사용.
            #      작은 풍선 도움말


            try:
                a_element = item.find_element(By.TAG_NAME, a_tag)
                # a_tag : 변수, 위의 함수에 'a'로 지정되어 있음
                navitxt = a_element.get_attribute("innerText").strip() # --> 메뉴이름
                # innerText : 꾸며진 text도 잘 가져옴
                # .strip() : 공백제거 -> text만 남김
                navihref = a_element.get_attribute("href").strip() # --> 메뉴주소

                # --> 버튼(a)찾고, 메뉴이름 찾고, 누르면 가는 주소까지 찾아뒀음

                if  navihref :
                    parsed_url = urlparse(navihref) # navihref로 변수명 통일
                    # urlparse(navihref): 긴 URL을 도메인, 경로, 쿼리(파라미터) 등으로 조각조각 나눕니다.

                    params = parse_qs(parsed_url.query)
                    # parse_qs(parsed_url.query)
                    # : 주소창의 ? 뒤에 붙는 정보들(예: cate_no=24&sort=1)을 사전형태로 변환.
                    # 결과물 예시: {'cate_no': ['24'], 'sort': ['1']}
        
                    # 3. cate_no 추출 (없으면 기본값 "#none" 사용)
                    # params.get('키', 기본값) 구조를 활용합니다.
                    cate_no = params.get('cate_no')[0] if params.get('cate_no') else "#none"
                    # cate_no_list = params.get('cate_no')
                    # if cate_no_list:
                    #     cate_no = cate_no_list[0]
                    # 삼항연산자 : 위의 3줄을 한줄로

                    # params.get('cate_no') → 결과: ['24'] (리스트)
                    # params.get('cate_no')[0] → 결과: '24'(리스트의 0번 인덱스, 즉 첫 번째만)

    # 메뉴 이름은 "상의", "TOP"처럼 운영자가 바꿀 수 있지만, 
    # **cate_no**는 DB에서 변하지 않는 고유 식별자

    # 이제 메뉴 이름, 링크, 카테고리 번호까지 다 모았네요! 


                if cate_no == "#none":
                    continue

                if navitxt:
                    
                    results.append([ navitxt, cate_no])

            except Exception:
                continue # ''멈추지말고'' 다음으로 컨티뉴 
            # ===> 어떤 에러가 나더라도 멈추지말고 다음으로 진행
            
    finally:
        driver.quit()

    return results


def scrape_banners_swiper_cafe24(
    url: str,
    parent_selector: str,
    item_selector: str,
    title_tag = "p",
    content_tag = "span",
    
    wait_time: int = 10,
    headless: bool = True
):
    """
    범용 배너 스크래핑 함수

    Args:
        url (str): 접속 URL
        parent_selector (str): 부모 영역 CSS selector
        item_selector (str): 개별 아이템 selector (class or css)
        title_tag (str): 제목 태그
        content_tag (str): 내용 태그
        link_tag: 링크값(카테고리확인하기위해서)
        wait_time (int): 로딩 대기 시간
        headless (bool): 헤드리스 모드 여부

    Returns:
        list: [[수집시간, 제목, 내용], ...]
    """

    chrome_options = Options()
    # if headless:
    #     chrome_options.add_argument("--headless")

    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)
    results = []

    try:
        print(f"🌐 접속: {url}")
        driver.get(url)

        print(f"⏳ 로딩 대기: {wait_time}초")
        time.sleep(wait_time)

        parent = driver.find_element(By.CSS_SELECTOR, parent_selector)
        items = parent.find_elements(By.CLASS_NAME, item_selector)

        print(f"🔍 요소 개수: {len(items)}")

        for item in items:
            # Swiper duplicate 필터링
            class_name = item.get_attribute("class")
            if "duplicate" in class_name:
                continue

            try:
                title = item.find_element(By.TAG_NAME, title_tag).get_attribute("innerText").strip()
                content = item.find_element(By.TAG_NAME, content_tag).get_attribute("innerText").strip()
                if item.tag_name == 'a' :
                    href = item.get_attribute("href").strip()

                    # item_selector로 잡힌 태그가 반드시 <a>일 때만 링크를 가져오게 되어 있습니다. 
                    # 만약 배너 구조가 <li><a href="...">...</a></li> 처럼 <li>가 아이템이고 
                    # 그 안에 <a>가 들어있는 구조라면, 
                    # 메뉴 스크래퍼처럼 item.find_element(By.TAG_NAME, "a") 과정을 한번 거치는 것이 더 안전.


                    if href :
                        # 1. URL 분석 (Parse)
                        parsed_url = urlparse(href)
                        # 2. 쿼리 스트링 추출 (? 뒤의 내용들을 딕셔너리 형태로 변환)
                        params = parse_qs(parsed_url.query)
                        cate_no = params.get('cate_no', [None])[0]
                else :
                    cate_no = "#none"

                if title:
                    
                    results.append([ title, content, cate_no])

            except Exception:
                continue

    finally:
        driver.quit()

    return results
