# app.py - TO'LIQ YANGILANGAN KOD
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'eco-verse-2024-secret-key'

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "ecoverse_fixed.db")}'
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

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    item_type = db.Column(db.String(30), nullable=False)
    image_path = db.Column(db.String(200))
    energy_boost = db.Column(db.Integer, default=0)

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

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)
    
    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_messages')

class GameSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    game_type = db.Column(db.String(50), nullable=False)
    score = db.Column(db.Integer, default=0)
    coins_earned = db.Column(db.Integer, default=0)
    played_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='game_sessions')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def init_database():
    with app.app_context():
        db.create_all()
        if not User.query.first():
            create_demo_data()
            print("✅ Database yaratildi!")

def create_demo_data():
    demo_tasks = [
        Task(title="Plastik idishlarni qayta ishlash", 
             description="5 ta plastik idishni qayta ishlash markaziga olib boring",
             reward_coins=15, energy_cost=10, difficulty="easy"),
        Task(title="Energiya tejash", 
             description="1 kun davomida keraksiz chiroqlarni o'chiring",
             reward_coins=20, energy_cost=15, difficulty="medium"),
        Task(title="Daraxt ekish", 
             description="Yashil maydonga 1 ta daraxt eking",
             reward_coins=50, energy_cost=25, difficulty="hard"),
    ]
    
    demo_items = [
        Item(name="Yashil Kepka", price=30, item_type="hat", image_path="images/hat_green.png"),
        Item(name="Ko'k Kepka", price=35, item_type="hat", image_path="images/hat_blue.png"),
        Item(name="Yashil Futbolka", price=45, item_type="clothes", image_path="images/shirt_green.png"),
        Item(name="Ko'k Futbolka", price=50, item_type="clothes", image_path="images/shirt_blue.png"),
        Item(name="Jins Shim", price=60, item_type="clothes", image_path="images/pants_jeans.png"),
        Item(name="Oq Krossovka", price=80, item_type="shoes", image_path="images/shoes_sneakers.png"),
        Item(name="Eco Rukzak", price=75, item_type="accessory", image_path="images/bag_backpack.png"),
        Item(name="Energiya Ichimlik", price=25, item_type="energy", image_path="images/energy_drink.png", energy_boost=20),
        Item(name="O'rmon Fon", price=100, item_type="background", image_path="images/bg_forest.png"),
    ]
    
    demo_users = [
        User(username='admin', email='admin@ecoverse.com', 
             password_hash=generate_password_hash('admin123'), role='admin', coins=1000, is_admin=True),
        User(username='eco_bola', email='bola@ecoverse.com', 
             password_hash=generate_password_hash('bola123'), role='child', coins=150),
        User(username='eco_katta', email='katta@ecoverse.com', 
             password_hash=generate_password_hash('katta123'), role='adult', coins=80),
    ]
    
    for user in demo_users:
        db.session.add(user)
    db.session.commit()
    
    demo_posts = [
        Post(user_id=2, title="Yashil energiya", 
             content="Quyosh energiyasidan foydalaning!", category="Eko-maslahat"),
        Post(user_id=3, title="Daraxt ekish", 
             content="Har kishi daraxt ekishi kerak.", category="Volunteer event"),
    ]
    
    demo_stories = [
        Story(user_id=2, title="Mening birinchi daraxtim", 
              content="Bugun men birinchi marta daraxt ekdim!", 
              image_path="images/story_tree.jpg"),
    ]
    
    for task in demo_tasks:
        db.session.add(task)
    for item in demo_items:
        db.session.add(item)
    for post in demo_posts:
        db.session.add(post)
    for story in demo_stories:
        db.session.add(story)
    
    db.session.commit()

