import os
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from datetime import timedelta
from flask_mail import Mail, Message
import uuid
import random
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon
import io
import base64
import sqlite3

app = Flask(__name__)
if not os.environ.get('SECRET_KEY'):
    raise ValueError("SECRET_KEY must be set in Replit Secrets")
app.secret_key = os.environ['SECRET_KEY']

# Basic security settings
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    PERMANENT_SESSION_LIFETIME=timedelta(days=30)
)

@app.after_request
def add_basic_security(response):
    # Allow YouTube embeds and essential content
    response.headers['Content-Security-Policy'] = "default-src 'self' 'unsafe-inline' 'unsafe-eval' https:; img-src 'self' data: https:; media-src 'self' https:; frame-src 'self' https://www.youtube.com"
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    
    # Store last visited page
    if request.endpoint and request.method == 'GET' and response.status_code == 200:
        excluded_routes = ['login', 'register', 'logout', 'static']
        if request.endpoint not in excluded_routes:
            session['last_page'] = request.url
            
    return response
app.permanent_session_lifetime = timedelta(days=30)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)

# Mail settings
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = os.environ['MAIL_USERNAME']  # Must be set in Replit Secrets
app.config['MAIL_PASSWORD'] = os.environ['MAIL_PASSWORD']  # Must be set in Replit Secrets
app.config['MAIL_DEFAULT_SENDER'] = os.environ['MAIL_USERNAME']
app.config['MAIL_MAX_EMAILS'] = None
app.config['MAIL_SUPPRESS_SEND'] = False
app.config['MAIL_ASCII_ATTACHMENTS'] = False
app.config['MAIL_DEBUG'] = True
app.config['MAIL_TIMEOUT'] = 10
app.config['TESTING'] = False
mail = Mail(app)

# Detailed mail debugging
print("Mail Configuration:")
print(f"Username: {app.config['MAIL_USERNAME']}")
print(f"Password length: {len(app.config['MAIL_PASSWORD']) if app.config['MAIL_PASSWORD'] else 0}")
print(f"Server: {app.config['MAIL_SERVER']}")
print(f"Port: {app.config['MAIL_PORT']}")
print(f"SSL: {app.config['MAIL_USE_SSL']}")

if not app.config['MAIL_USERNAME'] or not app.config['MAIL_PASSWORD']:
    print("Warning: Email credentials not set. Email features will not work.")

# Store registered users persistently
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    # Create users table
    c.execute('DROP TABLE IF EXISTS visits')
    c.execute('DROP TABLE IF EXISTS users')
    c.execute('''CREATE TABLE users
                 (email TEXT PRIMARY KEY, 
                  password TEXT, 
                  verified INTEGER DEFAULT 0, 
                  first_name TEXT,
                  last_name TEXT)''')
    # Create visits table
    c.execute('''CREATE TABLE visits
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  email TEXT,
                  page TEXT,
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                  notified INTEGER DEFAULT 0,
                  FOREIGN KEY(email) REFERENCES users(email))''')
    conn.commit()
    conn.close()

def check_and_send_analytics():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    # Count unnotified visits
    c.execute('SELECT COUNT(*) FROM visits WHERE notified = 0')
    unnotified_count = c.fetchone()[0]
    
    if unnotified_count >= 20:
        # Get analytics data
        c.execute('SELECT COUNT(DISTINCT email) FROM users')
        total_users = c.fetchone()[0]
        
        c.execute('SELECT COUNT(*) FROM visits')
        total_visits = c.fetchone()[0]
        
        c.execute('''SELECT page, COUNT(*) as count 
                     FROM visits 
                     GROUP BY page 
                     ORDER BY count DESC''')
        page_views = c.fetchall()
        
        # Prepare email content
        email_content = f'''
        <h2>CodeCraft Academy Analytics Update</h2>
        <p>Total Registered Users: {total_users}</p>
        <p>Total Page Visits: {total_visits}</p>
        <h3>Page Views:</h3>
        <ul>
        '''
        for page, count in page_views:
            email_content += f'<li>{page}: {count} views</li>'
        email_content += '</ul>'
        
        # Send email
        msg = Message('CodeCraft Academy Analytics Update',
                     sender=app.config['MAIL_USERNAME'],
                     recipients=['lilianjeripowers@gmail.com'])
        msg.html = email_content
        mail.send(msg)
        
        # Mark visits as notified
        c.execute('UPDATE visits SET notified = 1 WHERE notified = 0')
        conn.commit()
    
    conn.close()

