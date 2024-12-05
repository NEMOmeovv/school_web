from faker import Faker
import pandas as pd
import random
from model.db_interface import *
# Faker 객체 생성
fake = Faker("ko_KR")  # 한국 이름 생성
genders = ["male", "female"]
addresses = ["서울", "부산", "대구", "인천", "광주", "대전", "울산", "세종", "경기", "강원"]
release_states = [0, 1]
# 90명의 고유 이름 생성
unique_real_names = [fake.name() for _ in range(90)]
# 나머지 10명은 랜덤으로 중복된 이름
additional_real_names = [random.choice(unique_real_names) for _ in range(10)]
# 100명의 이름 리스트 생성
all_names = unique_real_names + additional_real_names
random.shuffle(all_names)  # 이름 섞기

# 학생 데이터 생성
data_real_names = {
    "std_id": range(1, 101),
    "name": all_names,
    "gender": [random.choice(genders) for _ in range(100)],
    "address": [random.choice(addresses) for _ in range(100)],
    "korean": [round(random.uniform(50, 100),2)for _ in range(100)],
    "english": [round(random.uniform(50, 100),2) for _ in range(100)],
    "math": [round(random.uniform(50, 100),2)for _ in range(100)],
    "release_state": [random.choice(release_states) for _ in range(100)],
}

# 데이터프레임 생성
df = pd.DataFrame(data_real_names)

# 엑셀로 저장
file_path_real_names = "student_info.xlsx"
df.to_excel(file_path_real_names, index=False)

# db에 DataFrame 내용 추가

db = DBInterface()
db.connect()

for i in range(len(df)):
    std_id, name, gender, addresss, korean, english, math, release_states = df.iloc[i]
    db.execute_query("""
    INSERT INTO students (std_id, name, gender, address, korean, english, math, release_state)
    VALUES (?,?,?,?,?,?,?,?)
    """,    int(std_id), name, gender, addresss, float(korean), float(english), float(math), int(release_states))

# 결과 확인
print(db.fetch_query("""
    SELECT * FROM students
"""))
db.disconnect()
