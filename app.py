# app.py - TO'LIQ ECOVERSE ILOVASI
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
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

# DATABASE MODELLARI
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='child')
    coins = db.Column(db.Integer, default=0)
    energy = db.Column(db.Integer, default=100)
    streak = db.Column(db.Integer, default=0)
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    avatar = db.Column(db.String(200), default='default.png')
    is_admin = db.Column(db.Boolean, default=False)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    reward_coins = db.Column(db.Integer, default=10)
    energy_cost = db.Column(db.Integer, default=10)
    difficulty = db.Column(db.String(20), default='easy')
    quiz_required = db.Column(db.Boolean, default=True)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    item_type = db.Column(db.String(30), nullable=False)
    image_path = db.Column(db.String(200))
    energy_boost = db.Column(db.Integer, default=0)

class EnergyPack(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    energy_amount = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text)

class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    equipped = db.Column(db.Boolean, default=False)
    item = db.relationship('Item', backref='inventory_items')

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='active')
    likes_count = db.Column(db.Integer, default=0)
    author = db.relationship('User', backref=db.backref('user_posts', lazy=True))

class Story(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_path = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(hours=24))
    views_count = db.Column(db.Integer, default=0)
    author = db.relationship('User', backref=db.backref('user_stories', lazy=True))

class QuizResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    correct_answers = db.Column(db.Integer, nullable=False)
    total_questions = db.Column(db.Integer, nullable=False)
    coins_earned = db.Column(db.Integer, nullable=False)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=True)
    user = db.relationship('User', backref='quiz_results')
    task = db.relationship('Task', backref='quiz_results')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def init_database():
    with app.app_context():
        try:
            db.drop_all()
            db.create_all()
            create_demo_data()
            print("✅ Database yangilandi!")
        except Exception as e:
            print(f"❌ Database yangilashda xatolik: {e}")
            db.create_all()
            create_demo_data()
            print("✅ Database yaratildi!")

def create_demo_data():
    demo_tasks = [
        Task(title="Plastik idishlarni qayta ishlash", description="5 ta plastik idishni qayta ishlash markaziga olib boring", reward_coins=15, energy_cost=10, difficulty="easy", quiz_required=True),
        Task(title="Energiya tejash", description="1 kun davomida keraksiz chiroqlarni o'chiring", reward_coins=20, energy_cost=15, difficulty="medium", quiz_required=True),
        Task(title="Daraxt ekish", description="Yashil maydonga 1 ta daraxt eking", reward_coins=50, energy_cost=25, difficulty="hard", quiz_required=True),
    ]
    
    demo_items = [
        Item(name="Yashil Kepka", price=30, item_type="hat", image_path="images/hat_green.png"),
        Item(name="Ko'k Kepka", price=35, item_type="hat", image_path="images/hat_blue.png"),
        Item(name="Qizil Kepka", price=40, item_type="hat", image_path="images/hat_red.png"),
        Item(name="Yashil Futbolka", price=45, item_type="clothes", image_path="images/shirt_green.png"),
        Item(name="Ko'k Futbolka", price=50, item_type="clothes", image_path="images/shirt_blue.png"),
        Item(name="Qora Futbolka", price=55, item_type="clothes", image_path="images/shirt_black.png"),
        Item(name="Krossovka", price=60, item_type="shoes", image_path="images/shoes_sneakers.png"),
        Item(name="Qizil krossovka", price=65, item_type="shoes", image_path="images/shoes_red.png"),
        Item(name="Oq Krossovka", price=70, item_type="shoes", image_path="images/shoes_white.png"),    
        Item(name="Jins Shim", price=70, item_type="clothes", image_path="images/pants_jeans.png"),
        Item(name="Yashil Shim", price=75, item_type="clothes", image_path="images/pants_green.png"),
        Item(name="Rukzak", price=80, item_type="accessory", image_path="images/backpack.png"),
        Item(name="Quyosh ko'zoynak", price=85, item_type="accessory", image_path="images/sunglasses.png"),
        Item(name="Sport soati", price=90, item_type="accessory", image_path="images/sport_watch.png"),
    ]
    
    demo_energy_packs = [
        EnergyPack(name="Kichik Energiya Paketi", energy_amount=20, price=15, description="20 energiya"),
        EnergyPack(name="O'rta Energiya Paketi", energy_amount=50, price=35, description="50 energiya"),
        EnergyPack(name="Katta Energiya Paketi", energy_amount=100, price=60, description="100 energiya"),
    ]
    
    demo_users = [
        User(username='admin', email='admin@ecoverse.com', password_hash=generate_password_hash('admin123'), role='admin', coins=1000, is_admin=True),
        User(username='eco_bola', email='bola@ecoverse.com', password_hash=generate_password_hash('bola123'), role='child', coins=150),
        User(username='eco_katta', email='katta@ecoverse.com', password_hash=generate_password_hash('katta123'), role='adult', coins=80),
    ]
    
    for user in demo_users:
        db.session.add(user)
    for task in demo_tasks:
        db.session.add(task)
    for item in demo_items:
        db.session.add(item)
    for energy_pack in demo_energy_packs:
        db.session.add(energy_pack)
    
    db.session.commit()