init_db()

@app.route('/')
def home():
    try:
        if session.get('email'):
            conn = sqlite3.connect('users.db')
            c = conn.cursor()
            c.execute('SELECT * FROM users WHERE email = ?', (session['email'],))
            user = c.fetchone()
            
            if user:
                c.execute('INSERT INTO visits (email, page) VALUES (?, ?)', 
                         (session['email'], 'home'))
                conn.commit()
                check_and_send_analytics()
            conn.close()
            
        return render_template('home.html')
    except Exception as e:
        flash(str(e), 'error')
        return render_template('home.html')

@app.route('/analytics')
def analytics():
    # Only allow admin access
    if not session.get('logged_in') or session.get('email') != 'lilianjeripowers@gmail.com':
        return redirect(url_for('home'))
        
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    # Get total users
    c.execute('SELECT COUNT(*) FROM users')
    total_users = c.fetchone()[0]
    
    # Get total visits
    c.execute('SELECT COUNT(*) FROM visits')
    total_visits = c.fetchone()[0]
    
    # Get page views
    c.execute('''SELECT page, COUNT(*) as count 
                 FROM visits 
                 GROUP BY page 
                 ORDER BY count DESC''')
    page_views = c.fetchall()
    
    conn.close()
    
    return render_template('analytics.html', 
                         total_users=total_users,
                         total_visits=total_visits,
                         page_views=page_views)

@app.route('/editors')
def editors():
    if not session.get('logged_in'):
        flash('Please login first to access the editors page', 'warning')
        return redirect(url_for('login'))
    return render_template('editors.html')

@app.route('/treasure_hunt', methods=['GET', 'POST'])
def treasure_hunt():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    if 'treasure_level' not in session:
        session['treasure_level'] = 0
    if 'treasures' not in session:
        session['treasures'] = 0
    level = session.get('treasure_level', 0)
    
    if request.method == 'POST':
        code = request.form.get('code')
        treasures = int(session.get('treasures', 0))
        
        if code:
            session.permanent = True
            if 'completed_questions' not in session:
                session['completed_questions'] = []
            
            try:
                stripped_code = code.strip()
                level = session.get('treasure_level', 0)
                is_correct = False
                
                def normalize_code(code):
                    return ' '.join(code.split()).lower()
                
                normalized_code = normalize_code(stripped_code)
                level_validations = {
                    0: lambda c: "print('hello python!')" in c or 'print("hello python!")' in c,
                    1: lambda c: "age=25" in c.replace(" ", ""),
                    2: lambda c: any(x in c for x in ["str(42)", "num=42\nnum2=str(42)"]),
                    3: lambda c: any(x in c for x in ["f'i am learning python'", 'f"i am learning python"']),
                    4: lambda c: any(x in c.replace(" ", "") for x in ["x=15\ny=7\nz=x+y", "15+7", "7+15"]),
                    5: lambda c: "type(3.14)" in c.replace(" ", "") or "num=3.14\nprint(type(num))" in c.replace(" ", ""),
                    6: lambda c: any(x in c.replace(" ", "") for x in ["'python'.upper()", '"python".upper()', "text='python'\nuppercase_text=text.upper()"]),
                    7: lambda c: any(x in c.replace(" ", "") for x in ["'hello'+'world'", '"hello"+"world"', "text1='hello'\ntext2='world'\nresult=text1+text2"]),
                    8: lambda c: any(x in c.replace(" ", "") for x in ["int('123')", 'text="123"\ninteger_value=int(text)']),
                    9: lambda c: any(x in c.replace(" ", "") for x in ["float(10)", "number=10\nfloat_value=float(number)"])
                }
                
                if level in level_validations and level_validations[level](normalized_code):
                    is_correct = True
                    session['treasure_level'] = level + 1
                else:
                    is_correct = False
                    
                if is_correct and level not in session['completed_questions']:
                    treasures += 1
                    session['completed_questions'].append(level)
                    session['treasures'] = treasures
                    encouragements = [
                        "🎉 Excellent work! Keep up the great progress!",
                        "💫 You're doing amazing! Ready for the next challenge?",
                        "⭐ Perfect! You're mastering Python step by step!",
                        "🌟 Fantastic job! You're becoming a coding pro!",
                        "✨ Brilliant solution! On to new adventures!"
                    ]
                    encouragement = random.choice(encouragements)
                    response = f"""{encouragement} Treasures: {treasures} 💎
                    <script>
                    document.getElementById('treasureScore').textContent = {treasures};
                    </script>"""
                else:
                    response = "Try again! Your code isn't quite right."
            except Exception as e:
                response = "There was an error in your code. Try again!"
        else:
            response = "Please enter your code solution."
            
        return jsonify({"response": response})
        
    return render_template('treasure_hunt.html', level=level)

