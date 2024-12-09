import os
from flask import Flask, render_template, request, jsonify, redirect
from model.db_access import DB_Access
from service.user_service import UserService

app = Flask(__name__)
app.secret_key = os.urandom(24)

# 환경변수에서 PORT 값을 가져오고, 없으면 기본값 5000을 사용
port = int(os.environ.get("PORT", 5000))

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=["POST"])
def login():
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
    user_service = UserService()
    user_service.logout()
    return redirect('/')

@app.route('/student/register')
def registing_page():
    return render_template('register.html')

@app.route('/student/register', methods=["POST"])
def register():
    std_id = request.form.get('std_id')
    user_id = request.form.get('user_id')
    user_pw = request.form.get('user_pw')

    if not std_id or not user_id or not user_pw:
        return render_template('register.html', error_msg="모든 필드를 입력해주세요.")

    db = DB_Access()
    if not db.check_std_id(std_id):
        return render_template('register.html', error_msg="존재하지 않는 학번입니다.")

    user_service = UserService()
    try:
        user_service.registration(std_id, user_id, user_pw)
        return render_template('home.html', success_msg="회원가입이 성공적으로 완료되었습니다!")
    except Exception as e:
        if str(e) == "UNIQUE constraint failed: User.std_id":
            return render_template('register.html', error_msg="이미 아이디가 있는 학번입니다. 관리자에게 문의하세요.")
        elif str(e) == "UNIQUE constraint failed: User.user_id":
            return render_template('register.html', error_msg="중복된 아이디 입니다. 다른 아이디를 사용해주세요.")
        return render_template('register.html', error_msg=f"회원가입 중 오류가 발생했습니다: {e}")

@app.route('/student/search_page')
def search_student_page():
    user_service = UserService()
    session_check = user_service.session_check()
    if session_check['state'] == 'fail':
        return redirect('/')

    user_data = user_service.get_user()
    db = DB_Access()
    user_info = db.find_by_std_id(user_data['std_id'])
    return render_template('search_page.html', user_info=user_info)

@app.route('/student/search', methods=['GET'])
def search_page():
    if request.method == 'GET':
        user_service = UserService()
        user_data = user_service.get_user()
        std_id = request.args.get('std_id')
        db = DB_Access()
        user_info = db.find_by_std_id(user_data['std_id'])
        std_info = db.find_by_std_id(std_id)
        return render_template('search_page.html', user_info=user_info, std_info=std_info)

@app.route('/ranking/<subject>')
def get_ranking(subject):
    db = DB_Access()
    students = db.get_all_students()

    if subject not in ['korean', 'english', 'math']:
        return jsonify([])

    sorted_students = sorted(students, key=lambda x: x[subject], reverse=True)

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
    user_service = UserService()
    user = user_service.get_user()
    db = DB_Access()

    user_data = db.find_by_std_id(user['std_id'])
    if not user_data:
        return jsonify({'state': 'fail', 'message': '사용자 정보를 찾을 수 없습니다.'})

    new_state = 0 if user_data['release_state'] else 1
    db.update_release_state(user['std_id'], new_state)

    return jsonify({'state': 'success', 'message': f"정보가 {'공개' if new_state else '비공개'}로 변경되었습니다."})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=port)  # 여기서 포트를 설정합니다.
