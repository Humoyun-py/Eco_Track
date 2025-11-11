from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import sqlite3
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'eco-verse-secret-key-2024'

# Database faylini aniq path bilan belgilash
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "eco_verse.db")}'
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
    
    posts = db.relationship('Post', backref='author', lazy=True)
    comments = db.relationship('Comment', backref='author', lazy=True)
    likes = db.relationship('PostLike', backref='user', lazy=True)

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
    
    comments = db.relationship('Comment', backref='post', lazy=True)
    likes = db.relationship('PostLike', backref='post', lazy=True)

class PostLike(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    read = db.Column(db.Boolean, default=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def init_database():
    """Database va demo ma'lumotlarni yaratish"""
    with app.app_context():
        # Database yaratish
        db.create_all()
        
        # Demo ma'lumotlarni tekshirish
        if not User.query.first():
            create_demo_data()
            print("✅ Demo ma'lumotlar yaratildi!")
        else:
            print("✅ Database allaqachon mavjud!")

def create_demo_data():
    """Demo ma'lumotlarni yaratish"""
    # Demo topshiriqlar
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
        Task(title="Suv tejash", 
             description="1 kun davomida dush vaqtingizni 5 daqiqaga kamaytiring",
             reward_coins=25, energy_cost=12, difficulty="easy"),
        Task(title="Qayta ishlash", 
             description="10 ta qog'oz va 5 ta shisha idishni ajrating",
             reward_coins=30, energy_cost=18, difficulty="medium")
    ]
    
    # Demo do'kon itemlari
    demo_items = [
        Item(name="Yashil Kepka", price=30, item_type="clothes", image_path="/static/images/hat.png"),
        Item(name="Eco Sumka", price=50, item_type="accessory", image_path="/static/images/bag.png"),
        Item(name="O'simlik Fon", price=100, item_type="background", image_path="/static/images/bg.png"),
        Item(name="Energiya Ichimligi", price=25, item_type="energy", energy_boost=20, image_path="/static/images/energy.png"),
        Item(name="Kuchli Energiya", price=50, item_type="energy", energy_boost=40, image_path="/static/images/energy2.png"),
        Item(name="Eko-Futbolka", price=45, item_type="clothes", image_path="/static/images/shirt.png"),
        Item(name="Eko-Shim", price=60, item_type="clothes", image_path="/static/images/pants.png"),
        Item(name="Quyosh Noyob", price=150, item_type="accessory", image_path="/static/images/sunglasses.png"),
        Item(name="Eko-Ayak", price=80, item_type="shoes", image_path="/static/images/shoes.png")
    ]
    
    # Demo foydalanuvchilar
    demo_users = [
        User(username='admin', email='admin@ecoverse.com', 
             password_hash=generate_password_hash('admin123'), role='admin', coins=1000),
        User(username='bola_test', email='bola@ecoverse.com', 
             password_hash=generate_password_hash('bola123'), role='child', coins=50),
        User(username='katta_test', email='katta@ecoverse.com', 
             password_hash=generate_password_hash('katta123'), role='adult', coins=75),
        User(username='eco_hero', email='hero@ecoverse.com', 
             password_hash=generate_password_hash('hero123'), role='child', coins=120, streak=7),
        User(username='green_warrior', email='warrior@ecoverse.com', 
             password_hash=generate_password_hash('warrior123'), role='adult', coins=200, streak=14)
    ]
    
    # Databasega qo'shish
    for task in demo_tasks:
        db.session.add(task)
    for item in demo_items:
        db.session.add(item)
    for user in demo_users:
        db.session.add(user)
    
    db.session.commit()
    
    print("🎉 Demo ma'lumotlar yaratildi!")
    print("👨‍💼 Admin: admin / admin123")
    print("👦 Bola: bola_test / bola123") 
    print("👨 Katta: katta_test / katta123")

# Asosiy Route'lar
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
            # Streak yangilash
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
            
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
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
        
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Hisob muvaffaqiyatli yaratildi! Iltimos, tizimga kiring.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Xatolik yuz berdi: {str(e)}', 'error')
    
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'child':
        tasks = Task.query.all()
        items = Item.query.limit(6).all()
        return render_template('dashboard_child.html', 
                             user=current_user,
                             tasks=tasks,
                             items=items)
    else:
        posts = Post.query.filter_by(status='active').order_by(Post.date.desc()).limit(5).all()
        return render_template('dashboard_adult.html',
                             user=current_user,
                             posts=posts)

# User Route'lar
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
    
    # Kategoriyalar bo'yicha itemlar
    clothes_items = [inv for inv in inventory if inv.item.item_type == 'clothes']
    accessory_items = [inv for inv in inventory if inv.item.item_type == 'accessory']
    background_items = [inv for inv in inventory if inv.item.item_type == 'background']
    hat_items = [inv for inv in inventory if inv.item.item_type == 'hat']
    shoe_items = [inv for inv in inventory if inv.item.item_type == 'shoes']
    
    return render_template('hero.html', 
                         inventory=inventory,
                         equipped_items=equipped_items,
                         clothes_items=clothes_items,
                         accessory_items=accessory_items,
                         background_items=background_items,
                         hat_items=hat_items,
                         shoe_items=shoe_items,
                         user=current_user)

@app.route('/posts')
@login_required
def posts():
    all_posts = Post.query.filter_by(status='active').order_by(Post.date.desc()).all()
    return render_template('posts.html', posts=all_posts, user=current_user)

@app.route('/post/<int:post_id>')
@login_required
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)
    similar_posts = Post.query.filter(Post.id != post_id, Post.category == post.category, Post.status == 'active').limit(3).all()
    
    user_liked = PostLike.query.filter_by(user_id=current_user.id, post_id=post_id).first() is not None
    
    return render_template('post_detail.html', 
                         post=post, 
                         similar_posts=similar_posts,
                         user_liked=user_liked,
                         user=current_user)

