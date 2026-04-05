from flask import Flask, render_template, request, flash, redirect, url_for, session
from sqlalchemy import create_engine, text
from argon2 import PasswordHasher

app = Flask(__name__)
app.secret_key = 'your_secret_key'
ph = PasswordHasher()


conn_str = 'mysql://root:cset155@localhost/bankdb'
engine = create_engine(conn_str, echo=False)
conn = engine.connect()

# --------- SIGN UP/IN ------------
@app.route('/', methods=['GET','POST'])
def index():
    if request.method == 'POST':
        if errorDetect():
            return render_template('index.html')
        data = dict(request.form)
        data['password'] = ph.hash(data['password'])
        data['ssn'] = ph.hash(data['ssn'])
        conn.execute(text('INSERT INTO users (username, password, first_name, last_name, ssn, address, phone) VALUES (:username, :password, :f_name, :l_name, :ssn, :address, :phone)'), data)
        conn.commit()
        session['user_id'] = conn.execute(text('SELECT user_id FROM users WHERE ssn=:ssn'),{'ssn':data['ssn']})
        session['role'] = 'user'
    else:
        return render_template('index.html')
    
@app.route('/log_in', methods=['GET','POST'])
def log_in():
    if request.method == 'POST':
        if errorDetect():
            return render_template('index.html')
        data = dict(request.form)
        try:
            hashedPass = conn.execute(text('SELECT password FROM users WHERE email=:email'), data)
        except Exception:
            flash('Email not recognized. Please try again', 'error')
            return render_template('log-in.html')
        status = conn.execute(text('SELECT status FROM users WHERE email=:email'), data)
        if status == 'pending':
            return redirect('/check_status')
        try:
            ph.verify(hashedPass, data['password'])
        except Exception:
            flash('Password not recognized. Please try again', 'error')
            return render_template('log-in.html')
        session['user_id'] = conn.execute(text('SELECT user_id FROM users WHERE ssn=:ssn'),{'ssn':data['ssn']})
        session['role'] = 'user'
        return redirect('/user_page')
    else:
        return render_template('log-in.html')

@app.route('/check_status', methods=['GET','POST'])
def check_status():
    if request.method == 'POST':
        status = conn.execute(text('SELECT status FROM users WHERE user_id=:user_id'), {'user_id':session.get('user_id')})
        if status == 'pending':
            return render_template('review.html')
        else:
            return render_template('log-in.html')
    else:
        return render_template('review.html')

def errorDetect():
    check = False
    try:
        if len(request.form['f_name']) < 1:
            flash('First name field not filled. Please try again.', 'error')
            check = True
        if len(request.form['l_name']) < 1:
            flash('Last name field not filled. Please try again.', 'error')
            check = True
        if len(request.form['address']) < 1:
            flash('Address field not filled. Please try again.', 'error')
            check = True
    except BaseException:
        print('')
    if len(request.form['username']) < 1:
        flash('Username field not filled. Please try again.', 'error')
        check = True
    if len(request.form['password']) != 8:
        flash('Password is not 8 characters in length. Please try again.', 'error')
        check = True
    if not any(char in request.form['password'] for char in ['!','@','#','$','%','^','&','*','-','+','=']):
        flash('Password does not containe a special character. Please try again.', 'error')
        check = True
    if not any(char.isupper() for char in request.form['password']):
        flash('Password does not containe a capital letter. Please try again.', 'error')
        check = True
    return check
    
# ------------- USER PAGE ----------------
@app.route('/user_page', methods=['GET','POST'])
def user_page():
    return

# ------------- ADMIN PAGE ----------------




if __name__ == '__main__':
    app.run(debug=True)