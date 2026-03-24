
# scraper.py의 데이터를 구글시트에 기존건 빼고 새것만 추가.

# 1. 인증: 구글 key(JSON)으로 시트 접속 권한을 얻음.
# 2. 자동화: 오늘 날짜로 시트 이름을 만들거나, 없는 시트는 새로 자동 생성함.
# 3. 지능형 저장: (= 중복방지) 시트 내용을 미리 읽어와서 똑같은 내용은 건너뜀.
# 4. 마무리: '새로 추가된 데이터'만 append_rows()로 한 번에 전송함.


import datetime
import gspread
from google.oauth2.service_account import Credentials


def get_client(keyfile: str):
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = Credentials.from_service_account_file(keyfile, scopes=scopes)
    return gspread.authorize(creds)


def save_to_sheet(               # : str :int = type hint
    url: str,                    # : 실제값 입력은 실행파일에서 진행
    keyfile: str,
    spreadsheet_name: str,
    data: list,
    sheet_name: str = None,
    header: list = None
):
    """
    구글 시트 저장 함수 (재사용 가능)

    Args:
        keyfile (str): 서비스 계정 키 경로
        spreadsheet_name (str): 스프레드시트 이름
        data (list): 저장할 데이터
        sheet_name (str): 시트 이름 (None이면 오늘 날짜)
        header (list): 헤더
    """

    if not data:                # data도 실행파일에서 여기로 보내라고 지시됨
        print("❌ 데이터 없음")
        return

    client = get_client(keyfile)
    spreadsheet = client.open(spreadsheet_name)

    # 시트 이름 자동 생성
    if not sheet_name: # 시트이름이 없으면...
        sheet_name = datetime.datetime.now().strftime('%Y-%m-%d') # 2026-03-24 형태
        """     
        ② 이름이 없어서 시간 기반으로 새로 만들 때  ---> 날자 이름 자동제작  
        ① 고정된 이름이 주어졌을 때              ---> 주어진 이름 사용
        ③ 주어졌는데 정작 시트 내에는 없을 때      ---> 주어진 이름을 만들어 냄
        """

    # if not sheet_name:   ---------------------> 260326_001 형태 (같은걸 여러번 돌릴때)
    #     # 1. 오늘 날짜(260324) 접두어 만들기
    #     prefix = datetime.datetime.now().strftime('%y%m%d')
        
    #     # 2. 현재 시트들 중 오늘 날짜로 시작하는 시트가 몇 개인지 세기
    #     count = len([s for s in spreadsheet.worksheets() if s.title.startswith(prefix)])
        
    #     # 3. 최종 이름 결정 (기존 개수 + 1 해서 001, 002... 붙이기)
    #     sheet_name = f"{prefix}_{count + 1:03d}"



    try:
        worksheet = spreadsheet.worksheet(sheet_name)
        print(f"📂 지정시트: {sheet_name}")

    except gspread.exceptions.WorksheetNotFound:  # --> gspread 라이브러리가 미리 정의해둔 '에러 이름표
        worksheet = spreadsheet.add_worksheet( # 2칸
            title=sheet_name,                  # 3칸 
            rows="300",
            cols="30"
        )                                      # 2칸
        print(f"✨ 새 시트 생성: {sheet_name}")   # 2칸

        if header:     
            # 함수를 호출할 때 header=["메뉴명", "카테고리ID"] 같은 정보를 넣어줬는지 확인.
            # 제목 정보(header)를 주지 않았다면, 굳이 맨 윗줄을 채울 필요가 없어서.
            worksheet.append_row(header)
            # 방금 막 생성된 **빈 시트의 첫 번째 줄(1행)**에 제목 데이터를 한 줄 추가.
    
    existing_values = worksheet.get_all_values()
    # existing_values = [
    #     ["메뉴명", "카테고리ID"],       # [0] 헤더
    #     ["아우터", "101"],            # [1] 기존 데이터
    #     ["상의", "102"]              # [2] 기존 데이터
    # ]
    
    # 비교를 위해 기존 데이터를 '튜플의 집합(set)'으로 변환 (속도 향상)
    # 리스트는 set에 넣을 수 없으므로 tuple로 변환합니다.
    existing_set = {tuple(row) for row in existing_values}
    # existing_set = {
    #     ("메뉴명", "카테고리ID"),
    #     ("아우터", "101"),
    #     ("상의", "102")
    # }

    # 새 데이터 중에서 기존에 없는 것만 골라냅니다.
    new_data = [row for row in data if tuple(row) not in existing_set]

    # # 내부적으로는 이 로직이 압축된 것과 같습니다.
    # new_data = []
    # for row in data:                       # 1. 하나씩 꺼내서
    #     temp_tuple = tuple(row)            # 2. 튜플로 변형한 뒤
    #     if temp_tuple not in existing_set: # 3. 검문소(if)에서 검사하고
    #         new_data.append(row)           # 4. 합격자만 새 리스트로!

    # 4. 결과에 따른 업로드 실행
    if not new_data:
        print("⏭️ 모든 데이터가 이미 존재합니다. 업로드 생략.")
        return

    worksheet.append_rows(new_data)
    print(f"✅ 중복 제외 {len(new_data)}건 저장 완료! (전체 {len(data)}건 중)")

  


