Haber Akışı - Dynamic News & Blogging Platform

A modern web application built with Flask that allows users to browse, search, and filter news articles (blogs). Admins can manage content through a secure dashboard, while users can interact with posts via likes and contact forms.

🚀 Features

User Features

    Browse news articles sorted by popularity (likes) and date.

    Search and filter articles by category.

    View trending articles.

    Interact via likes (IP-based tracking to prevent duplicate likes).

    Contact admin via a contact form (emails sent via SMTP).

    Responsive and user-friendly interface.

Admin Features

    Secure login to the admin dashboard.

    Create, edit, and delete articles.

    Upload images for articles.

    Manage article categories dynamically.

    View all articles with likes and author info.

    Technical Features

    Flask web framework

    SQLite database with automatic migrations

    Image uploads with file validation

    Secure password hashing using SHA256

    Session-based authentication

    Email notifications for contact form using SMTP

    Pagination and trending article calculations

📁 Project Structure
    
    blog/
    ├── app.py               # Main Flask application
    ├── static/              # CSS, JS, images, and uploads
    │   └── uploads/         # Uploaded images
    ├── templates/           # HTML templates
    ├── blog.db              # SQLite database (auto-generated)
    ├── .env                 # Environment variables for email credentials

⚡ Installation

Clone the repository:

    git clone https://github.com/asilgumus/Haber-Akisi.git
    cd Haber-Akisi/blog

Install dependencies:

    pip install -r requirements.txt


Create a .env file in the project root:

    SMTP_SERVER=smtp.gmail.com
    SMTP_PORT=587
    SMTP_USERNAME=your_email@gmail.com
    SMTP_PASSWORD=your_email_password
    ADMIN_EMAIL=admin@haberakisi.com


Run the application:

    python app.py
Open in browser:

    http://127.0.0.1:5000/

🔧 Usage

    Home page shows trending articles sorted by likes.

    Click on any article to see details.

    Search articles using the search bar.

    Filter articles by category using the category menu.

    Admin dashboard:

    http://127.0.0.1:5000/admin


    Default admin credentials are set during database initialization.

    Create, edit, delete articles and upload images.

💾 Database

    SQLite database (blog.db) initialized automatically.

    Tables:

    users – Stores user accounts and admin info

    blogs – Stores articles with title, content, category, likes, and author

    blog_likes – Tracks likes per user IP

📬 Contact Form

    Sends emails to the admin email specified in .env.

    Requires SMTP credentials for proper functionality.

🛡 Security

    Passwords hashed using SHA256

    Session-based authentication for admin panel

    File upload validation to allow only images (png, jpg, jpeg, webp, gif)

📄 License

MIT License © [Asil Doğan Gümüş]