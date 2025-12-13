import sqlite3

# DB 연결
conn = sqlite3.connect('sellers.db')
cursor = conn.cursor()

# 데이터 조회
cursor.execute("SELECT * FROM sellers")
rows = cursor.fetchall()

print(f"📊 총 {len(rows)}개의 데이터가 수집되었습니다.\n")
print("-" * 60)
print(f"{'순위':<5} {'상품명':<20} {'상호명':<10} {'연락처'}")
print("-" * 60)

for row in rows:
    # row[1]: 순위, row[2]: 상품명, row[3]: 상호명, row[5]: 연락처
    # (긴 이름은 잘라서 보여줌)
    name = row[2][:15] + "..." if len(row[2]) > 15 else row[2]
    print(f"{row[1]:<5} {name:<20} {row[3]:<10} {row[5]}")

print("-" * 60)
conn.close()