@app.route('/messages')
@login_required
def messages():
    all_users = User.query.filter(User.id != current_user.id).all()
    
    conversations = []
    for user in all_users:
        last_message = Message.query.filter(
            ((Message.sender_id == current_user.id) & (Message.receiver_id == user.id)) |
            ((Message.sender_id == user.id) & (Message.receiver_id == current_user.id))
        ).order_by(Message.timestamp.desc()).first()
        
        if last_message:
            unread_count = Message.query.filter_by(sender_id=user.id, receiver_id=current_user.id, read=False).count()
            conversations.append({
                'user': user,
                'last_message': last_message.text[:50] + '...' if len(last_message.text) > 50 else last_message.text,
                'last_message_time': last_message.timestamp.strftime('%H:%M'),
                'unread': unread_count > 0
            })
    
    return render_template('messages.html', 
                         conversations=conversations, 
                         all_users=all_users,
                         user=current_user)

# Tezkor Havolalar Route'lari
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

# Admin Route'lar
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated and current_user.role == 'admin':
        return redirect(url_for('admin_dashboard'))
        
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username, role='admin').first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user, remember=True)
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Admin login yoki parol noto\'g\'ri!', 'error')
    
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('Admin huquqi kerak!', 'error')
        return redirect(url_for('dashboard'))
    
    total_users = User.query.count()
    total_child_users = User.query.filter_by(role='child').count()
    total_adult_users = User.query.filter_by(role='adult').count()
    total_posts = Post.query.count()
    total_tasks = Task.query.count()
    total_items = Item.query.count()
    
    recent_posts = Post.query.order_by(Post.date.desc()).limit(5).all()
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    
    return render_template('admin_dashboard.html',
                         total_users=total_users,
                         total_child_users=total_child_users,
                         total_adult_users=total_adult_users,
                         total_posts=total_posts,
                         total_tasks=total_tasks,
                         total_items=total_items,
                         recent_posts=recent_posts,
                         recent_users=recent_users,
                         current_user=current_user)