# ML SAVOLLARNI JSON FAYLDAN O'QISH
def load_questions_from_json():
    try:
        with open('ml_questions.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print("⚠️  ml_questions.json fayli topilmadi! Demo savollar ishlatiladi.")
        return create_demo_questions()
    except json.JSONDecodeError as e:
        print(f"⚠️  JSON faylini o'qishda xatolik: {e}")
        return create_demo_questions()
    except Exception as e:
        print(f"⚠️  Xatolik: {e}")
        return create_demo_questions()

def create_demo_questions():
    """Agar ml_questions.json bo'lmasa, demo savollar yaratish"""
    return {
        "eco_questions": [
            {
                "id": 1,
                "question": "Qaysi material qayta ishlanishi eng oson?",
                "options": ["Plastik", "Shisha", "Alyuminiy", "Qog'oz"],
                "correct_answer": 3,
                "category": "Qayta ishlash",
                "difficulty": "Oson"
            },
            {
                "id": 2,
                "question": "Energiya tejash uchun qanday chiroq turi yaxshi?",
                "options": ["Lampa", "LED", "Neytron", "Halogen"],
                "correct_answer": 1,
                "category": "Energiya",
                "difficulty": "O'rta"
            },
            {
                "id": 3,
                "question": "Daraxtlar nima uchun muhim?",
                "options": ["Kulon olish", "Havoni tozalash", "Ovqat berish", "Sovutish"],
                "correct_answer": 1,
                "category": "Ekologiya",
                "difficulty": "Oson"
            },
            {
                "id": 4,
                "question": "Suvni tejash usuli?",
                "options": ["Dushda uzoq turish", "Kranni yopish", "Hammom qilish", "Suv ichish"],
                "correct_answer": 1,
                "category": "Suv",
                "difficulty": "O'rta"
            },
            {
                "id": 5,
                "question": "Qaysi transport ekologik toza?",
                "options": ["Avtomobil", "Velosiped", "Samolyot", "Poyezd"],
                "correct_answer": 1,
                "category": "Transport",
                "difficulty": "Oson"
            },
            {
                "id": 6,
                "question": "Kompost qanday tayyorlanadi?",
                "options": ["Plastik idishlar", "Oziq-ovqat chiqindilari", "Metall buyumlar", "Suv"],
                "correct_answer": 1,
                "category": "Kompost",
                "difficulty": "Qiyin"
            },
            {
                "id": 7,
                "question": "Qaysi energiya manbai qayta tiklanadi?",
                "options": ["Quyosh", "Neft", "Gaz", "Ko'mir"],
                "correct_answer": 0,
                "category": "Energiya",
                "difficulty": "O'rta"
            },
            {
                "id": 8,
                "question": "Atrof-muhitni ifloslantiruvchi gaz?",
                "options": ["Oksigen", "Azot", "Uglerod dioksid", "Geliy"],
                "correct_answer": 2,
                "category": "Havo",
                "difficulty": "Oson"
            },
            {
                "id": 9,
                "question": "Qaysi hayvon yo'qolib ketish xavfi ostida?",
                "options": ["It", "Mushuk", "Yo'lbars", "Sigir"],
                "correct_answer": 2,
                "category": "Hayvonot",
                "difficulty": "O'rta"
            },
            {
                "id": 10,
                "question": "Ekologik iz qoldirmaslik nima?",
                "options": ["Tabiatni buzmaslik", "Uy qurish", "Yo'l qurish", "Daraxt kesish"],
                "correct_answer": 0,
                "category": "Ekologiya",
                "difficulty": "Qiyin"
            },
            {
                "id": 11,
                "question": "Qaysi chiqindilar biologik parchalanishi mumkin?",
                "options": ["Plastik", "Metall", "Oziq-ovqat chiqindilari", "Shisha"],
                "correct_answer": 2,
                "category": "Chiqindilar",
                "difficulty": "Oson"
            },
            {
                "id": 12,
                "question": "Global isishga qaysi gaz sabab bo'ladi?",
                "options": ["Kislorod", "Uglerod dioksid", "Azot", "Vodorod"],
                "correct_answer": 1,
                "category": "Iqlim",
                "difficulty": "O'rta"
            },
            {
                "id": 13,
                "question": "Suvni tozalashda qaysi usul samarali?",
                "options": ["Xlorlash", "Quyosh energiyasi", "Filtrlash", "Quyultirish"],
                "correct_answer": 2,
                "category": "Suv",
                "difficulty": "O'rta"
            },
            {
                "id": 14,
                "question": "Qaysi energiya manbai eng toza?",
                "options": ["Quyosh", "Yadro", "Ko'mir", "Gaz"],
                "correct_answer": 0,
                "category": "Energiya",
                "difficulty": "Oson"
            },
            {
                "id": 15,
                "question": "O'rmonlarni qo'riqlash nima uchun muhim?",
                "options": ["Daraxtlar uchun", "Havo sifatini yaxshilash", "Yer osti suvlari uchun", "Barcha javoblar to'g'ri"],
                "correct_answer": 3,
                "category": "Ekologiya",
                "difficulty": "Qiyin"
            }
        ]
    }

# ASOSIY ROUTE'LAR
@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin_dashboard'))
        elif current_user.role == 'adult':
            return redirect(url_for('dashboard_adult'))
        else:
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
            today = datetime.now().date()
            if user.last_login:
                last_login_date = user.last_login.date()
                if last_login_date != today:
                    if (today - last_login_date).days == 1:
                        user.streak += 1
                    else:
                        user.streak = 1
            else:
                user.streak = 1
            
            user.last_login = datetime.utcnow()
            db.session.commit()
            login_user(user, remember=True)
            flash(f'Xush kelibsiz, {user.username}!', 'success')
            
            if user.is_admin:
                return redirect(url_for('admin_dashboard'))
            elif user.role == 'adult':
                return redirect(url_for('dashboard_adult'))
            else:
                return redirect(url_for('dashboard'))
        else:
            flash('Login yoki parol noto\'g\'ri!', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        
        if User.query.filter_by(username=username).first():
            flash('Bu foydalanuvchi nomi band!', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Bu email band!', 'error')
            return render_template('register.html')
        
        hashed_password = generate_password_hash(password)
        new_user = User(
            username=username, email=email, password_hash=hashed_password, role=role,
            coins=100 if role == 'child' else 50, energy=100, streak=0
        )
        
        db.session.add(new_user)
        db.session.commit()
        flash('Hisob muvaffaqiyatli yaratildi! Iltimos, tizimga kiring.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_admin:
        return redirect(url_for('admin_dashboard'))
    if current_user.role == 'adult':
        return redirect(url_for('dashboard_adult'))
    
    tasks = Task.query.all()
    items = Item.query.limit(6).all()
    energy_packs = EnergyPack.query.all()
    return render_template('dashboard_child.html', user=current_user, tasks=tasks, items=items, energy_packs=energy_packs)

# GAMES ROUTE'LARI
@app.route('/games')
@login_required
def games():
    """O'yinlar sahifasi"""
    # Foydalanuvchi statistikasini olish
    quiz_count = QuizResult.query.filter_by(user_id=current_user.id).count()
    
    return render_template('games.html', 
                         user=current_user, 
                         quiz_count=quiz_count)

@app.route('/games/recycling')
@login_required
def recycling_game():
    """Qayta ishlash o'yini"""
    flash('Bu oʻyin hozircha ishlab chiqilmoqda. Tez orada!', 'info')
    return redirect(url_for('games'))

@app.route('/games/energy_saving')
@login_required
def energy_saving_game():
    """Energiya tejash o'yini"""
    flash('Bu oʻyin hozircha ishlab chiqilmoqda. Tez orada!', 'info')
    return redirect(url_for('games'))

# ML TEST ROUTE'LARI
@app.route('/ml_quiz')
@login_required
def ml_quiz():
    task_id = request.args.get('task_id', type=int)
    task = None
    if task_id:
        task = Task.query.get(task_id)
    return render_template('ml_quiz.html', user=current_user, task=task)

@app.route('/ml/get_questions')
@login_required
def get_questions():
    try:
        # JSON fayldan savollarni o'qish
        data = load_questions_from_json()
        
        if 'eco_questions' not in data:
            return jsonify({
                'success': False,
                'error': 'JSON faylda eco_questions topilmadi!'
            })
        
        all_questions = data['eco_questions']
        
        if len(all_questions) == 0:
            return jsonify({
                'success': False,
                'error': 'JSON faylda savollar topilmadi!'
            })
        
        # Task ID bo'yicha qiyinlik darajasini aniqlash
        task_id = request.args.get('task_id', type=int)
        difficulty_filter = None
        
        if task_id:
            task = Task.query.get(task_id)
            if task:
                difficulty_filter = task.difficulty
                print(f"🔍 Task {task_id} uchun qiyinlik darajasi: {difficulty_filter}")
        
        # Qiyinlik darajasiga qarab savollarni filtrlash
        if difficulty_filter:
            # Qiyinlik darajasini moslashtirish
            difficulty_mapping = {
                'easy': ['Oson'],
                'medium': ['O\'rta', 'Ortacha'],
                'hard': ['Qiyin', 'Murakkab']
            }
            
            target_difficulties = difficulty_mapping.get(difficulty_filter.lower(), [difficulty_filter])
            filtered_questions = [q for q in all_questions if q.get('difficulty') in target_difficulties]
            
            if len(filtered_questions) > 0:
                all_questions = filtered_questions
                print(f"✅ {difficulty_filter} darajali {len(filtered_questions)} ta savol topildi")
            else:
                print(f"⚠️ {difficulty_filter} darajali savol topilmadi, barcha savollar ishlatiladi")
        
        # 10 ta tasodifiy savol tanlash (5 o'rniga 10)
        selected_questions = random.sample(all_questions, min(10, len(all_questions)))
        
        print(f"✅ {len(selected_questions)} ta savol yuklandi (qiyinlik: {difficulty_filter or 'barcha'})")
        
        return jsonify({
            'success': True,
            'questions': selected_questions,
            'total': len(selected_questions),
            'difficulty': difficulty_filter,
            'source': 'ml_questions.json'
        })
        
    except Exception as e:
        print(f"❌ Savollarni yuklashda xatolik: {str(e)}")
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
        task_id = data.get('task_id', None)
        
        # 10 ta savol uchun mukofotni oshirdim
        coins_earned = max(20, correct_count * 3)  # Har bir to'g'ri javob uchun 3 coin
        energy_cost = 25  # Energiya xarajatini oshirdim
        
        # Agar task_id bo'lsa, topshiriq uchun test
        task = None
        if task_id:
            task = Task.query.get(task_id)
            if task:
                # Topshiriqning qiyinlik darajasiga qarab mukofot
                if task.difficulty == 'easy':
                    coins_earned = task.reward_coins + 10
                elif task.difficulty == 'medium':
                    coins_earned = task.reward_coins + 15
                elif task.difficulty == 'hard':
                    coins_earned = task.reward_coins + 20
        
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
            coins_earned=coins_earned,
            task_id=task_id
        )
        
        db.session.add(quiz_result)
        db.session.commit()
        
        message = f'Test muvaffaqiyatli yakunlandi! {correct_count}/{total_questions} savolga to\'g\'ri javob berdingiz. {coins_earned} coin yutib oldingiz!'
        if task:
            message += f' "{task.title}" topshirig\'i uchun test tamomlandi!'
        
        return jsonify({
            'success': True,
            'score': score,
            'correct_answers': correct_count,
            'total_questions': total_questions,
            'coins_earned': coins_earned,
            'energy_used': energy_cost,
            'new_coins': current_user.coins,
            'new_energy': current_user.energy,
            'task_completed': bool(task),
            'message': message
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Natijalarni saqlashda xatolik: {str(e)}'
        })

# API ROUTE'LARI
@app.route('/start_task_quiz/<int:task_id>')
@login_required
def start_task_quiz(task_id):
    """Topshiriq uchun testni boshlash"""
    if current_user.role != 'child':
        flash('Faqat bolalar uchun!', 'error')
        return redirect(url_for('dashboard'))
    
    task = Task.query.get_or_404(task_id)
    
    if current_user.energy < task.energy_cost:
        flash(f'Energiya yetarli emas! Sizda {current_user.energy} energiya bor, kerak: {task.energy_cost}', 'error')
        return redirect(url_for('dashboard'))
    
    return redirect(url_for('ml_quiz', task_id=task_id))

@app.route('/complete_task/<int:task_id>', methods=['POST'])
@login_required
def complete_task(task_id):
    if current_user.role != 'child':
        return jsonify({'success': False, 'error': 'Faqat bolalar uchun'})
    
    task = Task.query.get_or_404(task_id)
    
    # Agar test talab qilinsa, test natijasini tekshirish
    if task.quiz_required:
        latest_quiz = QuizResult.query.filter_by(
            user_id=current_user.id, 
            task_id=task_id
        ).order_by(QuizResult.completed_at.desc()).first()
        
        if not latest_quiz:
            return jsonify({
                'success': False, 
                'error': 'Avval topshiriq uchun testni topshiring!',
                'quiz_required': True
            })
    
    if current_user.energy >= task.energy_cost:
        current_user.coins += task.reward_coins
        current_user.energy = max(0, current_user.energy - task.energy_cost)
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'coins': current_user.coins,
            'energy': current_user.energy,
            'message': f'Topshiriq bajarildi! +{task.reward_coins} coin, -{task.energy_cost} energiya'
        })
    
    return jsonify({'success': False, 'error': f'Energiya yetarli emas! Sizda {current_user.energy} energiya bor, kerak: {task.energy_cost}'})

@app.route('/buy_item/<int:item_id>', methods=['POST'])
@login_required
def buy_item(item_id):
    item = Item.query.get_or_404(item_id)
    
    if current_user.coins >= item.price:
        current_user.coins -= item.price
        
        if item.energy_boost > 0:
            current_user.energy += item.energy_boost
        
        new_inventory = Inventory(user_id=current_user.id, item_id=item.id)
        db.session.add(new_inventory)
        db.session.commit()
        
        message = f'{item.name} sotib olindi!'
        if item.energy_boost > 0:
            message += f' +{item.energy_boost} energiya'
        
        return jsonify({
            'success': True,
            'coins': current_user.coins,
            'energy': current_user.energy,
            'message': message
        })
    
    return jsonify({'success': False, 'error': 'Coin yetarli emas!'})

@app.route('/buy_energy', methods=['POST'])
@login_required
def buy_energy():
    try:
        data = request.get_json()
        energy_amount = data.get('energy', 0)
        price = data.get('price', 0)
        
        if current_user.coins >= price:
            current_user.coins -= price
            current_user.energy += energy_amount
            db.session.commit()
            
            return jsonify({
                'success': True,
                'coins': current_user.coins,
                'energy': current_user.energy,
                'message': f'Energiya sotib olindi! +{energy_amount} energiya'
            })
        
        return jsonify({'success': False, 'error': 'Coin yetarli emas!'})
    
    except Exception as e:
        return jsonify({'success': False, 'error': f'Xatolik: {str(e)}'})

@app.route('/check_energy/<int:energy_needed>')
@login_required
def check_energy(energy_needed):
    has_enough = current_user.energy >= energy_needed
    return jsonify({
        'has_enough': has_enough,
        'current_energy': current_user.energy,
        'energy_needed': energy_needed
    })

@app.route('/get_user_stats')
@login_required
def get_user_stats():
    return jsonify({
        'success': True,
        'coins': current_user.coins,
        'energy': current_user.energy,
        'streak': current_user.streak
    })

# ADMIN ROUTE'LARI (soddalashtirilgan)
@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('Sizga admin huquqi berilmagan!', 'error')
        return redirect(url_for('dashboard'))
    return render_template('admin_dashboard.html', user=current_user)

@app.route('/admin/login')
def admin_login():
    if current_user.is_authenticated and current_user.is_admin:
        return redirect(url_for('admin_dashboard'))
    return render_template('admin_login.html')

# BOSHQALAR ROUTE'LARI
@app.route('/leaderboard')
@login_required
def leaderboard():
    return render_template('leaderboard.html', user=current_user)

@app.route('/news')
@login_required
def news():
    return render_template('news.html', user=current_user)

@app.route('/missions')
@login_required
def missions():
    return render_template('missions.html', user=current_user)

@app.route('/stories')
@login_required
def stories():
    return render_template('stories.html', user=current_user)

@app.route('/shop')
@login_required
def shop():
    items = Item.query.all()
    energy_packs = EnergyPack.query.all()
    return render_template('shop.html', user=current_user, items=items, energy_packs=energy_packs)

@app.route('/hero')
@login_required
def hero():
    return render_template('hero.html', user=current_user)

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

@app.route('/posts')
@login_required
def posts():
    return render_template('posts.html', user=current_user)

@app.route('/messages')
@login_required
def messages():
    return render_template('messages.html', user=current_user)

@app.route('/dashboard_adult')
@login_required
def dashboard_adult():
    if current_user.role != 'adult':
        flash('Bu sahifa faqat kattalar uchun!', 'error')
        return redirect(url_for('dashboard'))
    return render_template('dashboard_adult.html', user=current_user)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Siz tizimdan chiqdingiz!', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_database()
    
    # ML savollarini yuklashni tekshirish
    questions_data = load_questions_from_json()
    question_count = len(questions_data.get('eco_questions', []))
    print(f"📚 ML savollari yuklandi: {question_count} ta savol")
    
    print("\n🎉 EcoVerse tizimi ishga tushdi!")
    print("📍 Asosiy sahifa: http://localhost:5000")
    print("👨‍💼 Admin panel: http://localhost:5000/admin/dashboard")
    print("🎮 O'yinlar: http://localhost:5000/games")
    print("🧠 Test: http://localhost:5000/ml_quiz")
    print("\n📋 Demo loginlar:")
    print("   👨‍💼 Admin: admin / admin123")
    print("   👦 Bola: eco_bola / bola123") 
    print("   👨 Katta: eco_katta / katta123")
    
    app.run(debug=True, host='0.0.0.0', port=5000)