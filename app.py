from flask import Flask, jsonify, request, render_template, redirect, url_for, flash, session
import sqlite3
import os
from datetime import datetime
import hashlib
import secrets
from werkzeug.utils import secure_filename
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Session için güvenli key

DATABASE = "blog.db"
UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "gif"}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def init_db():
    """Database'i başlat ve tabloları oluştur"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Users tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            is_admin BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Blogs tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS blogs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            summary TEXT NOT NULL,
            content TEXT NOT NULL,
            category TEXT DEFAULT 'genel',
            image_path TEXT,
            likes INTEGER DEFAULT 0,
            author_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (author_id) REFERENCES users (id)
        )
    ''')

    # Migration: category kolonu yoksa ekle
    cursor.execute("PRAGMA table_info(blogs)")
    existing_columns = [row[1] for row in cursor.fetchall()]
    if 'category' not in existing_columns:
        cursor.execute("ALTER TABLE blogs ADD COLUMN category TEXT DEFAULT 'genel'")
    if 'image_path' not in existing_columns:
        cursor.execute("ALTER TABLE blogs ADD COLUMN image_path TEXT")
    if 'likes' not in existing_columns:
        cursor.execute("ALTER TABLE blogs ADD COLUMN likes INTEGER DEFAULT 0")
    
    # Blog likes tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS blog_likes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            blog_id INTEGER,
            user_ip TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (blog_id) REFERENCES blogs (id),
            UNIQUE(blog_id, user_ip)
        )
    ''')
    
    # Migration: user_ip kolonu yoksa ekle
    cursor.execute("PRAGMA table_info(blog_likes)")
    existing_columns = [row[1] for row in cursor.fetchall()]
    if 'user_ip' not in existing_columns:
        cursor.execute("ALTER TABLE blog_likes ADD COLUMN user_ip TEXT")
        # Eski user_id verilerini temizle
        cursor.execute("DELETE FROM blog_likes")
    
    # Admin kullanıcısı oluştur (eğer yoksa)
    cursor.execute('SELECT COUNT(*) FROM users WHERE is_admin = 1')
    if cursor.fetchone()[0] == 0:
        admin_password = hashlib.sha256('admin123'.encode()).hexdigest()
        cursor.execute('''
            INSERT INTO users (name, email, password, is_admin)
            VALUES (?, ?, ?, ?)
        ''', ('Admin', 'admin@blog.com', admin_password, 1))

    # Örnek blog yazıları ekle (eğer yoksa)
    cursor.execute('SELECT COUNT(*) FROM blogs')
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO blogs (title, summary, content, category, author_id, likes)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', ('İlk Blog Yazısı', 'Bilgi ve güncel içerikler burada.',
              'Bu blog yazısında modern web geliştirme teknikleri hakkında detaylı bilgiler bulacaksınız. Frontend ve backend teknolojilerinin nasıl birlikte çalıştığını öğreneceksiniz.\n\nModern web geliştirme, kullanıcı deneyimini ön planda tutarak responsive ve hızlı uygulamalar oluşturmayı hedefler. Bu süreçte HTML, CSS ve JavaScript gibi temel teknolojilerin yanı sıra, React, Vue.js gibi modern framework\'ler de önemli rol oynar.', 'genel', 1, 8))

        cursor.execute('''
            INSERT INTO blogs (title, summary, content, category, author_id, likes)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', ('Frontend Geliştirme İpuçları', 'Modern web tasarım örnekleri.',
              'Responsive tasarım, modern CSS teknikleri ve JavaScript best practices hakkında kapsamlı bir rehber. UI/UX tasarım prensipleri ve kullanıcı deneyimi optimizasyonu.\n\nFrontend geliştirmede dikkat edilmesi gereken en önemli noktalar:\n- Responsive tasarım prensipleri\n- Performance optimizasyonu\n- Accessibility standartları\n- Modern CSS teknikleri\n- JavaScript best practices', 'frontend', 1, 12))

        cursor.execute('''
            INSERT INTO blogs (title, summary, content, category, author_id, likes)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', ('Tailwind CSS ile Modern UI', 'Responsive ve minimal tasarım.',
              'Tailwind CSS kullanarak hızlı ve etkili arayüzler oluşturma teknikleri. Utility-first CSS yaklaşımı ve component-based tasarım prensipleri.\n\nTailwind CSS\'in avantajları:\n- Hızlı prototipleme\n- Tutarlı tasarım sistemi\n- Küçük bundle boyutu\n- Özelleştirilebilir yapı\n- Modern web standartlarına uygunluk', 'ui', 1, 5))
    else:
        # Eğer bloglar varsa, likes'ları güncelle
        cursor.execute('UPDATE blogs SET likes = 8 WHERE title = ?', ('İlk Blog Yazısı',))
        cursor.execute('UPDATE blogs SET likes = 12 WHERE title = ?', ('Frontend Geliştirme İpuçları',))
        cursor.execute('UPDATE blogs SET likes = 5 WHERE title = ?', ('Tailwind CSS ile Modern UI',))
    
    conn.commit()
    conn.close()

def get_db_connection():
    """Database bağlantısı al"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def get_user_by_email(email):
    """Email ile kullanıcı bul"""
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    conn.close()
    return user