@app.route('/games', methods=['GET', 'POST'])
def games():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    # Initialize session variables if they don't exist
    if 'treasure_level' not in session:
        session['treasure_level'] = 0
    level = session.get('treasure_level', 0)
    if 'treasures' not in session:
        session['treasures'] = 0
    if 'rps_score' not in session:
        session['rps_score'] = 0
    if 'rps_streak' not in session:
        session['rps_streak'] = 0
    session.permanent = True
        
    if request.method == 'POST':
        game = request.form.get('game')
        if game == "conversation":
            name = request.form.get('name')
            response = f"Hello, {name}! Welcome to CodeCraft Academy. Let's start learning!"
            
        elif game == "guessing":
            number = random.randint(1, 10)
            guess = int(request.form.get('guess', 0))
            if guess == number:
                response = f"🎉 Congratulations! You guessed {number} correctly!"
            else:
                response = f"The number was {number}. Try again!"
                
        elif game == "math":
            num1 = int(request.form.get('num1', 0))
            num2 = int(request.form.get('num2', 0))
            answer = int(request.form.get('answer', 0))
            correct = num1 + num2
            if answer == correct:
                response = f"✨ Correct! {num1} + {num2} = {correct}"
            else:
                response = f"The correct answer was {correct}. Keep practicing!"
                
        elif game == "rock_paper_scissors":
            choices = ['rock', 'paper', 'scissors']
            player_choice = request.form.get('player_choice')
            computer_choice = random.choice(choices)
            
            score = session.get('rps_score', 0)
            streak = session.get('rps_streak', 0)
            
            if player_choice == computer_choice:
                response = f"It's a tie! Computer also chose {computer_choice}"
                streak = 0
            elif (player_choice == 'rock' and computer_choice == 'scissors') or \
                 (player_choice == 'paper' and computer_choice == 'rock') or \
                 (player_choice == 'scissors' and computer_choice == 'paper'):
                score += 1
                streak += 1
                response = f"""You win! Computer chose {computer_choice}. Score: {score}, Streak: {streak}🔥
                <script>
                document.getElementById('playerScore').textContent = {score};
                document.getElementById('playerStreak').textContent = {streak};
                </script>"""
            else:
                response = f"Computer wins with {computer_choice}!"
                streak = 0
                
            session['rps_score'] = score
            session['rps_streak'] = streak
                
        elif game == "shapes":
            shape = request.form.get('shape')
            color = request.form.get('color')
            
            plt.figure(figsize=(6, 6))
            ax = plt.gca()
            ax.set_xlim(-2, 2)
            ax.set_ylim(-2, 2)
            
            if shape == 'square':
                patch = Rectangle((-1, -1), 2, 2, color=color)
            elif shape == 'triangle':
                patch = Polygon([[0, 1], [-1, -1], [1, -1]], color=color)
            elif shape == 'circle':
                patch = plt.Circle((0, 0), 1, color=color)
            elif shape == 'star':
                vertices = [[0, 1], [0.2, 0.2], [1, 0.2], [0.4, -0.2], [0.6, -1], 
                          [0, -0.4], [-0.6, -1], [-0.4, -0.2], [-1, 0.2], [-0.2, 0.2]]
                patch = Polygon(vertices, color=color)
            elif shape == 'hexagon':
                import numpy as np
                angles = np.linspace(0, 2*np.pi, 7)[:-1]
                vertices = [[np.cos(angle), np.sin(angle)] for angle in angles]
                patch = Polygon(vertices, color=color)
            
            ax.add_patch(patch)
            ax.set_aspect('equal')
            ax.axis('off')
            
            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight')
            buf.seek(0)
            plt.close()
            
            image = base64.b64encode(buf.getvalue()).decode('utf-8')
            response = f'<img src="data:image/png;base64,{image}" alt="{color} {shape}">'
            
        elif game == "treasure_hunt":
            code = request.form.get('code')
            treasures = int(session.get('treasures', 0))
            completed_questions = session.get('completed_questions', [])
            
            if code:
                session.permanent = True
                if 'completed_questions' not in session:
                    session['completed_questions'] = []
                expected_outputs = {
                    0: "Hello Python!",
                    1: "25",
                    2: "str(42)",
                    3: "f'I am learning Python'",
                    4: "22",
                    5: "<class 'float'>",
                    6: "PYTHON",
                    7: "HelloWorld",
                    8: "123",
                    9: "10.0"
                }
                
                try:
                    stripped_code = code.strip()
                    level = int(request.form.get('level', 0))
                    is_correct = False
                    
                    def normalize_code(code):
                        return ' '.join(code.split()).lower()
                    
                    normalized_code = normalize_code(stripped_code)
                    level_validations = {
                        0: lambda c: "print('hello python!')" in c or 'print("hello python!")' in c,
                        1: lambda c: "age=25" in c.replace(" ", ""),
                        2: lambda c: any(x in c for x in ["str(42)", "num=42\nnum2=str(42)"]),
                        3: lambda c: any(x in c for x in ["f'i am learning python'", 'f"i am learning python"']),
                        4: lambda c: any(x in c.replace(" ", "") for x in ["x=15\ny=7\nz=x+y", "15+7", "7+15"]),
                        5: lambda c: "type(3.14)" in c.replace(" ", "") or "num=3.14\nprint(type(num))" in c.replace(" ", ""),
                        6: lambda c: any(x in c.replace(" ", "") for x in ["'python'.upper()", '"python".upper()', "text='python'\nuppercase_text=text.upper()"]),
                        7: lambda c: any(x in c.replace(" ", "") for x in ["'hello'+'world'", '"hello"+"world"', "text1='hello'\ntext2='world'\nresult=text1+text2"]),
                        8: lambda c: any(x in c.replace(" ", "") for x in ["int('123')", 'text="123"\ninteger_value=int(text)']),
                        9: lambda c: any(x in c.replace(" ", "") for x in ["float(10)", "number=10\nfloat_value=float(number)"])
                    }
                    
                    if level in level_validations and level_validations[level](normalized_code):
                        is_correct = True
                        session['treasure_level'] = level + 1
                    else:
                        is_correct = False
                        
                    if is_correct and level not in session['completed_questions']:
                        treasures += 1
                        session['completed_questions'].append(level)
                        session['treasures'] = treasures
                        encouragements = [
                            "🎉 Excellent work! Keep up the great progress!",
                            "💫 You're doing amazing! Ready for the next challenge?",
                            "⭐ Perfect! You're mastering Python step by step!",
                            "🌟 Fantastic job! You're becoming a coding pro!",
                            "✨ Brilliant solution! On to new adventures!"
                        ]
                        encouragement = random.choice(encouragements)
                        response = f"""{encouragement} Treasures: {treasures} 💎
                        <script>
                        document.getElementById('treasureScore').textContent = {treasures};
                        </script>"""
                    else:
                        response = "Try again! Your code isn't quite right."
                except Exception as e:
                    response = "There was an error in your code. Try again!"
            else:
                response = "Please enter your code solution."
                
        return jsonify({"response": response})
        
    return render_template('games.html', random=random, level=level)
    

