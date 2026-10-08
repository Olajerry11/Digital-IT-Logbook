from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Configure the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///logbook.db'
db = SQLAlchemy(app)

# Define the database blueprint (Model)
class LogEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(50), nullable=False)
    activity = db.Column(db.Text, nullable=False)
    comment = db.Column(db.Text, nullable=True)

@app.route('/')
def home():
    return render_template('logbook.html')

@app.route('/submit', methods=['POST'])
def submit():
    # Grab the data from the HTML form
    raw_date = request.form['date']
    
    # Format the date
    formatted_date = datetime.strptime(raw_date, '%Y-%m-%d').strftime('%B %d, %Y')
    
    activity_submitted = request.form['activity']
    comment_submitted = request.form['comment']
    
    # Package all three into the database entry using the formatted date
    new_entry = LogEntry(date=formatted_date, activity=activity_submitted, comment=comment_submitted)
    db.session.add(new_entry)
    db.session.commit()
    
    return "Entry saved to database successfully! <br><br> <a href='/logs'>View your past logs here</a>"

@app.route('/logs')
def view_logs():
    entries = LogEntry.query.all()
    return render_template('logs.html', entries=entries)

# New route to handle deleting an entry
@app.route('/delete/<int:id>')
def delete(id):
    entry_to_delete = LogEntry.query.get_or_404(id)
    db.session.delete(entry_to_delete)
    db.session.commit()
    return redirect('/logs')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)