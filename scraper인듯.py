
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
    a_tag = "a",
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
    # 공유 메모리( /dev/shm, 보통 64MB)가 아닌, SSD의 가상메모리 사용지시

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

        print(f"⏳ 로딩 대기: {wait_time}초")
        time.sleep(wait_time)

        parent = driver.find_element(By.CSS_SELECTOR, parent_selector)

        # print("--- 부모 요소 HTML ---")
        # print(parent.get_attribute('outerHTML'))
        items = parent.find_elements(By.TAG_NAME, item_selector)
        # print(items)

        print(f"🔍 네비 요소 개수: {len(items)}")

        for item in items:
            # Swiper duplicate 필터링
            class_name = item.get_attribute("class")
            if "d-none" in class_name:
                continue

            try:
                a_element = item.find_element(By.TAG_NAME, a_tag)
                navitxt = a_element.get_attribute("innerText").strip()
                navihref = a_element.get_attribute("href").strip()
              
                if  navihref :
                    parsed_url = urlparse(navihref) # navihref로 변수명 통일
                    params = parse_qs(parsed_url.query)
        
                    # 3. cate_no 추출 (없으면 기본값 "#none" 사용)
                    # params.get('키', 기본값) 구조를 활용합니다.
                    cate_no = params.get('cate_no')[0] if params.get('cate_no') else "#none"
                    # cate_no_list = params.get('cate_no')
                    # if cate_no_list:
                    #     cate_no = cate_no_list[0]

                if cate_no == "#none":
                    continue

                if navitxt:
                    
                    results.append([ navitxt, cate_no])

            except Exception:
                continue

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