#  **[입구 컷] → [접속/시트 준비] → [검문소(중복 제거)] → [최종 저장]**의 단계로 나뉩니다.
#  ---> 결국, 새것만 추가하는 코드. 매일 확인해서 며칠이나 배너에 뜨는지를 확인해야 인기, 주력상품을 알아낼수 있는거 아닌가 ?
#  ---> 제미나이에 해뒀음
 
#  🌊 데이터 변형 및 이동 순서도
#  📦 단계별 데이터 변신 과정 (실제 예시)
#  사용자가 **[['상의', '101'], ['신발', '105']]**라는 데이터를 넣었다고 가정해 봅시다.
#  1단계: 입구 컷 (Validation)데이터: [['상의', '101'], ['신발', '105']]
#        동작: if not data: 조건문이 데이터가 비었는지 확인합니다. 내용물이 있으니 통과!
 
#  2단계: 접속 및 시트 준비동작: get_client로 받은 권한으로 스프레드시트를 엽니다.
#        시트 이름 결정: 이름을 안 줬다면 2026-03-24 같은 이름이 생성됩니다.
       
#        시트 생성: try-except 문을 통해 시트가 없으면 새로 만들고, 
#        header(['메뉴', '번호'])를 1행에 적습니다.

#  3단계: 기존 데이터 읽기 및 변환 (가장 중요한 구간!)
#        기존 시트 내용 (existing_values):[['메뉴', '번호'], ['상의', '101']] (리스트 형태)
#        초고속 검색 주머니 (existing_set):리스트는 검색이 느리므로 튜플로 묶어 **세트(set)**에 담습니다.
#        결과: { ('메뉴', '번호'), ('상의', '101') }
       
#  4단계: 새 데이터 검문 (Filtering)이제 새로 가져온 data의 항목들을 하나씩 꺼내서 위 주머니(existing_set)와 비교
#        ('상의', '101')을 꺼냄 → "주머니에 있네?" → 탈락(제외)
#        ('신발', '105')를 꺼냄 → "주머니에 없네!" → 합격(new_data에 추가)

#  5단계: 최종 저장new_data: [['신발', '105']] (합격자 명단)
#        동작: append_rows(new_data) 명령으로 구글 시트의 기존 데이터 아래에 딱 한 줄만 추가됩니다.
       

#  💡 요약: 
#     데이터 형태특징코드 내 역할리스트 []수정이 자유롭고 다루기 쉬움처음에 데이터를 수집하고 담아올 때 사용
#     튜플 ()내용 수정 불가 (고체 상태)set 주머니에 넣기 위해 데이터를 딱딱하게 굳힘세트 {}검색 속도가 광속임
#     수만 개의 기존 데이터 중 중복이 있는지 찾을 때 사용