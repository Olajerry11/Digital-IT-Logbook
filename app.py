import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, Response, session, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from fpdf import FPDF
from werkzeug.security import generate_password_hash, check_password_hash
import re
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature

# Load environment variables from the .env file
load_dotenv()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///logbook.db'
app.config['SECRET_KEY'] = 'my_super_secret_key' # Secures your session data

# --- GMAIL SMTP CONFIGURATION ---
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME') 
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
mail = Mail(app)

# Token generator for email verification and password resets
s = URLSafeTimedSerializer(app.config['SECRET_KEY'])

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)

class LogEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(50), nullable=False)
    activity = db.Column(db.Text, nullable=False)
    comment = db.Column(db.Text, nullable=True)

# --- AUTHENTICATION & VERIFICATION ROUTES ---

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        form_username = request.form['username']
        form_email = request.form['email']
        form_password = request.form['password']
        
        # Updated Regex: Now allows periods and other trailing characters
        password_pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).{8,}$"
        if not re.match(password_pattern, form_password):
            return "Password is too weak. Please go back."

        hashed_password = generate_password_hash(form_password)
        new_user = User(username=form_username, email=form_email, password=hashed_password)
        
        try:
            db.session.add(new_user)
            db.session.commit()
            
            token = s.dumps(form_email, salt='email-confirm')
            link = url_for('verify_email', token=token, _external=True)
            
            msg = Message('Verify your Digital Logbook Account', sender='noreply@logbook.com', recipients=[form_email])
            msg.body = f'Your verification link is {link}'
            mail.send(msg)
            
            return "Account created! Please check your email to verify your account before logging in."
        except Exception as e:
            return "Username or Email already exists. Please go back and try again."
            
    return render_template('register.html')

@app.route('/verify_email/<token>')
def verify_email(token):
    try:
        email = s.loads(token, salt='email-confirm', max_age=3600)
        user = User.query.filter_by(email=email).first_or_404()
        user.is_verified = True
        db.session.commit()
        return "Your email has been verified! <a href='/login'>Click here to login</a>."
    except SignatureExpired:
        return "The verification link has expired."
    except BadSignature:
        return "Invalid verification token."

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_username = request.form['username']
        login_password = request.form['password']
        user = User.query.filter_by(username=login_username).first()
        
        if user and check_password_hash(user.password, login_password):
            if not user.is_verified:
                return "Please check your email and verify your account before logging in."
            session['user_id'] = user.id
            return redirect('/logs')
        else:
            return "Invalid username or password."
    return render_template('login.html')

# --- PASSWORD RESET ROUTES ---

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first()
        if user:
            token = s.dumps(email, salt='password-reset')
            link = url_for('reset_password', token=token, _external=True)
            msg = Message('Reset Your Password', sender='noreply@logbook.com', recipients=[email])
            msg.body = f'Click here to reset your password: {link}'
            mail.send(msg)
        return "If that email exists in our system, a reset link has been sent."
    return render_template('forgot_password.html')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        email = s.loads(token, salt='password-reset', max_age=3600)
    except:
        return "The reset link is invalid or has expired."
        
    if request.method == 'POST':
        new_password = request.form['password']
        
        # Updated Regex for password reset to match registration
        password_pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).{8,}$"
        if not re.match(password_pattern, new_password):
            return "Password is too weak. Please go back."
            
        user = User.query.filter_by(email=email).first_or_404()
        user.password = generate_password_hash(new_password)
        db.session.commit()
        return "Password has been successfully updated! <a href='/login'>Login here</a>."
        
    return render_template('reset_password.html')

# --- LOGBOOK ROUTES ---

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/login')

@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('logbook.html')

@app.route('/submit', methods=['POST'])
def submit():
    if 'user_id' not in session:
        return redirect('/login')
    raw_date = request.form['date']
    formatted_date = datetime.strptime(raw_date, '%Y-%m-%d').strftime('%B %d, %Y')
    activity_submitted = request.form['activity']
    comment_submitted = request.form['comment']
    new_entry = LogEntry(date=formatted_date, activity=activity_submitted, comment=comment_submitted)
    db.session.add(new_entry)
    db.session.commit()
    return "Entry saved successfully! <a href='/logs'>View past logs</a>"

@app.route('/logs')
def view_logs():
    if 'user_id' not in session:
        return redirect('/login')
    search_query = request.args.get('query')
    if search_query:
        entries = LogEntry.query.filter(
            LogEntry.activity.contains(search_query) | LogEntry.date.contains(search_query) | LogEntry.comment.contains(search_query)
        ).all()
    else:
        entries = LogEntry.query.all()
    return render_template('logs.html', entries=entries, search_query=search_query)

@app.route('/delete/<int:id>')
def delete(id):
    if 'user_id' not in session:
        return redirect('/login')
    entry_to_delete = LogEntry.query.get_or_404(id)
    db.session.delete(entry_to_delete)
    db.session.commit()
    return redirect('/logs')

@app.route('/edit/<int:id>')
def edit(id):
    if 'user_id' not in session:
        return redirect('/login')
    entry_to_edit = LogEntry.query.get_or_404(id)
    return render_template('edit.html', entry=entry_to_edit)

@app.route('/update/<int:id>', methods=['POST'])
def update(id):
    if 'user_id' not in session:
        return redirect('/login')
    entry_to_update = LogEntry.query.get_or_404(id)
    entry_to_update.activity = request.form['activity']
    entry_to_update.comment = request.form['comment']
    db.session.commit()
    return redirect('/logs')

@app.route('/export')
def export_logs():
    if 'user_id' not in session:
        return redirect('/login')
    entries = LogEntry.query.all()
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for entry in entries:
        pdf.cell(200, 10, txt=f"Date: {entry.date}", ln=True)
        pdf.cell(200, 10, txt=f"Activity: {entry.activity}", ln=True)
        pdf.cell(200, 10, txt=f"Comment: {entry.comment}", ln=True)
        pdf.cell(200, 10, txt="", ln=True)
    return Response(pdf.output(dest='S').encode('latin-1'), mimetype="application/pdf", headers={"Content-disposition": "attachment; filename=my_logs.pdf"})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)