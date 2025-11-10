from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import sqlite3
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'eco-verse-secret-key-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///eco.db'
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
    
    posts = db.relationship('Post', backref='author', lazy=True)
    comments = db.relationship('Comment', backref='author', lazy=True)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    reward_coins = db.Column(db.Integer, default=10)
    reward_energy = db.Column(db.Integer, default=5)
    difficulty = db.Column(db.String(20), default='easy')

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    item_type = db.Column(db.String(30), nullable=False)
    image_path = db.Column(db.String(200))

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
    
    comments = db.relationship('Comment', backref='post', lazy=True)

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
            if user.last_login and user.last_login.date() != today:
                if (today - user.last_login.date()).days == 1:
                    user.streak += 1
                else:
                    user.streak = 1
            elif not user.last_login:
                user.streak = 1
            
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            login_user(user)
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('dashboard'))
        else:
            flash('Login yoki parol noto‘g‘ri!')
    
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
            flash('Bu foydalanuvchi nomi band!')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Bu email band!')
            return render_template('register.html')
        
        hashed_password = generate_password_hash(password)
        
        new_user = User(
            username=username,
            email=email,
            password_hash=hashed_password,
            role=role,
            coins=0
        )
        
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Hisob muvaffaqiyatli yaratildi! Iltimos, tizimga kiring.')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Xatolik yuz berdi: {str(e)}')
    
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'child':
        tasks = Task.query.all()
        items = Item.query.all()
        return render_template('dashboard_child.html', 
                             user=current_user,
                             tasks=tasks,
                             items=items)
    else:
        posts = Post.query.order_by(Post.date.desc()).limit(5).all()
        return render_template('dashboard_adult.html',
                             user=current_user,
                             posts=posts)

# User Route'lar
@app.route('/shop')
@login_required
def shop():
    items = Item.query.all()
    return render_template('shop.html', items=items)

@app.route('/hero')
@login_required
def hero():
    inventory = Inventory.query.filter_by(user_id=current_user.id).all()
    return render_template('hero.html', inventory=inventory)

@app.route('/posts')
@login_required
def posts():
    all_posts = Post.query.order_by(Post.date.desc()).all()
    return render_template('posts.html', posts=all_posts)

@app.route('/post/<int:post_id>')
@login_required
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)
    similar_posts = Post.query.filter(Post.id != post_id, Post.category == post.category).limit(3).all()
    return render_template('post_detail.html', post=post, similar_posts=similar_posts)

@app.route('/messages')
@login_required
def messages():
    # Foydalanuvchining xabarlashuvlari
    sent_messages = Message.query.filter_by(sender_id=current_user.id).all()
    received_messages = Message.query.filter_by(receiver_id=current_user.id).all()
    
    # Barcha foydalanuvchilar (yangi xabar yuborish uchun)
    all_users = User.query.filter(User.id != current_user.id).all()
    
    # Xabarlashuvlar ro'yxati
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
                         all_users=all_users)

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
            login_user(user)
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Admin login yoki parol noto‘g‘ri!')
    
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('Admin huquqi kerak!')
        return redirect(url_for('dashboard'))
    
    # Admin statistikasi
    total_users = User.query.count()
    total_child_users = User.query.filter_by(role='child').count()
    total_adult_users = User.query.filter_by(role='adult').count()
    total_posts = Post.query.count()
    total_tasks = Task.query.count()
    total_items = Item.query.count()
    
    # So'nggi faollik
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
                         recent_users=recent_users)

@app.route('/admin/child')
@login_required
def admin_child():
    if current_user.role != 'admin':
        flash('Admin huquqi kerak!')
        return redirect(url_for('dashboard'))
    
    child_users = User.query.filter_by(role='child').all()
    tasks = Task.query.all()
    items = Item.query.all()
    
    return render_template('admin_child.html',
                         child_users=child_users,
                         tasks=tasks,
                         items=items)

@app.route('/admin/adult')
@login_required
def admin_adult():
    if current_user.role != 'admin':
        flash('Admin huquqi kerak!')
        return redirect(url_for('dashboard'))
    
    adult_users = User.query.filter_by(role='adult').all()
    posts = Post.query.order_by(Post.date.desc()).all()
    
    return render_template('admin_adult.html',
                         adult_users=adult_users,
                         posts=posts)

@app.route('/admin/users')
@login_required
def admin_users():
    if current_user.role != 'admin':
        flash('Admin huquqi kerak!')
        return redirect(url_for('dashboard'))
    
    users = User.query.all()
    return render_template('admin_users.html', users=users)

