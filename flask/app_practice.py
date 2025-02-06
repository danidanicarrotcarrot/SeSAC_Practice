from email_validator import EmailNotValidError, validate_email
from flask import Flask, current_app, render_template, url_for, redirect, request, make_response, session, flash
import os
from flask_mail import Mail, Message

# flask 클래스 인스턴스화
app = Flask(__name__)

app.secret_key = 'dani'
app.config["config_key"] = "2AZSMss3p5qPbcY2hBsJ"

# 이메일 송신 기능 구현 >flask-mail 처리 추가
# Mail 클래스의 컨피그를 추가
app.config["MAIL_SERVER"] = os.environ.get("MAIL_SERVER")
app.config["MAIL_PORT"] = os.environ.get("MAIL_PORT")
app.config["MAIL_USE_TLS"] = os.environ.get("MAIL_USE_TLS")
app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD")
app.config["MAIL_DEFAULT_SENDER"] = os.environ.get("MAIL_DEFAULT_SENDER")

# flask-mail확장을 등록
mail = Mail(app)

# url과 실행할 함수를 매핑
@app.route("/")
def index():
	return "<h1>Hello, FlaskBook!</>"

# 엔드포인트 명 추가하기
@app.route("/hello", methods=["GET"], endpoint="hello-endpoint")
def hello():
    return "<h1>Hello, World</>"

# # Rule에 변수 지정하기 > 템플릿 활용 (templates/index.html)
@app.route("/hello/<name>")
def show_name(name):
    return render_template("index.html", name=name)

# 문의 폼 엔드포인트 만들기
@app.route("/contact") # 문의 폼 화면을 반환하는 contact 엔드포인트
def contact():
    # 이메일을 보낸다.
    # contact 앤드포트로 리다이렉트 한다
    
    # 응답 오브젝트를 취득한다
    response = make_response(render_template("contact.html"))
    # 쿠키 설정
    response.set_cookie("flaskbook key", "flaskbook value")
    # 세션 설정
    session["username"] = "AK"
    # 응답 오브젝트 반환
    return response

# post된 폼의 값 얻기
@app.route("/contact/complete", methods = ["GET", "POST"]) # get과 post 메서드 허가
def contact_complete():
    if request.method == "POST": # 요청된 메서드 확인
        # form 속성을 이용해서 폼의 값을 취득한다
        username = request.form["username"]
        email = request.form["email"]
        description = request.form["description"]
        
        # 입력 체크
        is_valid = True
        if not username:
            flash("사용자명은 필수입니다")
            is_valid = False
        
        if not email:
            flash("메일 주소는 필수입니다")
            is_valid = False
        
        try:
            validate_email(email)
        except EmailNotValidError:
            flash("메일 주소의 형식으로 입력해 주세요")
            is_valid = False
            
        if not description:
            flash("문의 내용은 필수입니다")
            is_valid = False
            
        if not is_valid:
            return redirect(url_for("contact"))
        
        # 문의 완료 엔드포인트로 리다이렉트한다
        flash("문의 내용은 메일로 송신했습니다. 문의해 주셔서 감사합니다")
        
        # 이메일 보내는 처리 추가
        send_email(email, "문의 감사합니다.", "contact_mail", username=username, description=description,)
        
        return redirect(url_for("contact_complete")) # post의 경우 문의 완료 엔드포인트로 리다이렉트
    return render_template("contact_complete.html") # get의 경우 문의 완료 화면(contact_complete.html) 반환

# 이메일 보내기 추가
def send_email(to, subject, template, **kwargs):
    """메일을 송신하는 함수"""
    msg = Message(subject, recipients=[to])
    msg.body = render_template(template+".txt", **kwargs)
    msg.html = render_template(template+".html", **kwargs)
    mail.send(msg)