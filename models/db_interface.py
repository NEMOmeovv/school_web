import sqlite3

class DBInterface:
    """
    데이터베이스의 연결, 쿼리 수행, 해제를
    정의한 DB 인터페이스
    """

    # sqlite3 DB 파일경로 (:memory:는 인메모리DB를 뜻함)
    DB_NAME = "test.db"

    def __init__(self):
        self.connection = None
        self.cursor = None

    def connect(self):
        """
        DB에 연결하여 연결객체와 커서를 획득
        """
        self.connection = sqlite3.connect(self.DB_NAME, check_same_thread=False)
        self.cursor = self.connection.cursor()

    def disconnect(self):
        """
        DB와의 연결을 해제함
        (해제하지 않을경우 메모리 누수 발생 및 파일 기반
         데이터베이스의 경우 파일 핸들을 반환하지 않아 문제 생길 수 있음)
        """
        self.connection.close()

    def execute_query(self, query, *param):
        """
        입력한 쿼리를 실행함 (결과값 반환 X)
        :param query: Query String
        """
        self.cursor.execute(query, param)  # 쿼리를 실행
        self.connection.commit()    # 데이터베이스에 반영

    def fetch_query(self, query, *param):
        """
        입력한 쿼리를 실행함 (결과값 반환 O)
        :param query: Query String
        :return: Tuple[]
        """
        print(f"query: {query}, *param: {param}")
        self.cursor.execute(query, param)
        return self.cursor.fetchall()


# initialize_once 호출 여부
_initialized = False

def initialize_DB():
    """
    현재 파일 import시 한번 실행 되는 함수
    Table 초기화 가능
    :return:
    """
    global _initialized
    if _initialized:
        return

    db = DBInterface()  # DB 인터페이스 인스턴스 획득
    db.connect()  # DB 연결

    db.execute_query("""
         CREATE TABLE IF NOT EXISTS Students (
             std_id     INTEGER PRIMARY KEY AUTOINCREMENT,  -- 학번 (기본키, 자동증가)
             name       TEXT NOT NULL,                      -- 타이틀 (NULL 비허용)
             gender     TEXT,                               -- 성별
             address    TEXT,                               -- 주소
             korean     REAL,                               -- 국어점수
             english    REAL,                               -- 영어점수
             math       REAL,                               -- 수학점수
             crt        DATETIME DEFAULT CURRENT_TIMESTAMP, -- 생성일자 (기본값은 현재시간)
             amd        DATETIME DEFAULT CURRENT_TIMESTAMP  -- 수정일자 (기본값은 현재시간)
         )  
     """)

    ret = db.fetch_query("SELECT * FROM sqlite_schema")
    for r in ret:
        print(r[4])

    # DB 연결 해제
    db.disconnect()

    _initialized = True

# 초기화 함수 실행
initialize_DB()