# YANGILANGAN LOGIN FUNKSIYASI
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin_dashboard'))
        elif current_user.role == 'child':
            return redirect(url_for('dashboard'))
        elif current_user.role == 'adult':
            return redirect(url_for('dashboard_adult'))
        else:
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
            username=username,
            email=email,
            password_hash=hashed_password,
            role=role,
            coins=100 if role == 'child' else 50,
            energy=100,
            streak=0
        )
        
        db.session.add(new_user)
        db.session.commit()
        flash('Hisob muvaffaqiyatli yaratildi! Iltimos, tizimga kiring.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

# YANGI: Kattalar uchun alohida dashboard route'i
@app.route('/dashboard_adult')
@login_required
def dashboard_adult():
    if current_user.is_admin:
        return redirect(url_for('admin_dashboard'))
    elif current_user.role == 'child':
        return redirect(url_for('dashboard'))
    
    posts = Post.query.filter_by(status='active').order_by(Post.date.desc()).limit(5).all()
    return render_template('dashboard_adult.html', user=current_user, posts=posts)

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_admin:
        return redirect(url_for('admin_dashboard'))
    
    if current_user.role == 'adult':
        return redirect(url_for('dashboard_adult'))
    
    tasks = Task.query.all()
    items = Item.query.limit(6).all()
    return render_template('dashboard_child.html', 
                         user=current_user,
                         tasks=tasks,
                         items=items)

# Admin route'lari
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated and current_user.is_admin:
        return redirect(url_for('admin_dashboard'))
        
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username, is_admin=True).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user, remember=True)
            flash('Admin panelga xush kelibsiz!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Admin login yoki parol noto\'g\'ri!', 'error')
    
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('Siz admin emassiz!', 'error')
        return redirect(url_for('dashboard'))
    
    total_users = User.query.count()
    total_child_users = User.query.filter_by(role='child').count()
    total_adult_users = User.query.filter_by(role='adult').count()
    total_posts = Post.query.count()
    total_tasks = Task.query.count()
    total_items = Item.query.count()
    
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_posts = Post.query.order_by(Post.date.desc()).limit(5).all()
    
    return render_template('admin_dashboard.html',
                         total_users=total_users,
                         total_child_users=total_child_users,
                         total_adult_users=total_adult_users,
                         total_posts=total_posts,
                         total_tasks=total_tasks,
                         total_items=total_items,
                         recent_users=recent_users,
                         recent_posts=recent_posts,
                         current_user=current_user)

@app.route('/admin/users')
@login_required
def admin_users():
    if not current_user.is_admin:
        flash('Siz admin emassiz!', 'error')
        return redirect(url_for('dashboard'))
    
    users = User.query.all()
    return render_template('admin_users.html', users=users, current_user=current_user)

@app.route('/admin/child')
@login_required
def admin_child():
    if not current_user.is_admin:
        flash('Siz admin emassiz!', 'error')
        return redirect(url_for('dashboard'))
    
    child_users = User.query.filter_by(role='child').all()
    tasks = Task.query.all()
    items = Item.query.all()
    
    return render_template('admin_child.html',
                         child_users=child_users,
                         tasks=tasks,
                         items=items,
                         current_user=current_user)

@app.route('/admin/adult')
@login_required
def admin_adult():
    if not current_user.is_admin:
        flash('Siz admin emassiz!', 'error')
        return redirect(url_for('dashboard'))
    
    adult_users = User.query.filter_by(role='adult').all()
    posts = Post.query.order_by(Post.date.desc()).all()
    
    return render_template('admin_adult.html',
                         adult_users=adult_users,
                         posts=posts,
                         current_user=current_user)

@app.route('/admin/shop')
@login_required
def admin_shop():
    if not current_user.is_admin:
        flash('Siz admin emassiz!', 'error')
        return redirect(url_for('dashboard'))
    
    items = Item.query.all()
    return render_template('admin_shop.html', items=items, current_user=current_user)

@app.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for('admin_login'))

# YANGI: Post statusini yangilash API
@app.route('/admin/update_post_status/<int:post_id>', methods=['POST'])
@login_required
def admin_update_post_status(post_id):
    if not current_user.is_admin:
        return jsonify({'success': False, 'error': 'Admin huquqi kerak!'})
    
    data = request.get_json()
    new_status = data.get('status')
    
    post = Post.query.get_or_404(post_id)
    post.status = new_status
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Post statusi yangilandi!'})

