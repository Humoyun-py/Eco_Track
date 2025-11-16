from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
import json
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'eco-verse-2024-secret-key'

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "ecoverse.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database Modellar
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='child')
    coins = db.Column(db.Integer, default=0)
    energy = db.Column(db.Integer, default=100)
    streak = db.Column(db.Integer, default=0)
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class QuizResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    correct_answers = db.Column(db.Integer, nullable=False)
    total_questions = db.Column(db.Integer, nullable=False)
    coins_earned = db.Column(db.Integer, nullable=False)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='quiz_results')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Asosiy route'lar
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Xush kelibsiz!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Login yoki parol noto\'g\'ri!', 'error')
    
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)

# ML route'lari (yuqoridagi to'g'irlangan kod)
@app.route('/ml_quiz')
@login_required
def ml_quiz():
    return render_template('ml_quiz.html', user=current_user)

@app.route('/ml/get_questions')
@login_required
def get_questions():
    try:
        with open('ml_questions.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        all_questions = data['eco_questions']
        selected_questions = random.sample(all_questions, min(10, len(all_questions)))
        
        return jsonify({
            'success': True,
            'questions': selected_questions,
            'total': len(selected_questions)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Savollarni yuklashda xatolik: {str(e)}'
        })

@app.route('/ml/submit_quiz', methods=['POST'])
@login_required
def submit_quiz():
    try:
        data = request.get_json()
        results = data.get('results', [])
        score = data.get('score', 0)
        correct_count = data.get('correct_count', 0)
        total_questions = data.get('total_questions', 0)
        
        coins_earned = max(10, correct_count * 5)
        energy_cost = 20
        
        if current_user.energy < energy_cost:
            return jsonify({
                'success': False,
                'error': f'Energiya yetarli emas! Sizda {current_user.energy} energiya bor, kerak: {energy_cost}'
            })
        
        current_user.coins += coins_earned
        current_user.energy = max(0, current_user.energy - energy_cost)
        
        quiz_result = QuizResult(
            user_id=current_user.id,
            score=score,
            correct_answers=correct_count,
            total_questions=total_questions,
            coins_earned=coins_earned
        )
        
        db.session.add(quiz_result)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'score': score,
            'correct_answers': correct_count,
            'total_questions': total_questions,
            'coins_earned': coins_earned,
            'energy_used': energy_cost,
            'new_coins': current_user.coins,
            'new_energy': current_user.energy,
            'message': f'Test muvaffaqiyatli yakunlandi! {coins_earned} coin yutib oldingiz!'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Natijalarni saqlashda xatolik: {str(e)}'
        })

@app.route('/ml/quiz_history')
@login_required
def quiz_history():
    quiz_results = QuizResult.query.filter_by(user_id=current_user.id).order_by(QuizResult.completed_at.desc()).all()
    return render_template('quiz_history.html', 
                         quiz_results=quiz_results,
                         user=current_user)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)