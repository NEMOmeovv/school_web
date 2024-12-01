from flask import Flask, render_template, request, jsonify
from models.db_access import DB_Access

app = Flask(__name__)

@app.route('/home')
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/student/info')
def search_student():
    return render_template('search_student.html')

@app.route('/student/check',methods = ['GET'])
def check_student():
    if request.method == 'GET':
        std_name = request.args.get('std_name')
        print(std_name)
        db = DB_Access()
        result = db.check_student(std_name)
        print(result)
        return render_template('show_info.html',std_infos=result)

@app.route('/no-sidebar')
def test():
    return render_template('no-sidebar.html')

if __name__ == "__main__":
    app.run(debug=True)
# TODO: 학생 정보에 info_release 라는 이름의 공개 여부bool 타입으로 정의