# YANGI: Post o'chirish API
@app.route('/admin/delete_post/<int:post_id>', methods=['POST'])
@login_required
def admin_delete_post(post_id):
    if not current_user.is_admin:
        return jsonify({'success': False, 'error': 'Admin huquqi kerak!'})
    
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Post muvaffaqiyatli o\'chirildi!'})

# Admin API Route'lar
@app.route('/admin/update_user_coins/<int:user_id>', methods=['POST'])
@login_required
def admin_update_user_coins(user_id):
    if not current_user.is_admin:
        return jsonify({'success': False, 'error': 'Admin huquqi kerak!'})
    
    data = request.get_json()
    new_coins = data.get('coins')
    
    user = User.query.get_or_404(user_id)
    user.coins = new_coins
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Coinlar yangilandi!'})

@app.route('/admin/update_user_energy/<int:user_id>', methods=['POST'])
@login_required
def admin_update_user_energy(user_id):
    if not current_user.is_admin:
        return jsonify({'success': False, 'error': 'Admin huquqi kerak!'})
    
    data = request.get_json()
    new_energy = data.get('energy')
    
    user = User.query.get_or_404(user_id)
    user.energy = new_energy
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Energiya yangilandi!'})

@app.route('/admin/add_task', methods=['POST'])
@login_required
def admin_add_task():
    if not current_user.is_admin:
        return jsonify({'success': False, 'error': 'Admin huquqi kerak!'})
    
    data = request.get_json()
    new_task = Task(
        title=data.get('title'),
        description=data.get('description'),
        reward_coins=data.get('reward_coins', 10),
        energy_cost=data.get('energy_cost', 10),
        difficulty=data.get('difficulty', 'easy')
    )
    
    db.session.add(new_task)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Topshiriq qo\'shildi!'})

@app.route('/admin/delete_task/<int:task_id>', methods=['POST'])
@login_required
def admin_delete_task(task_id):
    if not current_user.is_admin:
        return jsonify({'success': False, 'error': 'Admin huquqi kerak!'})
    
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Topshiriq o\'chirildi!'})

# Asosiy Route'lar
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

# YANGI: Barcha sahifalar uchun route'lar
@app.route('/shop')
@login_required
def shop():
    items = Item.query.all()
    return render_template('shop.html', items=items, user=current_user)

@app.route('/hero')
@login_required
def hero():
    inventory = Inventory.query.filter_by(user_id=current_user.id).all()
    equipped_items = Inventory.query.filter_by(user_id=current_user.id, equipped=True).all()
    
    equipped_clothes = [inv for inv in equipped_items if inv.item.item_type == 'clothes']
    equipped_hat = [inv for inv in equipped_items if inv.item.item_type == 'hat']
    equipped_shoes = [inv for inv in equipped_items if inv.item.item_type == 'shoes']
    equipped_accessory = [inv for inv in equipped_items if inv.item.item_type == 'accessory']
    
    clothes_items = [inv for inv in inventory if inv.item.item_type == 'clothes']
    accessory_items = [inv for inv in inventory if inv.item.item_type == 'accessory']
    hat_items = [inv for inv in inventory if inv.item.item_type == 'hat']
    shoe_items = [inv for inv in inventory if inv.item.item_type == 'shoes']
    background_items = [inv for inv in inventory if inv.item.item_type == 'background']
    
    return render_template('hero.html', 
                         inventory=inventory,
                         equipped_items=equipped_items,
                         equipped_clothes=equipped_clothes,
                         equipped_hat=equipped_hat,
                         equipped_shoes=equipped_shoes,
                         equipped_accessory=equipped_accessory,
                         clothes_items=clothes_items,
                         accessory_items=accessory_items,
                         hat_items=hat_items,
                         shoe_items=shoe_items,
                         background_items=background_items,
                         user=current_user)

@app.route('/posts')
@login_required
def posts():
    all_posts = Post.query.filter_by(status='active').order_by(Post.date.desc()).all()
    return render_template('posts.html', posts=all_posts, user=current_user)

