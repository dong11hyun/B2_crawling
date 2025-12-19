import asyncio
from playwright.async_api import async_playwright
import random
import sqlite3
import os

# ==========================================
# [설정] 안전 운전 모드
# ==========================================
DB_NAME = "sellers_safe.db"   # 안전모드용 DB 파일
MIN_DELAY = 3.0               # 최소 대기 (초)
MAX_DELAY = 7.0               # 최대 대기 (초)
WASH_CYCLE = 10               # 10개마다 쿠키 세탁

# ==========================================
# [1] 데이터베이스 초기화 및 저장
# ==========================================
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sellers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rank INTEGER,
            product_name TEXT,
            seller_name TEXT,
            biz_no TEXT,
            contact TEXT,
            url TEXT UNIQUE,
            crawled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    print(f"📁 [시스템] DB 초기화 완료: {DB_NAME}")

def save_to_db(data):
    """건별 저장 (안전모드는 배치 대신 바로바로 저장 추천)"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT OR REPLACE INTO sellers (rank, product_name, seller_name, biz_no, contact, url)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (data['rank'], data['name'], data['seller'], data['biz'], data['contact'], data['url']))
        conn.commit()
        print(f"   💾 [저장] {data['name'][:10]}...")
    except Exception as e:
        print(f"   ❌ 저장 실패: {e}")
    finally:
        conn.close()

# ==========================================
# [2] 사람처럼 행동하는 함수들
# ==========================================
async def human_sleep(reason=""):
    """불규칙하게 쉬는 함수"""
    sleep_time = random.uniform(MIN_DELAY, MAX_DELAY)
    print(f"      💤 {reason} 대기... ({sleep_time:.1f}초)")
    await asyncio.sleep(sleep_time)

async def slow_scroll(page):
    """마우스 휠을 천천히 굴리는 척하는 함수"""
    # 2~3번 나눠서 내림
    for _ in range(random.randint(2, 4)):
        await page.mouse.wheel(0, random.randint(500, 1000))
        await asyncio.sleep(random.uniform(0.5, 1.2))
    
    # 마지막에 바닥 찍기 (데이터 로딩 트리거)
    await page.keyboard.press("End")
    await asyncio.sleep(2) # 로딩 대기

# ==========================================
# [3] 메인 크롤러 로직
# ==========================================
async def run_safe_bot():
    print("🐢 [쿠팡 안전 모드] 천천히 수집을 시작합니다...")
    init_db()

    async with async_playwright() as p:
        try:
            # 1. 기생 모드 연결
            browser = await p.chromium.connect_over_cdp("http://localhost:9222")
            context = browser.contexts[0]
            
            # 탭 확보
            if len(context.pages) > 0:
                page = context.pages[0]
            else:
                page = await context.new_page()

            # ----------------------------------------------------
            # 1단계: URL 수집 (지도 그리기) - 기존 로직 유지
            # ----------------------------------------------------
            keyword = "딸기"
            product_list = []
            collected = 0

            print(f"\n🔍 1단계: '{keyword}' URL 수집 중...")
            
            # 테스트를 위해 1페이지만 (필요하면 range(1, 3) 등으로 변경)
            for page_num in range(1, 2): 
                await page.goto(f"https://www.coupang.com/np/search?component=&q={keyword}&channel=user&page={page_num}", timeout=30000)
                await asyncio.sleep(2)
                
                # HTML 구조 자동 감지 (기존 코드 활용)
                if await page.locator("ul#product-list li").count() > 0:
                    items = page.locator("ul#product-list > li")
                else:
                    items = page.locator("ul#productList > li.search-product")
                
                count = await items.count()
                
                for i in range(count):
                    try:
                        item = items.nth(i)
                        link_el = item.locator("a")
                        if await link_el.count() == 0: continue
                        
                        href = await link_el.get_attribute("href")
                        if not href: continue

                        full_url = "https://www.coupang.com" + href
                        raw_name = await item.inner_text()
                        name = raw_name.split("\n")[0]
                        
                        collected += 1
                        product_list.append({
                            "rank": collected,
                            "name": name,
                            "url": full_url
                        })
                    except:
                        continue
                
                print(f"   📄 {page_num}페이지 완료. 누적 {len(product_list)}개")
                await human_sleep("페이지 이동 전")

            print(f"\n✅ 총 {len(product_list)}개 확보. 2단계 상세 수집 시작...\n")

            # ----------------------------------------------------
            # 2단계: 상세 수집 (한 땀 한 땀)
            # ----------------------------------------------------
            for i, prod in enumerate(product_list):
                
                # [핵심] 신분 세탁 (Session Washing)
                # 10개마다 쿠키를 지워서 '새로운 방문자'인 척 위장
                if i > 0 and i % WASH_CYCLE == 0:
                    print("\n🧹 [보안] 쿠키 및 캐시 삭제 (신분 세탁)...")
                    await context.clear_cookies()
                    await asyncio.sleep(1)

                print(f"▶ [{i+1}/{len(product_list)}] {prod['name'][:10]}... 이동")
                
                try:
                    # 페이지 이동
                    await page.goto(prod['url'], timeout=30000)
                    
                    # 사람처럼 천천히 스크롤
                    await slow_scroll(page)

                    # 데이터 추출
                    seller, biz, contact = "-", "-", "-"
                    
                    # 테이블이 있는지 확인
                    if await page.locator("table.prod-delivery-return-policy-table").count() > 0:
                        # 상호
                        if await page.locator("//th[contains(., '상호')]/following-sibling::td[1]").count() > 0:
                            seller = await page.locator("//th[contains(., '상호')]/following-sibling::td[1]").inner_text()
                        
                        # 사업자번호
                        if await page.locator("//th[contains(., '사업자')]/following-sibling::td[1]").count() > 0:
                            biz = await page.locator("//th[contains(., '사업자')]/following-sibling::td[1]").inner_text()
                        
                        # 연락처
                        if await page.locator("//th[contains(., '연락처')]/following-sibling::td[1]").count() > 0:
                            contact = await page.locator("//th[contains(., '연락처')]/following-sibling::td[1]").inner_text()

                    # DB에 즉시 저장
                    save_to_db({
                        "rank": prod['rank'],
                        "name": prod['name'],
                        "seller": seller.strip(),
                        "biz": biz.strip(),
                        "contact": contact.strip(),
                        "url": prod['url']
                    })

                    # 사람처럼 쉬기
                    await human_sleep("다음 상품 이동 전")

                except Exception as e:
                    print(f"   ⚠️ 에러 발생 (건너뜀): {e}")
                    continue

            print("\n🎉 [완료] 안전하게 모든 수집이 끝났습니다.")

        except Exception as e:
            print(f"🚫 전체 에러: {e}")

if __name__ == "__main__":
    asyncio.run(run_safe_bot())