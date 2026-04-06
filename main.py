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
        conn.execute(text('INSERT INTO users (username, password, first_name, last_name, ssn, address, phone) VALUES (:username, :password, :f_name, :l_name, :ssn, :address, :phone)'), data)
        conn.commit()
        session['user_id'] = conn.execute(text('SELECT user_id FROM users WHERE ssn=:ssn'), data).fetchone()[0]
        session['role'] = 'user'
        return redirect('/check_status')
    else:
        return render_template('index.html')
    
@app.route('/log_in', methods=['GET','POST'])
def log_in():
    if request.method == 'POST':
        if errorDetect():
            return render_template('index.html')
        data = dict(request.form)
        try:
            hashedUsers = conn.execute(text('SELECT username, password FROM users')).fetchall()
            hashedAdmin = conn.execute(text('SELECT username, password FROM admin')).fetchone()
            if any(ph.verify(hp.password, data['password']) and hp.username == data['username'] for hp in hashedUsers):
                user_id = conn.execute(text('SELECT user_id FROM users WHERE username=:username'), data).fetchone()[0]
        except Exception:
            try:
                if ph.verify(hashedAdmin[1],data['password']) and hashedAdmin[0] == data['username']:
                    user_id = conn.execute(text('SELECT admin_id FROM admin WHERE username=:username'), data).fetchone()[0]
                    session['user_id'] = user_id
                    session['role'] = 'admin'
                    return redirect('/admin_page')
            except Exception:
                flash('Password or username not recognized. Please try again', 'error')
                return render_template('log-in.html')
        status = conn.execute(text('SELECT status FROM users WHERE user_id=:user_id'), {'user_id':user_id}).fetchone()[0]
        if status == 'pending':
            return redirect('/check_status')
        session['user_id'] = user_id
        session['role'] = 'user'
        return redirect('/my_account_page')
    else:
        return render_template('log-in.html')

@app.route('/check_status', methods=['GET','POST'])
def check_status():
    if request.method == 'POST':
        try:
            status = conn.execute(text('SELECT status FROM users WHERE user_id=:user_id'), {'user_id':session.get('user_id')}).fetchone()[0]
            if status == 'pending':
                return render_template('review.html')
            else:
                return redirect('/log_in')
        except Exception:
            flash('Session ended.', 'error')
            return redirect('/log_in')
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
@app.route('/my_account_page', methods=['GET','POST'])
def user_page():
    bank_acc = conn.execute(text('SELECT * FROM bank_accounts WHERE user_id=:user_id'),{'user_id':session.get('user_id')}).fetchone()
    cards = conn.execute(text('SELECT c.*, CONCAT(u.first_name, \' \', u.last_name) AS name FROM cards AS c JOIN users AS u USING (user_id) WHERE user_id=:user_id;'),{'user_id':session.get('user_id')}).fetchall()
    return render_template('user_page.html', bank_acc=bank_acc, cards=cards)

@app.route('/add_card/<string:card_num>', methods=['POST'])
def add_card(card_num):
    bank_acc = conn.execute(text('SELECT * FROM bank_accounts WHERE user_id=:user_id'),{'user_id':session.get('user_id')}).fetchone()
    cards = conn.execute(text('SELECT c.*, CONCAT(u.first_name, \' \', u.last_name) AS name FROM cards AS c JOIN users AS u USING (user_id) WHERE user_id=:user_id;'),{'user_id':session.get('user_id')}).fetchall()
    add_card = conn.execute(text('SELECT c.*, CONCAT(u.first_name, \' \', u.last_name) AS name FROM cards AS c JOIN users AS u USING (user_id) WHERE user_id=:user_id and card_number=:card_num;'),{'user_id':session.get('user_id'), 'card_num':card_num}).fetchone()
    return render_template('user_page.html', bank_acc=bank_acc, cards=cards, add_card=add_card)