@app.route('/post_detail/<int:post_id>')
@login_required
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post_detail.html', post=post, user=current_user)

@app.route('/messages')
@login_required
def messages():
    users = User.query.filter(User.id != current_user.id).all()
    return render_template('messages.html', users=users, user=current_user)

@app.route('/games')
@login_required
def games():
    return render_template('games.html', user=current_user)

@app.route('/leaderboard')
@login_required
def leaderboard():
    users = User.query.order_by(User.coins.desc()).limit(10).all()
    return render_template('leaderboard.html', users=users, user=current_user)

@app.route('/news')
@login_required
def news():
    return render_template('news.html', user=current_user)

@app.route('/missions')
@login_required
def missions():
    tasks = Task.query.all()
    return render_template('missions.html', tasks=tasks, user=current_user)

@app.route('/eco_tips')
@login_required
def eco_tips():
    return render_template('eco_tips.html', user=current_user)

@app.route('/achievements')
@login_required
def achievements():
    return render_template('achievements.html', user=current_user)

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

@app.route('/stories')
@login_required
def stories():
    active_stories = Story.query.filter(Story.expires_at > datetime.utcnow()).order_by(Story.created_at.desc()).all()
    total_views = db.session.query(db.func.sum(Story.views_count)).scalar() or 0
    popular_story = Story.query.order_by(Story.views_count.desc()).first()
    
    return render_template('stories.html', 
                         stories=active_stories,
                         total_views=total_views,
                         popular_story=popular_story,
                         now=datetime.utcnow(),
                         user=current_user)

# YANGI: Stories uchun API route'lar
@app.route('/create_story', methods=['POST'])
@login_required
def create_story():
    if current_user.role != 'adult':
        return jsonify({'success': False, 'error': 'Faqat kattalar story yaratishi mumkin!'})
    
    title = request.form['title']
    content = request.form['content']
    image = request.files.get('image')
    
    image_path = None
    if image:
        filename = f"story_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{image.filename}"
        image_path = f"images/stories/{filename}"
        image.save(os.path.join('static', image_path))
    
    new_story = Story(
        user_id=current_user.id,
        title=title,
        content=content,
        image_path=image_path
    )
    
    db.session.add(new_story)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Story muvaffaqiyatli yaratildi!'})

@app.route('/view_story/<int:story_id>', methods=['POST'])
@login_required
def view_story(story_id):
    story = Story.query.get_or_404(story_id)
    story.views_count += 1
    db.session.commit()
    
    return jsonify({'success': True, 'views_count': story.views_count})

# YANGI: O'yinlar uchun API route'lar
@app.route('/play_game/<game_type>', methods=['POST'])
@login_required
def play_game(game_type):
    if current_user.energy < 10:
        return jsonify({'success': False, 'error': 'Energiya yetarli emas!'})
    
    # O'yin natijasini hisoblash
    score = 50 + (current_user.streak * 5)  # Streak ga qarab score
    coins_earned = 10 + (score // 10)
    
    # Energiya sarflash
    current_user.energy = max(0, current_user.energy - 10)
    current_user.coins += coins_earned
    
    # O'yin sessiyasini saqlash
    game_session = GameSession(
        user_id=current_user.id,
        game_type=game_type,
        score=score,
        coins_earned=coins_earned
    )
    
    db.session.add(game_session)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'score': score,
        'coins_earned': coins_earned,
        'energy': current_user.energy,
        'coins': current_user.coins,
        'message': f'O\'yin yakunlandi! {coins_earned} coin yutib oldingiz!'
    })

# YANGI: Xabarlar uchun API route'lar
@app.route('/send_message', methods=['POST'])
@login_required
def send_message():
    data = request.get_json()
    receiver_id = data.get('receiver_id')
    content = data.get('content')
    
    if not content or not receiver_id:
        return jsonify({'success': False, 'error': 'Xabar va qabul qiluvchi kerak!'})
    
    receiver = User.query.get(receiver_id)
    if not receiver:
        return jsonify({'success': False, 'error': 'Qabul qiluvchi topilmadi!'})
    
    new_message = Message(
        sender_id=current_user.id,
        receiver_id=receiver_id,
        content=content
    )
    
    db.session.add(new_message)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Xabar yuborildi!'})

