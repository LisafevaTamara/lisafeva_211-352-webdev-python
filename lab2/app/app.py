from flask import Flask, render_template, request, make_response
import re

app = Flask(__name__)

@app.route('/')
def index():
    url = request.url
    return render_template('index.html')

@app.route('/headers')
def headers():
    return render_template('headers.html')

@app.route('/args')
def args():
    return render_template('args.html')

@app.route('/cookies')
def cookies():
    response = make_response(render_template("cookies.html"))
    if 'q' in request.cookies: 
        response.set_cookie('q', 'qq', expires = 0)
    else:
        response.set_cookie('q', 'qq')
    return response

@app.route('/form', methods = ['GET', 'POST'])
def form():
    return render_template("form.html")

@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404

@app.route('/check_phone', methods=['GET', 'POST'])
def check_phone():
    if request.method=="POST":
        phone_number = request.form['phone']
        if re.search(r'[^0-9 +().-]', phone_number):
            return render_template('check_phone.html', error='Недопустимый ввод. В номере телефона встречаются недопустимые символы.', phone = phone_number)

        phone_number = re.sub(r'\D', '', phone_number) 
        if len(phone_number) == 11:
            if phone_number[0] == '7' or phone_number[0] == '8':
                phone_number = '8' + phone_number[1:]
            else:
                return render_template('check_phone.html', error='Недопустимый ввод. Неверное количество цифр.', phone = phone_number)
        elif len(phone_number) == 10:
            phone_number = '8' + phone_number
        else:
            return render_template('check_phone.html', error='Недопустимый ввод. Неверное количество цифр.', phone = phone_number)

        phone_number = re.sub(r'(\d{1})(\d{3})(\d{3})(\d{2})(\d{2})', r'8-\2-\3-\4-\5', phone_number)
        return render_template('check_phone.html', phone=phone_number)
    else:
        return render_template('check_phone.html')