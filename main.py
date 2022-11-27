## project MiniOtter

import re
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os 
from config import Config
import openpyxl as op 

url = 'https://www.ssg.com/' 
r = requests.get(url)

if r.status_code == 200:
    html = r.text
    soup = BeautifulSoup(html, 'html.parser')

else : 
    print(r.status_code)

events = soup.find_all(class_ = 'ssghero_slide_col')
event_ls = [] 
for event in events : 
    try : 
        link = event.find(href=True)["href"]
        if "nevntId" in link : 
            event_ls.append(event)
        # 확실하게 event인 거만 뽑아내기 (프로모션 없는 단순 제품 나열형 기획전 제외 -> 코드가 다름) 
    except : 
        continue

df = pd.DataFrame()
for event in event_ls : 
    
    #기본정보
    titlemain = event.find(class_ = 'ssghero_titmain').text
    titlesub = event.find(class_ = 'ssghero_titsub').text
    link = event.find(href=True)["href"]

    sub_url = link
    r2 = requests.get(sub_url)

    if r2.status_code == 200:
        html = r2.text
        soup = BeautifulSoup(html, 'html.parser')

    else : 
        print(r2.status_code)
    # title, date 
    try : 
        evt_title = soup.find(class_ = 'etxt')
        evt_title = evt_title.text
    except :
        evt_title = soup.find(class_ = 'cevent_subject_tit')
        evt_title = evt_title.text

    try :
        evt_date = soup.find(class_ = 'edays')
        p = re.compile('[0-9]{4}.[0-9]{2}.[0-9]{2}')
        evt_date = p.findall(evt_date.text)

    except :
        evt_date = soup.find(class_ = 'cevent_data_term')
        p = re.compile('[0-9]{4}.[0-9]{2}.[0-9]{2}')
        evt_date = p.findall(evt_date.text)

    if len(evt_date) == 2 :
        evt_start_dt = evt_date[0]
        evt_end_dt = evt_date[1]
    elif len(evt_date) == 1 :
        evt_start_dt = evt_date[0]
        evt_end_dt = evt_date[0]
    

    # evt_mall 
    # 2. 대상 샵 -> 사이트 구조 변경으로 대상 샵 제거 
    # try :
    #     evt_mall = soup.find(class_ = 'cm_mall_ic ty_text_s').text
    # except :
    #     evt_mall = soup.find(class_ = 'cevent_mall_ic cm_mall_ic ty_circle_m').text
    # evt_mall = evt_mall.splitlines()
    # evt_mall = [m for m in evt_mall if m != '']

    # if len(evt_mall) < 1 :
    #     evt_mall = 'none'
        
    # text 
    evt_text = soup.text.splitlines()
    evt_text = [ t for t in evt_text 
    if (('쿠폰' in t) 
    or ('%' in t)
    or ('SSGMONEY' in t)
    or ('SSG MONEY' in t)
    or ('첫구매' in t)
    or ('구매시' in t)
    or ('이벤트' in t)
    or ('핫딜' in t)
    or ('타임딜' in t)
    or ('할인' in t)
    or ('할인쿠폰' in t)   
    or ('쿠폰할인' in t)
    or ('스마일클럽' in t)
    or ('SSGPAY' in t)
    or ('쓱배송' in t)
    or ('선착순' in t)
    or ('무료배송' in t)
    or ('청구' in t))
    and ('바로가기' not in t)
    and ('주문금액' not in t)
    and ('최소주문금액' not in t)
    and ('최소 주문금액' not in t)
    and ('기준 금액' not in t)
    and ('기준금액' not in t)
    and ('결제 페이지' not in t)
    and ('결제페이지' not in t)
    and ('보유 쿠폰' not in t)
    and ('불가능' not in t)
    and ('불가' not in t)
    and ('제세공과금' not in t)
    and ('다운로드' not in t)   
    and ('다운로드 받기' not in t)
    and ('다운로드받기' not in t)
    and ('다운받기' not in t)
    and ('통합회원' not in t)
    and ('중복적용' not in t)
    and ('중복 적용' not in t)
    and ('중복적용 불가' not in t)
    and ('비방댓글' not in t)
    and ('조기종료' not in t)
    and ('유의사항' not in t)
    and ('재발급' not in t)
    and ('SOLD OUT' not in t)
    and ('Sold out' not in t)
    and ('쿠폰이 다운되었습니다' not in t)
    and ('고객님은 쿠폰을 이미 다운 받으셨습니다' not in t)
    and ('금일 쿠폰이 소진되었습니다' not in t)
    and ('선착순 사은품 증정이 마감되었습니다' not in t)
    and ('선착순 사은품 증정이 마감되었습니다' not in t)

    ]
    evt_desc = []
    for t in evt_text :
        if t not in evt_desc :
            evt_desc.append(t)

    row = pd.DataFrame.from_dict( [{"titlemain" : titlemain
                        ,"titlesub" : titlesub
                        ,"link" : link
                       ,"evt_title" : evt_title
                       ,"evt_start_dt" : evt_start_dt
                       ,"evt_end_dt" :  evt_end_dt
                      # ,"evt_mall" : evt_mall
                       ,"evt_desc" : evt_desc}])
    df = pd.concat([df, row], ignore_index = True)


## 엑셀 함수처리 
df.to_excel('./tmp/tmp.xlsx', encoding = 'utf-8-sig', index = False)
tmp_path = './tmp/tmp.xlsx'
update_dt = datetime.now()
result_path = f'./result/result_{update_dt}.xlsx'

wb = op.load_workbook(tmp_path)
ws = wb.active
for r in ws.rows : 
    #print(r)
    row_index = r[0].row
    #print(row_index)
    if row_index == 1 : 
        continue
    else : 
        ws['I'+str(row_index)] = f'''= SUBSTITUTE(H{row_index}, "', '", CHAR(10)) '''
    
wb.save(result_path)