def get_all_blogs():
    """Tüm blogları getir ve sözlük listesi olarak döndür"""
    conn = get_db_connection()
    blogs_from_db = conn.execute('''
        SELECT b.*, u.name as author_name 
        FROM blogs b 
        LEFT JOIN users u ON b.author_id = u.id 
        ORDER BY b.created_at DESC
    ''').fetchall()
    conn.close()
    
    # DEĞİŞİKLİK BURADA:
    # Veritabanından gelen 'Row' nesneleri listesini,
    # JSON'a dönüştürülebilir standart bir Python sözlük (dictionary) listesine çeviriyoruz.
    return [dict(row) for row in blogs_from_db]

def get_blog_by_id(blog_id):
    """ID ile blog getir"""
    conn = get_db_connection()
    blog = conn.execute('''
        SELECT b.*, u.name as author_name 
        FROM blogs b 
        LEFT JOIN users u ON b.author_id = u.id 
        WHERE b.id = ?
    ''', (blog_id,)).fetchone()
    conn.close()
    return blog

def create_blog(title, summary, content, category, author_id, image_path=None):
    """Yeni blog oluştur"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO blogs (title, summary, content, category, image_path, author_id) 
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (title, summary, content, category, image_path, author_id))
    blog_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return blog_id

def update_blog(blog_id, title, summary, content, category, image_path=None):
    """Blog güncelle"""
    conn = get_db_connection()
    conn.execute('''
        UPDATE blogs 
        SET title = ?, summary = ?, content = ?, category = ?, image_path = COALESCE(?, image_path), updated_at = CURRENT_TIMESTAMP 
        WHERE id = ?
    ''', (title, summary, content, category, image_path, blog_id))
    conn.commit()
    conn.close()

def delete_blog(blog_id):
    """Blog sil"""
    conn = get_db_connection()
    conn.execute('DELETE FROM blogs WHERE id = ?', (blog_id,))
    conn.commit()
    conn.close()

    
@app.route("/")
def home():
    return redirect(url_for('blog'))

@app.route("/blog")
def blog():
    page = request.args.get('page', 1, type=int)
    per_page = 3  # Show 3 blogs per page
    
    conn = get_db_connection()
    
    # Get total count for pagination
    total_blogs = conn.execute('SELECT COUNT(*) FROM blogs').fetchone()[0]
    
    # Calculate offset
    offset = (page - 1) * per_page
    
    # Get blogs for current page - ordered by likes DESC, then by created_at DESC
    blogs = conn.execute('''
        SELECT b.*, u.name as author_name FROM blogs b
        LEFT JOIN users u ON b.author_id = u.id
        ORDER BY b.likes DESC, b.created_at DESC
        LIMIT ? OFFSET ?
    ''', (per_page, offset)).fetchall()
    
    # Get categories with counts
    categories = conn.execute('''
        SELECT category, COUNT(*) as count 
        FROM blogs 
        WHERE category IS NOT NULL AND category != ''
        GROUP BY category 
        ORDER BY count DESC
    ''').fetchall()
    
    # Get trending blogs (top 5 most liked across ALL pages)
    trending_blogs = conn.execute('''
        SELECT b.*, u.name as author_name FROM blogs b
        LEFT JOIN users u ON b.author_id = u.id
        ORDER BY b.likes DESC, b.created_at DESC
        LIMIT 5
    ''').fetchall()
    
    # Calculate pagination info
    total_pages = (total_blogs + per_page - 1) // per_page
    has_prev = page > 1
    has_next = page < total_pages
    
    conn.close()
    
    return render_template("blog2.html", 
                         blogs=blogs, 
                         page=page, 
                         total_pages=total_pages,
                         has_prev=has_prev, 
                         has_next=has_next,
                         prev_num=page-1 if has_prev else None,
                         next_num=page+1 if has_next else None,
                         categories=categories,
                         trending_blogs=trending_blogs)

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        # Email gönder
        try:
            send_contact_email(name, email, subject, message)
            flash('Mesajınız başarıyla gönderildi!', 'success')
        except Exception as e:
            flash('Mesaj gönderilirken hata oluştu. Lütfen tekrar deneyin.', 'error')
        
        return redirect(url_for('contact'))
    
    return render_template("contact.html")

def send_contact_email(name, email, subject, message):
    # .env dosyasından email ayarlarını al
    smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    smtp_username = os.getenv('SMTP_USERNAME')
    smtp_password = os.getenv('SMTP_PASSWORD')
    admin_email = os.getenv('ADMIN_EMAIL', 'admin@haberakisi.com')
    
    if not smtp_username or not smtp_password:
        raise Exception("Email ayarları eksik")
    
    # Email oluştur
    msg = MIMEMultipart()
    msg['From'] = smtp_username
    msg['To'] = admin_email
    msg['Subject'] = f"İletişim Formu: {subject}"
    
    body = f"""
    Yeni iletişim formu mesajı:
    
    Ad Soyad: {name}
    E-posta: {email}
    Konu: {subject}
    
    Mesaj:
    {message}
    """
    
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    
    # Email gönder
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(smtp_username, smtp_password)
    text = msg.as_string()
    server.sendmail(smtp_username, admin_email, text)
    server.quit()

@app.route("/about")
def about():
    return render_template("about.html")

@app.route('/category/<slug>')
def category_page(slug):
    conn = get_db_connection()
    blogs = conn.execute('''
        SELECT b.*, u.name as author_name FROM blogs b
        LEFT JOIN users u ON b.author_id = u.id
        WHERE lower(replace(b.category, ' ', '-')) = ?
        ORDER BY b.likes DESC, b.created_at DESC
    ''', (slug.lower(),)).fetchall()

    # Get all categories for the selection box
    categories = conn.execute('''
        SELECT category, COUNT(*) as count
        FROM blogs
        WHERE category IS NOT NULL AND category != ''
        GROUP BY category
        ORDER BY count DESC
    ''').fetchall()

    # Get trending blogs (top 5 most liked in this category)
    trending_blogs = conn.execute('''
        SELECT b.*, u.name as author_name FROM blogs b
        LEFT JOIN users u ON b.author_id = u.id
        WHERE lower(b.category) = lower(?)
        ORDER BY b.likes DESC, b.created_at DESC
        LIMIT 5
    ''', (slug,)).fetchall()

    conn.close()
    return render_template('category.html', blogs=blogs, category_slug=slug, categories=categories, trending_blogs=trending_blogs)


@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    name = data["name"]
    email = data["email"]
    password = data["password"]
    
    # Kullanıcı zaten var mı kontrol et
    existing_user = get_user_by_email(email)
    if existing_user:
        return jsonify({"message": "Bu email adresi zaten kayıtlı!"}), 400
    
    # Şifreyi hashle
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    # Yeni kullanıcı oluştur
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO users (name, email, password) 
        VALUES (?, ?, ?)
    ''', (name, email, hashed_password))
    conn.commit()
    conn.close()

    return jsonify({"message": "Kayıt Başarılı"}), 200


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data["email"]
    password = data["password"]

    # Kullanıcıyı bul
    user = get_user_by_email(email)
    if not user:
        return jsonify({"message": "Kayıtlı Kullanıcı Bulunamadı"}), 400
    
    # Şifreyi kontrol et
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    if user['password'] == hashed_password:
        # Session'a kullanıcı bilgilerini kaydet
        session['user_id'] = user['id']
        session['user_name'] = user['name']
        session['user_email'] = user['email']
        session['is_admin'] = user['is_admin']
        
        return jsonify({
            "message": "Giriş Başarılı",
            "is_admin": user['is_admin']
        }), 200
    else:
        return jsonify({"message": "Şifre yanlış"}), 400



@app.route("/blogDetail.html/id=<int:id>", methods=["GET"])
def show_detail(id):
    return render_template("blogDetail.html", id=id)

@app.route("/api/blog-detail", methods=["POST"])
def get_blog_detail():
    data = request.get_json()
    blog_id = data.get("id")

    blog = get_blog_by_id(blog_id)

    if blog:
        return jsonify({
            "success": True,
            "data": {
                "id": blog['id'],
                "title": blog['title'],
                "summary": blog['summary'],
                "content": blog['content'],
                "date": blog['created_at'][:10],  # YYYY-MM-DD formatı
                "author": blog['author_name'],
                "category": blog['category'],
                "likes": blog['likes'],
                "image_path": blog['image_path']
            }
        })
    else:
        return jsonify({
            "success": False,
            "message": "Blog bulunamadı"
        }), 404

@app.route("/api/search-blogs", methods=["GET"])
def search_blogs():
    query = request.args.get('query', '').strip()
    category = request.args.get('category', '').strip()
    if not query:
        return jsonify({"blogs": []})

    conn = get_db_connection()
    sql = '''
        SELECT b.*, u.name as author_name
        FROM blogs b
        LEFT JOIN users u ON b.author_id = u.id
        WHERE (LOWER(b.title) LIKE LOWER(?) OR LOWER(b.summary) LIKE LOWER(?))
    '''
    params = (f'%{query}%', f'%{query}%')
    if category and category != 'all':
        sql += ' AND lower(b.category) = lower(?)'
        params = params + (category,)

    sql += ' ORDER BY b.likes DESC, b.created_at DESC'
    blogs = conn.execute(sql, params).fetchall()
    conn.close()

    blogs_list = [dict(row) for row in blogs]
    return jsonify({"blogs": blogs_list})

# Admin Panel Routes
@app.route("/admin")
def admin_panel():
    return render_template("admin_login.html")

@app.route("/admin/login", methods=["POST"])
def admin_login():
    username = request.form.get('username')
    password1 = request.form.get('password1')
    password2 = request.form.get('password2')
    
    # Admin credentials
    correct_username = "YOUR_USERNAME"
    correct_password1 = "YOUR_PASSWORD1"
    correct_password2 = "YOUR_PASSWORD2"
    
    # Check credentials
    if (username == correct_username and 
        password1 == correct_password1 and 
        password2 == correct_password2):
        
        # Get admin user from database
        conn = get_db_connection()
        admin_user = conn.execute('SELECT * FROM users WHERE is_admin = 1').fetchone()
        conn.close()
        
        if admin_user:
            session['is_admin'] = True
            session['user_id'] = admin_user['id']
            session['user_name'] = admin_user['name']
            session['user_email'] = admin_user['email']
            return redirect(url_for('admin_dashboard'))
    
    flash('Yanlış kullanıcı adı veya şifre!', 'error')
    return redirect(url_for('admin_panel'))

@app.route("/admin/dashboard")
def admin_dashboard():
    if not session.get('is_admin'):
        return redirect(url_for('admin_panel'))
    
    blogs = get_all_blogs()
    return render_template("admin.html", blogs=blogs)

@app.route("/admin/blog/new", methods=["GET", "POST"])
def admin_new_blog():
    if not session.get('is_admin'):
        return redirect(url_for('admin_panel'))
    
    if request.method == "POST":
        title = request.form['title']
        summary = request.form['summary']
        content = request.form['content']
        category = request.form.get('category', 'genel')
        author_id = session['user_id']
        image_path = None
        file = request.files.get('image')
        if file and file.filename:
            filename = secure_filename(file.filename)
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(save_path)
            image_path = '/' + save_path.replace('\\', '/')
        
        blog_id = create_blog(title, summary, content, category, author_id, image_path)
        flash('Blog başarıyla oluşturuldu!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    # Kategori listesi (mevcutlardan öneri)
    conn = get_db_connection()
    categories = [row['category'] for row in conn.execute('SELECT DISTINCT category FROM blogs ORDER BY category').fetchall()]
    conn.close()
    return render_template("admin_new_blog.html", categories=categories)

@app.route("/admin/blog/edit/<int:blog_id>", methods=["GET", "POST"])
def admin_edit_blog(blog_id):
    if not session.get('is_admin'):
        return redirect(url_for('admin_panel'))
    
    blog = get_blog_by_id(blog_id)
    if not blog:
        flash('Blog bulunamadı!', 'error')
        return redirect(url_for('admin_panel'))
    
    if request.method == "POST":
        title = request.form['title']
        summary = request.form['summary']
        content = request.form['content']
        category = request.form.get('category', blog['category'])
        image_path = None
        file = request.files.get('image')
        if file and file.filename:
            filename = secure_filename(file.filename)
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(save_path)
            image_path = '/' + save_path.replace('\\', '/')
        
        update_blog(blog_id, title, summary, content, category, image_path)
        flash('Blog başarıyla güncellendi!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    conn = get_db_connection()
    categories = [row['category'] for row in conn.execute('SELECT DISTINCT category FROM blogs ORDER BY category').fetchall()]
    conn.close()
    return render_template("admin_edit_blog.html", blog=blog, categories=categories)
@app.route("/blog2")
def blog2():
    return render_template("blog2.html")

@app.route("/blog-old")
def blog_old():
    blogs = get_all_blogs()

    # Get categories with counts
    conn = get_db_connection()
    categories = conn.execute('''
        SELECT category, COUNT(*) as count
        FROM blogs
        WHERE category IS NOT NULL AND category != ''
        GROUP BY category
        ORDER BY count DESC
    ''').fetchall()

    conn.close()
    return render_template("blog.html", blogs=blogs, categories=categories)

@app.route("/admin/blog/delete/<int:blog_id>", methods=["POST"])
def admin_delete_blog(blog_id):
    if not session.get('is_admin'):
        return redirect(url_for('admin_panel'))
    
    blog = get_blog_by_id(blog_id)
    if blog:
        delete_blog(blog_id)
        flash('Blog başarıyla silindi!', 'success')
    else:
        flash('Blog bulunamadı!', 'error')
    
    return redirect(url_for('admin_dashboard'))

@app.route("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for('admin_panel'))

# Likes API
@app.route('/api/blogs/<int:blog_id>/like', methods=['POST'])
def like_blog(blog_id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Check if user already liked this blog (using IP as identifier)
    user_ip = request.remote_addr
    if not user_ip:
        return jsonify({"success": False, "message": "Kullanıcı tanımlanamadı"}), 401
    
    # Check if user already liked
    existing_like = conn.execute(
        'SELECT id FROM blog_likes WHERE blog_id = ? AND user_ip = ?', 
        (blog_id, user_ip)
    ).fetchone()
    
    if existing_like:
        # Unlike: remove like and decrease count
        cur.execute('DELETE FROM blog_likes WHERE blog_id = ? AND user_ip = ?', (blog_id, user_ip))
        cur.execute('UPDATE blogs SET likes = likes - 1 WHERE id = ?', (blog_id,))
        liked = False
    else:
        # Like: add like and increase count
        cur.execute('INSERT INTO blog_likes (blog_id, user_ip) VALUES (?, ?)', (blog_id, user_ip))
        cur.execute('UPDATE blogs SET likes = likes + 1 WHERE id = ?', (blog_id,))
        liked = True
    
    conn.commit()
    row = conn.execute('SELECT likes FROM blogs WHERE id = ?', (blog_id,)).fetchone()
    conn.close()
    
    if not row:
        return jsonify({"success": False, "message": "Blog bulunamadı"}), 404
    
    return jsonify({"success": True, "likes": row['likes'], "liked": liked})


    




if __name__ == "__main__":
    init_db()  # Database'i başlat
    app.run(debug=True) 