# API Route'lar
@app.route('/complete_task/<int:task_id>', methods=['POST'])
@login_required
def complete_task(task_id):
    if current_user.role != 'child':
        return jsonify({'success': False, 'error': 'Faqat bolalar uchun'})
    
    task = Task.query.get_or_404(task_id)
    
    if current_user.energy >= 10:
        current_user.coins += task.reward_coins
        current_user.energy = max(0, current_user.energy - 10)
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'coins': current_user.coins,
            'energy': current_user.energy,
            'message': f'Topshiriq bajarildi! +{task.reward_coins} coin'
        })
    
    return jsonify({'success': False, 'error': 'Energiya yetarli emas!'})

@app.route('/buy_item/<int:item_id>', methods=['POST'])
@login_required
def buy_item(item_id):
    item = Item.query.get_or_404(item_id)
    
    if current_user.coins >= item.price:
        current_user.coins -= item.price
        
        # Inventoryga qo'shish
        new_inventory = Inventory(user_id=current_user.id, item_id=item.id)
        db.session.add(new_inventory)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'coins': current_user.coins,
            'message': f'{item.name} sotib olindi!'
        })
    
    return jsonify({'success': False, 'error': 'Coin yetarli emas!'})

@app.route('/equip_item/<int:item_id>', methods=['POST'])
@login_required
def equip_item(item_id):
    inventory_item = Inventory.query.filter_by(id=item_id, user_id=current_user.id).first()
    
    if not inventory_item:
        return jsonify({'success': False, 'error': 'Item topilmadi!'})
    
    # Barcha itemlarni faolligini olib tashlash
    Inventory.query.filter_by(user_id=current_user.id).update({'equipped': False})
    
    # Tanlangan itemni faollashtirish
    inventory_item.equipped = True
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'{inventory_item.item.name} muvaffaqiyatli kiyildi!'
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
        category=category
    )
    
    db.session.add(new_post)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Post muvaffaqiyatli yaratildi!'})

@app.route('/add_comment/<int:post_id>', methods=['POST'])
@login_required
def add_comment(post_id):
    data = request.get_json()
    text = data.get('text')
    
    if not text:
        return jsonify({'success': False, 'error': 'Izoh bo\'sh bo\'lmasligi kerak!'})
    
    new_comment = Comment(
        post_id=post_id,
        user_id=current_user.id,
        text=text
    )
    
    db.session.add(new_comment)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Izoh muvaffaqiyatli qo\'shildi!'})

@app.route('/send_message', methods=['POST'])
@login_required
def send_message():
    data = request.get_json()
    receiver_id = data.get('receiver_id')
    text = data.get('text')
    
    if not text or not receiver_id:
        return jsonify({'success': False, 'error': 'Xabar va qabul qiluvchi kerak!'})
    
    new_message = Message(
        sender_id=current_user.id,
        receiver_id=receiver_id,
        text=text
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
    
    # Xabarlarni o'qilgan deb belgilash
    Message.query.filter_by(sender_id=user_id, receiver_id=current_user.id, read=False).update({'read': True})
    db.session.commit()
    
    messages_data = []
    for msg in messages:
        messages_data.append({
            'id': msg.id,
            'sender_id': msg.sender_id,
            'text': msg.text,
            'timestamp': msg.timestamp.strftime('%H:%M'),
            'is_sent': msg.sender_id == current_user.id
        })
    
    return jsonify({'success': True, 'messages': messages_data})

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
        difficulty=data.get('difficulty', 'easy')
    )
    
    db.session.add(new_task)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Topshiriq qo‘shildi!'})

@app.route('/admin/delete_task/<int:task_id>', methods=['POST'])
@login_required
def admin_delete_task(task_id):
    if current_user.role != 'admin':
        return jsonify({'success': False, 'error': 'Admin huquqi kerak!'})
    
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Topshiriq o‘chirildi!'})

@app.route('/admin/delete_post/<int:post_id>', methods=['POST'])
@login_required
def admin_delete_post(post_id):
    if current_user.role != 'admin':
        return jsonify({'success': False, 'error': 'Admin huquqi kerak!'})
    
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Post o‘chirildi!'})

@app.route('/admin/add_item', methods=['POST'])
@login_required
def admin_add_item():
    if current_user.role != 'admin':
        return jsonify({'success': False, 'error': 'Admin huquqi kerak!'})
    
    data = request.get_json()
    new_item = Item(
        name=data.get('name'),
        price=data.get('price'),
        item_type=data.get('item_type'),
        image_path=data.get('image_path', '')
    )
    
    db.session.add(new_item)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Item qo‘shildi!'})

