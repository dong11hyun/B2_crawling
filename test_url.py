from playwright.sync_api import sync_playwright
import time

def debug_url_harvest():
    print("🕵️ [진단 모드] URL 수집 테스트 시작...")
    
    with sync_playwright() as p:
        try:
            # 1. 켜져있는 크롬에 연결
            browser = p.chromium.connect_over_cdp("http://localhost:9222")
            context = browser.contexts[0]
            page = context.pages[0]
            
            print(f"✅ 브라우저 연결됨. 현재 페이지: {page.title()}")

            # 2. 검색 페이지 접속 확인
            keyword = "딸기"
            search_url = f"https://www.coupang.com/np/search?component=&q={keyword}&channel=user"
            
            # 이미 검색창이면 새로고침, 아니면 이동
            if "search" in page.url:
                print("🔄 현재 검색 페이지입니다. 새로고침합니다.")
                page.reload()
            else:
                print(f"👉 검색 페이지로 이동합니다...")
                page.goto(search_url, timeout=30000)
            
            time.sleep(3) # 로딩 대기

            # 3. 상품 리스트 요소 찾기 (진단 핵심)
            print("\n[분석 중] 화면의 상품 요소를 찾습니다...")
            
            # 상품 목록 컨테이너가 있는지 확인
            try:
                page.wait_for_selector("ul#productList", timeout=5000)
                print("  - OK: 상품 리스트 컨테이너(ul#productList) 발견됨")
            except:
                print("  - FAIL: 상품 리스트 컨테이너를 못 찾았습니다. (로딩 실패 또는 차단)")
            
            # 개별 상품 요소 찾기
            items = page.locator("li.search-product")
            count = items.count()
            print(f"  - 발견된 상품 개수: {count}개")

            if count == 0:
                print("❌ [결과] 실패: 상품이 하나도 안 잡힙니다. HTML 구조가 다르거나 로딩이 안 됐습니다.")
                return

            # 4. 상위 5개 추출 테스트
            print(f"\n[추출 테스트] 상위 5개 링크를 뽑아봅니다.")
            print("-" * 50)
            
            success_count = 0
            for i in range(min(5, count)):
                try:
                    item = items.nth(i)
                    
                    # 상품명
                    name = item.locator("div.name").inner_text()
                    # 링크
                    link_element = item.locator("a.search-product-link")
                    href = link_element.get_attribute("href")
                    
                    full_url = "https://www.coupang.com" + href
                    
                    print(f"[{i+1}등] {name[:20]}...")
                    print(f"   🔗 {full_url}")
                    success_count += 1
                except Exception as e:
                    print(f"[{i+1}등] ⚠️ 추출 에러: {e}")
            
            print("-" * 50)
            print(f"✅ 최종 진단: 5개 중 {success_count}개 추출 성공")

        except Exception as e:
            print(f"🚫 시스템 에러: {e}")
            print("💡 팁: 크롬 디버깅 모드가 켜져 있는지 확인하세요.")

if __name__ == "__main__":
    debug_url_harvest()