@app.route('/admin/child')
@login_required
def admin_child():
    if current_user.role != 'admin':
        flash('Admin huquqi kerak!', 'error')
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
    if current_user.role != 'admin':
        flash('Admin huquqi kerak!', 'error')
        return redirect(url_for('dashboard'))
    
    adult_users = User.query.filter_by(role='adult').all()
    posts = Post.query.order_by(Post.date.desc()).all()
    
    return render_template('admin_adult.html',
                         adult_users=adult_users,
                         posts=posts,
                         current_user=current_user)

@app.route('/admin/users')
@login_required
def admin_users():
    if current_user.role != 'admin':
        flash('Admin huquqi kerak!', 'error')
        return redirect(url_for('dashboard'))
    
    users = User.query.all()
    return render_template('admin_users.html', users=users, current_user=current_user)

@app.route('/admin/shop')
@login_required
def admin_shop():
    if current_user.role != 'admin':
        flash('Admin huquqi kerak!', 'error')
        return redirect(url_for('dashboard'))
    
    items = Item.query.all()
    return render_template('admin_shop.html', items=items, current_user=current_user)

# API Route'lar
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
        
        # Agar item energiya bersa, energiyani oshirish
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
    
    # Energiya sotib olish
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
    
    # Avval barcha itemlarni echish (faqat bir xil turdagi)
    same_type_items = Inventory.query.filter_by(
        user_id=current_user.id, 
        equipped=True
    ).join(Item).filter(Item.item_type == inventory_item.item.item_type).all()
    
    for item in same_type_items:
        item.equipped = False
    
    # Yangi itemni kiyish
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

@app.route('/like_post/<int:post_id>', methods=['POST'])
@login_required
def like_post(post_id):
    post = Post.query.get_or_404(post_id)
    
    existing_like = PostLike.query.filter_by(user_id=current_user.id, post_id=post_id).first()
    
    if existing_like:
        db.session.delete(existing_like)
        post.likes_count = max(0, post.likes_count - 1)
        liked = False
    else:
        new_like = PostLike(user_id=current_user.id, post_id=post_id)
        db.session.add(new_like)
        post.likes_count += 1
        liked = True
    
    db.session.commit()
    
    return jsonify({
        'success': True, 
        'liked': liked,
        'likes_count': post.likes_count,
        'message': 'Post like qilindi!' if liked else 'Post like olib tashlandi!'
    })

# Admin API Route'lar
@app.route('/admin/update_user_coins/<int:user_id>', methods=['POST'])
@login_required
def admin_update_user_coins(user_id):
    if current_user.role != 'admin':
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
    if current_user.role != 'admin':
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
    if current_user.role != 'admin':
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
    if current_user.role != 'admin':
        return jsonify({'success': False, 'error': 'Admin huquqi kerak!'})
    
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Topshiriq o\'chirildi!'})

# Logout Route'lar
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Siz tizimdan chiqdingiz!', 'info')
    return redirect(url_for('login'))

@app.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for('admin_login'))

if __name__ == '__main__':
    # Database va demo ma'lumotlarni yaratish
    init_database()
    
    print("\n🎉 EcoVerse tizimi ishga tushdi!")
    print("📍 Asosiy sahifa: http://localhost:5000")
    print("👨‍💼 Admin panel: http://localhost:5000/admin/login")
    print("\n📋 Demo loginlar:")
    print("   👨‍💼 Admin: admin / admin123")
    print("   👦 Bola: bola_test / bola123") 
    print("   👨 Katta: katta_test / katta123")
    print("   🦸 Eco Hero: eco_hero / hero123")
    print("   🛡️ Green Warrior: green_warrior / warrior123")
    
    app.run(debug=True, host='0.0.0.0', port=5000)