# Logout Route'lar
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for('admin_login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Demo ma'lumotlar
        if not Task.query.first():
            demo_tasks = [
                Task(title="Plastik idishlarni qayta ishlash", 
                     description="5 ta plastik idishni qayta ishlash markaziga olib boring",
                     reward_coins=15, difficulty="easy"),
                Task(title="Energiya tejash", 
                     description="1 kun davomida keraksiz chiroqlarni o'chiring",
                     reward_coins=20, difficulty="medium"),
                Task(title="Daraxt ekish", 
                     description="Yashil maydonga 1 ta daraxt eking",
                     reward_coins=50, difficulty="hard"),
                Task(title="Suv tejash", 
                     description="Dush vaqtingizni 5 daqiqaga qisqartiring",
                     reward_coins=10, difficulty="easy"),
                Task(title="Qayta ishlatish", 
                     description="Eski gazetalardan qog'oz sumka yasang",
                     reward_coins=25, difficulty="medium")
            ]
            
            demo_items = [
                Item(name="Yashil Kepka", price=30, item_type="clothes", image_path="/static/images/items/green_hat.png"),
                Item(name="Eco Sumka", price=50, item_type="accessory", image_path="/static/images/items/eco_bag.png"),
                Item(name="O'simlik Fon", price=100, item_type="background", image_path="/static/images/items/plant_bg.png"),
                Item(name="Daraxt Nishoni", price=75, item_type="accessory", image_path="/static/images/items/tree_badge.png"),
                Item(name="Quyosh Batareyasi", price=150, item_type="accessory", image_path="/static/images/items/solar_battery.png"),
                Item(name="Eko-Futbolka", price=45, item_type="clothes", image_path="/static/images/items/eco_tshirt.png")
            ]
            
            for task in demo_tasks:
                db.session.add(task)
            for item in demo_items:
                db.session.add(item)
            
            # Demo admin foydalanuvchi yaratish
            if not User.query.filter_by(username='admin').first():
                admin_user = User(
                    username='admin',
                    email='admin@ecoverse.com',
                    password_hash=generate_password_hash('admin123'),
                    role='admin',
                    coins=1000
                )
                db.session.add(admin_user)
                print("✅ Demo admin yaratildi:")
                print("   👤 Username: admin")
                print("   🔑 Password: admin123")
                print("   🌐 Admin panel: http://localhost:5000/admin/login")
            
            # Demo oddiy foydalanuvchilar
            if not User.query.filter_by(role='child').first():
                child_user = User(
                    username='bola_test',
                    email='bola@ecoverse.com',
                    password_hash=generate_password_hash('bola123'),
                    role='child',
                    coins=50
                )
                db.session.add(child_user)
                print("✅ Demo bola foydalanuvchi:")
                print("   👤 Username: bola_test")
                print("   🔑 Password: bola123")
            
            if not User.query.filter_by(role='adult').first():
                adult_user = User(
                    username='katta_test',
                    email='katta@ecoverse.com',
                    password_hash=generate_password_hash('katta123'),
                    role='adult',
                    coins=100
                )
                db.session.add(adult_user)
                print("✅ Demo katta foydalanuvchi:")
                print("   👤 Username: katta_test") 
                print("   🔑 Password: katta123")
            
            # Demo postlar
            if not Post.query.first():
                adult_user = User.query.filter_by(role='adult').first()
                if adult_user:
                    demo_posts = [
                        Post(
                            user_id=adult_user.id,
                            title="Plastikni qayta ishlash bo'yicha maslahat",
                            content="Har kuni 3 ta plastik idishni qayta ishlash markaziga olib boring. Bu atrof-muhitni muhofaza qilishga katta yordam beradi!",
                            category="Eko-lifehack"
                        ),
                        Post(
                            user_id=adult_user.id,
                            title="Daraxt ekish aksiyasi",
                            content="Yakshanba kuni shahar bog'ida daraxt ekamiz. Barchani taklif qilamiz! Kelajagimiz uchun yashil dunyo yaratamiz.",
                            category="Volunteer event"
                        )
                    ]
                    for post in demo_posts:
                        db.session.add(post)
            
            db.session.commit()
            print("\n🎉 Barcha demo ma'lumotlar yaratildi!")
            print("📍 Asosiy sahifa: http://localhost:5000")
            print("👨‍💼 Admin panel: http://localhost:5000/admin/login")
    
    app.run(debug=True)