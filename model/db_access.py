from model.db_interface import DBInterface

class DB_Access:    # 학생 정보를 가져오기 위해 DB에 접근
    def check_std_id(self,std_id):
        db = DBInterface()
        db.connect()

        result = db.fetch_query("""
                   SELECT *
                   FROM students
                   WHERE std_id = ?
               """, std_id)

        db.disconnect()

        return bool(result)

    def find_by_std_id(self, std_id):
        """
        std_name: 찾을 학생 이름
        return: 해당 하는 학생의 정보, 여러개 일 경우 여러개 리턴
        """
        db = DBInterface()
        db.connect()

        result = db.fetch_query("""
            SELECT *
            FROM students
            WHERE std_id = ?
        """,std_id)

        db.disconnect()

        if len(result) :
            result = result[0]
            return {'std_id': result[0], 'name': result[1], 'gender': result[2],'address': result[3],
                    'korean': result[4], 'english': result[5], 'math': result[6], 'release_state': result[7]}
        else:
            return []

    def get_all_students(self):
        db = DBInterface()
        db.connect()

        result = db.fetch_query("""
              SELECT *
              FROM students
              """)

        return [
            { 'name': result[i][1],'korean': result[i][4], 'english': result[i][5], 'math': result[i][6], 'release_state': result[i][7]}
            for i in range(len(result))
        ]

    def update_release_state(self,std_id, new_state):
        db = DBInterface()
        db.connect()
        db.execute_query("""
            UPDATE Students 
            SET release_state= ?
            WHERE std_id=?
        """,new_state, std_id)
        db.disconnect()