@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('logged_in'):
        flash('You are already logged in!', 'info')
        return redirect(url_for('home'))
        
    if request.method == 'POST':
        email = request.form.get('mail')
        password = request.form.get('password')
        remember = request.form.get('remember')
        
        try:
            with sqlite3.connect('users.db', timeout=30) as conn:
                c = conn.cursor()
                c.execute('SELECT email, password, first_name FROM users WHERE email = ? COLLATE NOCASE', (email,))
                user = c.fetchone()
                
                if user:
                    from werkzeug.security import check_password_hash
                    if check_password_hash(user[1], password):
                        session.permanent = True if remember else False
                        session['logged_in'] = True
                        session['email'] = user[0]
                        session['first_name'] = user[2] if user[2] else email.split('@')[0]
                        flash('Login successful! Welcome back to CodeCraft Academy.', 'success')
                        return redirect(session.get('last_page', url_for('home')))
                    else:
                        flash('Incorrect password. Please try again.', 'error')
                else:
                    flash('Account not found. Creating a new account for you...', 'info')
                    # Store email in session for pre-filling registration form
                    session['temp_email'] = email
                    return redirect(url_for('register'))
                    
        except sqlite3.Error as e:
            print(f"Database error during login: {e}")
            flash('Unable to access user account. Please try again.', 'error')
        
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if session.get('logged_in'):
        flash('You already have an account and are logged in!', 'info')
        return redirect(url_for('home'))
        
    if request.method == 'POST':
        email = request.form.get('mail')
        password = request.form.get('password')
        
        if '@' not in email or '.' not in email:
            flash('Please enter a valid existing email address that you actively use.', 'error')
            return render_template('register.html')

        from werkzeug.security import generate_password_hash
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        
        try:
            with sqlite3.connect('users.db', timeout=20) as conn:
                c = conn.cursor()
                c.execute('SELECT * FROM users WHERE email = ?', (email,))
                if c.fetchone():
                    flash('This email is already registered. Please login to your existing account.', 'warning')
                    return redirect(url_for('login'))
                    
                first_name = request.form.get('fname')
                last_name = request.form.get('lname')
                c.execute('INSERT INTO users (email, password, first_name, last_name) VALUES (?, ?, ?, ?)', 
                         (email, hashed_password, first_name, last_name))
                conn.commit()
            flash('Registration successful! Please login to continue.')
            return redirect(url_for('login'))
        except Exception as e:
            flash(f'Error during registration: {str(e)}', 'error')
            return redirect(url_for('register'))
        
    return render_template('register.html')