@app.route('/add_money', methods=['POST'])
def add_money():
    add_card = dict(request.form)
    owned_cards = conn.execute(text('SELECT card_number FROM cards WHERE user_id=:user_id'),{'user_id':session.get('user_id')}).fetchall()
    owned_card_numbers = [row[0] for row in owned_cards]
    if add_card['card_number'] not in owned_card_numbers:
        card_num = add_card['card_number'][:4]+' '+add_card['card_number'][4:8]+' '+add_card['card_number'][8:12]+' '+add_card['card_number'][12:16]
        conn.execute(text('INSERT INTO cards (user_id, card_number, expiry_date, cvv) VALUES (:user_id, :card_number, :date, :cvv)'), {'user_id':session.get('user_id'), 'card_number':card_num, 'date':add_card['date'], 'cvv':add_card['cvv']})
        conn.commit()
    deposit = dict(request.form)['deposit-amount']
    conn.execute(text('UPDATE bank_accounts SET balance = balance + :deposit WHERE user_id=:user_id'),{'deposit':deposit[1:], 'user_id':session.get('user_id')})
    conn.commit()
    bank_acc = conn.execute(text('SELECT * FROM bank_accounts WHERE user_id=:user_id'),{'user_id':session.get('user_id')}).fetchone()
    cards = conn.execute(text('SELECT c.*, CONCAT(u.first_name, \' \', u.last_name) AS name FROM cards AS c JOIN users AS u USING (user_id) WHERE user_id=:user_id;'),{'user_id':session.get('user_id')}).fetchall()
    return render_template('user_page.html', bank_acc=bank_acc, cards=cards)

@app.route('/send_money', methods=['POST'])
def send_money():
    data = dict(request.form)
    balance = conn.execute(text('SELECT balance FROM bank_accounts WHERE user_id=:user_id'),{'user_id':session.get('user_id')}).fetchone()[0]
    if balance >= float(data['send-amount'][1:]):
        try:
            conn.execute(text('UPDATE bank_accounts SET balance = balance - :credit WHERE user_id=:user_id'),{'credit':data['send-amount'][1:], 'user_id':session.get('user_id')})
            conn.commit()
            recipient_id = conn.execute(text('SELECT user_id FROM bank_accounts WHERE account_number=:account_number'),{'account_number':data['recipient']}).fetchone()[0]
            conn.execute(text('UPDATE bank_accounts SET balance = balance + :deposit WHERE user_id=:user_id'),{'deposit':data['send-amount'][1:], 'user_id':recipient_id})
            conn.commit()
        except Exception:
            print('')
    bank_acc = conn.execute(text('SELECT * FROM bank_accounts WHERE user_id=:user_id'),{'user_id':session.get('user_id')}).fetchone()
    cards = conn.execute(text('SELECT c.*, CONCAT(u.first_name, \' \', u.last_name) AS name FROM cards AS c JOIN users AS u USING (user_id) WHERE user_id=:user_id;'),{'user_id':session.get('user_id')}).fetchall()
    return render_template('user_page.html', bank_acc=bank_acc, cards=cards)

@app.route('/view_account', methods=['POST'])
def view_account():
    user_data = conn.execute(text('SELECT * FROM users WHERE user_id=:user_id'),{'user_id':session.get('user_id')}).fetchone()
    return render_template('acc_details.html', user_data=user_data)
# ------------- ADMIN PAGE ----------------
@app.route('/admin_page')
def admin_page():
    users_data = conn.execute(text('SELECT * FROM users WHERE status="pending"')).fetchall()
    return render_template('admin_page.html', users_data=users_data)

@app.route('/reject_app/<int:user_id>', methods=['POST'])
def reject(user_id):
    conn.execute(text('DELETE FROM users WHERE user_id=:user_id'),{'user_id':user_id})
    conn.commit()
    return redirect('/admin_page')

@app.route('/approve_app/<int:user_id>', methods=['POST'])
def approve(user_id):
    conn.execute(text('UPDATE users SET status = "approved" WHERE user_id=:user_id'),{'user_id':user_id})
    conn.commit()
    conn.execute(text('INSERT INTO bank_accounts (user_id, balance) VALUES (:user_id, 0.00)'),{'user_id':user_id})
    conn.commit()
    return redirect('/admin_page')


if __name__ == '__main__':
    app.run(debug=True)