@app.route('/get_messages/<int:user_id>')
@login_required
def get_messages(user_id):
    messages = Message.query.filter(
        ((Message.sender_id == current_user.id) & (Message.receiver_id == user_id)) |
        ((Message.sender_id == user_id) & (Message.receiver_id == current_user.id))
    ).order_by(Message.timestamp.asc()).all()
    
    messages_data = []
    for msg in messages:
        messages_data.append({
            'id': msg.id,
            'sender_id': msg.sender_id,
            'sender_name': msg.sender.username,
            'content': msg.content,
            'timestamp': msg.timestamp.strftime('%H:%M'),
            'is_sent': msg.sender_id == current_user.id
        })
    
    return jsonify({'success': True, 'messages': messages_data})

# Mavjud API route'lar
@app.route('/complete_task/<int:task_id>', methods=['POST'])
@login_required
def complete_task(task_id):
    if current_user.role != 'child':
        return jsonify({'success': False, 'error': 'Faqat bolalar uchun'})
    
    task = Task.query.get_or_404(task_id)
    
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
            current_user.energy = min(100, current_user.energy + item.energy_boost)
        
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
    data = request.get_json()
    energy_amount = int(data.get('energy', 50))
    price = int(data.get('price', 25))
    
    if current_user.coins < price:
        return jsonify({'success': False, 'error': 'Coin yetarli emas!'})
    
    current_user.coins -= price
    current_user.energy += energy_amount
    db.session.commit()
    
    return jsonify({
        'success': True, 
        'message': f'{energy_amount} energiya sotib olindi!',
        'coins': current_user.coins,
        'energy': current_user.energy
    })

@app.route('/equip_item/<int:item_id>', methods=['POST'])
@login_required
def equip_item(item_id):
    inventory_item = Inventory.query.filter_by(id=item_id, user_id=current_user.id).first()
    
    if not inventory_item:
        return jsonify({'success': False, 'error': 'Item topilmadi!'})
    
    same_type_items = Inventory.query.filter_by(
        user_id=current_user.id, 
        equipped=True
    ).join(Item).filter(Item.item_type == inventory_item.item.item_type).all()
    
    for item in same_type_items:
        item.equipped = False
    
    inventory_item.equipped = True
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'{inventory_item.item.name} muvaffaqiyatli kiyildi!'
    })

@app.route('/unequip_item/<int:item_id>', methods=['POST'])
@login_required
def unequip_item(item_id):
    inventory_item = Inventory.query.filter_by(id=item_id, user_id=current_user.id).first()
    
    if not inventory_item:
        return jsonify({'success': False, 'error': 'Item topilmadi!'})
    
    inventory_item.equipped = False
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'{inventory_item.item.name} muvaffaqiyatli echildi!'
    })

@app.route('/create_post', methods=['POST'])
@login_required
def create_post():
    if current_user.role != 'adult':
        return jsonify({'success': False, 'error': 'Faqat kattalar uchun'})
    
    title = request.form['title']
    content = request.form['content']
    category = request.form['category']
    
    new_post = Post(
        user_id=current_user.id,
        title=title,
        content=content,
        category=category,
        status='active'
    )
    
    db.session.add(new_post)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Post muvaffaqiyatli yaratildi!'})

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Siz tizimdan chiqdingiz!', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_database()
    
    print("\n🎉 EcoVerse tizimi ishga tushdi!")
    print("📍 Asosiy sahifa: http://localhost:5000")
    print("👨‍💼 Admin panel: http://localhost:5000/admin/login")
    print("\n📋 Demo loginlar:")
    print("   👨‍💼 Admin: admin / admin123")
    print("   👦 Bola: eco_bola / bola123") 
    print("   👨 Katta: eco_katta / katta123")
    
    app.run(debug=True, host='0.0.0.0', port=5000)