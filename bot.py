from playwright.sync_api import sync_playwright
import time
import random
import csv
import os

# 결과 저장 파일명
FILE_NAME = "sellers_result.csv"

def save_to_csv(data):
    """데이터를 엑셀(csv) 파일에 한 줄씩 저장"""
    file_exists = os.path.isfile(FILE_NAME)
    with open(FILE_NAME, mode='a', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        # 파일이 없으면 헤더(제목) 추가
        if not file_exists:
            writer.writerow(["순위", "상품명", "상호", "사업자번호", "연락처", "URL"])
        
        writer.writerow([
            data['rank'], 
            data['name'], 
            data['seller'], 
            data['biz'], 
            data['contact'], 
            data['url']
        ])
    print(f"   💾 [저장 완료] {data['name'][:15]}...")

def run_bot():
    print("🚀 [자동화 모드] 크롬(9222)에 연결 시도...")
    
    with sync_playwright() as p:
        try:
            # 1. 켜져있는 디버깅 크롬에 연결
            browser = p.chromium.connect_over_cdp("http://localhost:9222")
            context = browser.contexts[0]
            page = context.pages[0]
            
            # 2. 검색 페이지 이동
            keyword = "딸기"
            print(f"🔍 '{keyword}' 검색 페이지로 이동합니다...")
            page.goto(f"https://www.coupang.com/np/search?component=&q={keyword}&channel=user", timeout=60000)
            
            # 로딩 대기 (페이지 구조가 바뀔 때까지 충분히 기다림)
            time.sleep(3)
            
            # 3. [수확] 상품 리스트 찾기 (사용자님 HTML 구조 반영)
            print("📋 상품 리스트 요소를 찾는 중...")
            
            product_list = []
            
            # [수정 포인트] 사용자님 화면에 맞는 선택자(Selector) 사용
            # 1순위: id="product-list" (새 디자인)
            # 2순위: id="productList" (구 디자인 - 혹시 몰라 예비용)
            if page.locator("ul#product-list li").count() > 0:
                items = page.locator("ul#product-list > li")
                print("   👉 신규 디자인(product-list) 감지됨!")
            else:
                items = page.locator("ul#productList > li.search-product")
                print("   👉 기존 디자인(productList) 감지됨!")
            
            count = items.count()
            if count == 0:
                print("❌ 상품을 하나도 못 찾았습니다. 로딩이 덜 됐거나 캡차(봇방지)가 떴을 수 있습니다.")
                return

            # 상위 5개만 수집 (광고 AD 제외 로직 포함)
            collected = 0
            for i in range(count):
                if collected >= 5: break # 5개 모으면 중단
                
                try:
                    item = items.nth(i)
                    
                    # 링크(a태그) 찾기
                    link_element = item.locator("a")
                    # 링크 주소가 없으면 패스 (광고 배너 등일 수 있음)
                    if link_element.count() == 0: continue
                        
                    href = link_element.get_attribute("href")
                    if not href: continue

                    full_url = "https://www.coupang.com" + href
                    
                    # 상품명 추출 (구조가 조금씩 달라도 텍스트가 있는 div나 img alt 등을 찾음)
                    name = item.inner_text().split("\n")[0] # 첫 번째 줄 텍스트를 이름으로 사용
                    
                    product_list.append({
                        "rank": collected + 1,
                        "name": name,
                        "url": full_url
                    })
                    collected += 1
                    print(f"   [{collected}등] URL 확보: {name[:10]}...")
                    
                except Exception as e:
                    print(f"   ⚠️ {i}번째 항목 패스: {e}")
                    continue
            
            print(f"\n✅ 총 {len(product_list)}개 URL 확보 완료! 상세 수집 시작...\n")

            # 4. [채굴] 각 상품 페이지 방문
            for prod in product_list:
                print(f"▶ {prod['rank']}등 상품 접속 중...")
                
                try:
                    # 페이지 이동 (새 탭 띄우지 않고 현재 탭 이동)
                    page.goto(prod['url'], timeout=60000)
                    
                    # 스크롤 내리기 (판매자 정보 로딩)
                    for _ in range(6):
                        page.mouse.wheel(0, 2000)
                        time.sleep(0.5)
                    page.keyboard.press("End")
                    time.sleep(2) # 로딩 대기

                    # 정보 추출
                    seller, biz, contact = "-", "-", "-"
                    
                    # 테이블 찾기 (못 찾으면 '-'로 저장됨)
                    if page.locator("table.prod-delivery-return-policy-table").count() > 0:
                        # 텍스트가 포함된 th의 형제 td 찾기
                        if page.locator("//th[contains(., '상호')]/following-sibling::td[1]").count() > 0:
                            seller = page.locator("//th[contains(., '상호')]/following-sibling::td[1]").inner_text()
                        if page.locator("//th[contains(., '사업자')]/following-sibling::td[1]").count() > 0:
                            biz = page.locator("//th[contains(., '사업자')]/following-sibling::td[1]").inner_text()
                        if page.locator("//th[contains(., '연락처')]/following-sibling::td[1]").count() > 0:
                            contact = page.locator("//th[contains(., '연락처')]/following-sibling::td[1]").inner_text()
                    
                    # CSV 파일 저장
                    save_to_csv({
                        "rank": prod['rank'],
                        "name": prod['name'],
                        "seller": seller.strip(),
                        "biz": biz.strip(),
                        "contact": contact.strip(),
                        "url": prod['url']
                    })
                    
                    # 봇 탐지 회피용 휴식
                    time.sleep(random.uniform(2, 4))

                except Exception as e:
                    print(f"   ❌ 에러 발생: {e}")
                    continue

            print("\n🎉 [작업 끝] 'sellers_result.csv' 파일을 확인해주세요!")

        except Exception as e:
            print(f"🚫 치명적 오류: {e}")
            print("💡 팁: 크롬이 디버깅 모드(9222 포트)로 켜져 있는지 확인하세요.")

if __name__ == "__main__":
    run_bot()