@app.route('/logout')
def logout():
    if session.get('logged_in'):
        session.clear()
        flash('You have been successfully logged out. Come back soon!', 'info')
    return redirect(url_for('login'))

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = c.fetchone()
        conn.close()
        
        if user:
            # For demo purposes, we'll just redirect to reset password
            # In production, you would send an email with reset link
            session['reset_email'] = email
            flash('Please set your new password.', 'info')
            return redirect(url_for('reset_password'))
        else:
            flash('Email not found in our records.', 'error')
    
    return render_template('forgot_password.html')

@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return redirect(url_for('reset_password'))
            
        from werkzeug.security import generate_password_hash
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        
        email = session.get('reset_email')
        if email:
            conn = sqlite3.connect('users.db')
            c = conn.cursor()
            c.execute('UPDATE users SET password = ? WHERE email = ?', 
                     (hashed_password, email))
            conn.commit()
            conn.close()
            session.clear()
            flash('Password successfully reset! Please login with your new password.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Error resetting password. Please try again.', 'error')
    
    return render_template('reset_password.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/portfolio')
def portfolio():
    return render_template('portfolio.html')

@app.route('/pricing')
def pricing():
    return render_template('pricing.html')

@app.route('/tutorials')
def tutorials():
    if not session.get('logged_in'):
        flash('Please login first to access the tutorials page', 'warning')
        return redirect(url_for('login'))
    return render_template('tutorials.html')

@app.errorhandler(500)
def internal_error(error):
    return render_template('games.html'), 500

@app.route('/verify-email/<token>') #This route remains as it is, but will be effectively unused.
def verify_email(token):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    # Get user email for this token
    c.execute('SELECT email FROM users WHERE verification_token = ?', (token,))
    user = c.fetchone()
    
    if user:
        email = user[0]
        c.execute('UPDATE users SET verified = 1 WHERE verification_token = ?', (token,))
        conn.commit()
        
        # Send confirmation email to notify all devices
        confirm_msg = Message('Email Verification Successful - CodeCraft Academy',
                            sender=('CodeCraft Academy', app.config['MAIL_DEFAULT_SENDER']),
                            recipients=[email])
        confirm_msg.html = f'''
        <div style="max-width: 600px; margin: 0 auto; font-family: Arial, sans-serif;">
            <div style="background: linear-gradient(135deg, #4361ee, #3f37c9); padding: 20px; text-align: center;">
                <img src="data:image/svg+xml;base64,{base64.b64encode(open('static/logo.svg', 'rb').read()).decode()}" alt="CodeCraft Academy" style="width: 150px; max-width: 100%; height: auto; margin-bottom: 10px;">
                <h1 style="color: white; margin: 0;">CodeCraft Academy</h1>
                <p style="color: rgba(255,255,255,0.9); font-style: italic;">for Absolute Beginners</p>
            </div>
            <div style="padding: 30px; background: white; border-radius: 5px; margin-top: 20px;">
                <h2 style="color: #4361ee;">Email Verified Successfully!</h2>
                <p>Your email has been verified. You can now log in to CodeCraft Academy from any device.</p>
            </div>
        </div>
        '''
        mail.send(confirm_msg)
        flash('Email verified successfully! You can now login from any device.', 'success')
    else:
        flash('Invalid or expired verification link.', 'error')
    
    conn.close()
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000, threaded=True, use_reloader=True)