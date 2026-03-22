
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
    if not sheet_name:
        sheet_name = datetime.datetime.now().strftime('%Y-%m-%d')
        """     
        ② 이름이 없어서 시간 기반으로 새로 만들 때, 
        ① 고정된 이름이 주어졌을 때,
        ③ 주어졌는데 정작 시트 내에는 없을 때
        """
    try:
        worksheet = spreadsheet.worksheet(sheet_name)
        print(f"📂 지정시트: {sheet_name}")

    except gspread.exceptions.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(
            title=sheet_name,
            rows="300",
            cols="30"
        )
        print(f"✨ 새 시트 생성: {sheet_name}")

        if header:
            worksheet.append_row(header)
    
    existing_values = worksheet.get_all_values()
    # existing_values = [
    #     ["메뉴명", "카테고리ID"],       # [0] 헤더
    #     ["아우터", "101"],              # [1] 기존 데이터
    #     ["상의", "102"]                 # [2] 기존 데이터
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

  