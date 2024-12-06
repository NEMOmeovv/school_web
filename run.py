import os

from flask import Flask, render_template, request, jsonify,redirect
from model.db_access import DB_Access
from service.user_service import UserService

app = Flask(__name__)
app.secret_key = os.urandom(24)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=["POST"])
def login():
    """
    입력한 user_id와 user_pw를 불러와 db에서 확인후 session에 user정보 추가
    :return:
    """
    user_id = request.form.get('user_id')
    user_pw = request.form.get('user_pw')

    user_service = UserService()
    result = user_service.login(user_id, user_pw)

    if result['state'] == 'success':
        return render_template('home.html', login_status='success')
    else:
        return render_template('home.html', login_status='fail', error_msg=result['msg'])

@app.route('/logout', methods=['POST'])
def logout():
    """
    세션에서 유저 정보 제거 후 홈 화면으로 전송
    """
    user_service = UserService()
    user_service.logout()
    return redirect('/')


@app.route('/student/register')
def registing_page():
    """
    회원가입 페이지 보여주기
    """
    return render_template('register.html')

@app.route('/student/register', methods=["POST"])
def register():
    """
    회원가입 처리 라우터
    """
    std_id = request.form.get('std_id')
    user_id = request.form.get('user_id')
    user_pw = request.form.get('user_pw')

    # 필수 값 검증
    if not std_id or not user_id or not user_pw:
        return render_template(
            'register.html',
            error_msg="모든 필드를 입력해주세요."
        )

    db = DB_Access()

    # 학번 존재 여부 확인
    if not db.check_std_id(std_id):
        return render_template(
            'register.html',
            error_msg="존재하지 않는 학번입니다."
        )

    user_service = UserService()
    try:
        user_service.registration(std_id, user_id, user_pw)
        return render_template(
            'home.html',
            success_msg="회원가입이 성공적으로 완료되었습니다!"
        )
    except Exception as e:
        # 중복된 ID 등의 예외 처리
        # print(str(e).strip() == "UNIQUE constraint failed: User.std_id")
        if str(e) == "UNIQUE constraint failed: User.std_id":
            return render_template('register.html',
               error_msg="이미 아이디가 있는 학번입니다. 관리자에게 문의하세요.")
        elif str(e) == "UNIQUE constraint failed: User.user_id":
            return render_template('register.html',
               error_msg="중복된 아이디 입니다. 다른 아이디를 사용해주세요.")
        return render_template(
            'register.html',
            error_msg=f"회원가입 중 오류가 발생했습니다: {e}"
        )

@app.route('/student/search_page')
def search_student_page():
    """
    검색 페이지 + 로그인된 사용자 정보 전달
    """
    user_service = UserService()

    # 로그인 세션 확인
    session_check = user_service.session_check()
    if session_check['state'] == 'fail':
        return redirect('/')

    # 로그인된 사용자 정보 가져오기
    user_data = user_service.get_user()
    db = DB_Access()
    user_info = db.find_by_std_id(user_data['std_id'])
    # print("search_student_page의 user_info:",user_info)
    return render_template('search_page.html', user_info=user_info)

@app.route('/student/search',methods = ['GET'])
def search_page():
    """
    검색한 학생 정보 넘기기
    """
    if request.method == 'GET':
        user_service = UserService()
        user_data = user_service.get_user()
        std_id = request.args.get('std_id')
        db = DB_Access()
        user_info = db.find_by_std_id(user_data['std_id'])
        std_info = db.find_by_std_id(std_id)
        return render_template('search_page.html',user_info=user_info, std_info=std_info)


@app.route('/ranking/<subject>')
def get_ranking(subject):
    """
    선택한 과목을 기준으로 정렬 + 정보 비공개 학생의 경우 이름을 비공개처리
    이름이 아닌 성적을 비공개 처리하고싶으면 147번째 줄의 if문을 148번째로 옮기면 가능
    """
    db = DB_Access()
    students = db.get_all_students()  # 모든 학생 데이터 가져오기

    if subject not in ['korean', 'english', 'math']:
        return jsonify([])

    # 점수 순으로 정렬 (모든 학생 포함)
    sorted_students = sorted(students, key=lambda x: x[subject], reverse=True)

    # 이름과 점수 반환, 비공개 처리
    result = [
        {
            'rank': index + 1,
            'name': student['name'] if student['release_state'] else '비공개',
            'score': student[subject]
        }
        for index, student in enumerate(sorted_students)
    ]
    return jsonify(result)


@app.route('/toggle_release', methods=['POST'])
def toggle_release():
    """
    현재 로그인된 사용자의 정보 공개/비공개 상태를 토글합니다.
    """
    user_service = UserService()
    user = user_service.get_user()
    db = DB_Access()

    # 현재 상태 가져오기
    user_data = db.find_by_std_id(user['std_id'])
    if not user_data:
        return jsonify({'state': 'fail', 'message': '사용자 정보를 찾을 수 없습니다.'})

    # 상태 토글
    new_state = 0 if user_data['release_state'] else 1
    db.update_release_state(user['std_id'], new_state)

    return jsonify({'state': 'success', 'message': f"정보가 {'공개' if new_state else '비공개'}로 변경되었습니다."})


if __name__ == "__main__":
    app.run(debug=True)
