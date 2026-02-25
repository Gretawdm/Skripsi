from flask import Blueprint, request, jsonify, session, redirect, url_for, render_template, flash
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from functools import wraps

auth_bp = Blueprint('auth', __name__)

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'database': 'arimax_forecasting',
    'user': 'root',
    'password': ''
}

def get_db_connection():
    """Get database connection"""
    return mysql.connector.connect(**DB_CONFIG)

def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Silakan login terlebih dahulu', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Silakan login terlebih dahulu', 'warning')
            return redirect(url_for('auth.login'))
        if session.get('role') != 'admin':
            flash('Akses ditolak. Hanya admin yang dapat mengakses halaman ini.', 'danger')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

# ==================== API ENDPOINTS (untuk Postman) ====================

@auth_bp.route('/api/register', methods=['POST'])
def api_register():
    """
    Register new user via API (untuk Postman)
    
    Request Body (JSON):
    {
        "username": "string",
        "password": "string",
        "full_name": "string",
        "email": "string",
        "role": "admin" atau "user"
    }
    """
    try:
        data = request.get_json()
        
        # Validasi input
        required_fields = ['username', 'password', 'role']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'Field {field} wajib diisi'
                }), 400
        
        username = data['username']
        password = data['password']
        full_name = data.get('full_name', '')
        email = data.get('email', '')
        role = data['role']
        
        # Validasi role
        if role not in ['admin', 'user']:
            return jsonify({
                'success': False,
                'message': 'Role harus admin atau user'
            }), 400
        
        # Validasi password
        if len(password) < 6:
            return jsonify({
                'success': False,
                'message': 'Password minimal 6 karakter'
            }), 400
        
        # Hash password
        hashed_password = generate_password_hash(password)
        
        # Insert ke database
        connection = get_db_connection()
        cursor = connection.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO users (username, password, full_name, email, role)
                VALUES (%s, %s, %s, %s, %s)
            """, (username, hashed_password, full_name, email, role))
            
            connection.commit()
            
            return jsonify({
                'success': True,
                'message': f'User {username} berhasil didaftarkan sebagai {role}',
                'data': {
                    'username': username,
                    'full_name': full_name,
                    'email': email,
                    'role': role
                }
            }), 201
            
        except mysql.connector.IntegrityError:
            return jsonify({
                'success': False,
                'message': f'Username {username} sudah digunakan'
            }), 409
            
        finally:
            cursor.close()
            connection.close()
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@auth_bp.route('/api/users', methods=['GET'])
def api_list_users():
    """
    List all users (untuk debugging)
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT id, username, full_name, email, role, is_active, created_at
            FROM users
            ORDER BY created_at DESC
        """)
        
        users = cursor.fetchall()
        
        # Convert datetime to string
        for user in users:
            if user['created_at']:
                user['created_at'] = user['created_at'].isoformat()
        
        cursor.close()
        connection.close()
        
        return jsonify({
            'success': True,
            'data': users,
            'count': len(users)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

# ==================== WEB ROUTES ====================

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page and handler"""
    if request.method == 'POST':
        identifier = request.form.get('username')  # bisa username atau email
        password = request.form.get('password')
        
        if not identifier or not password:
            flash('Username/email dan password wajib diisi', 'danger')
            return redirect(url_for('auth.login'))
        
        # Check user in database (username OR email)
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s OR email = %s", (identifier, identifier))
        user = cursor.fetchone()
        cursor.close()
        connection.close()
        
        if user and check_password_hash(user['password'], password):
            if not user['is_active']:
                flash('Akun Anda tidak aktif. Hubungi administrator.', 'danger')
                return redirect(url_for('auth.login'))
            # Set session
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            session['full_name'] = user['full_name']
            # Redirect based on role
            if user['role'] == 'admin':
                return redirect('/admin/dashboard')
            else:
                return redirect('/')
        else:
            flash('Username/email atau password salah', 'danger')
            return redirect(url_for('auth.login'))
    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    """Logout handler"""
    session.clear()
    flash('Anda telah logout', 'info')
    return redirect('/')

@auth_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """Change password handler"""
    try:
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        if not all([current_password, new_password, confirm_password]):
            flash('Semua field wajib diisi', 'danger')
            return redirect(request.referrer or url_for('admin.dashboard'))
        
        if new_password != confirm_password:
            flash('Password baru dan konfirmasi password tidak sama', 'danger')
            return redirect(request.referrer or url_for('admin.dashboard'))
        
        if len(new_password) < 6:
            flash('Password minimal 6 karakter', 'danger')
            return redirect(request.referrer or url_for('admin.dashboard'))
        
        # Get user from database
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM users WHERE id = %s", (session['user_id'],))
        user = cursor.fetchone()
        
        if not user:
            flash('User tidak ditemukan', 'danger')
            cursor.close()
            connection.close()
            return redirect(request.referrer or url_for('admin.dashboard'))
        
        # Check current password
        if not check_password_hash(user['password'], current_password):
            flash('Password lama salah', 'danger')
            cursor.close()
            connection.close()
            return redirect(request.referrer or url_for('admin.dashboard'))
        
        # Update password
        hashed_password = generate_password_hash(new_password)
        cursor.execute(
            "UPDATE users SET password = %s WHERE id = %s",
            (hashed_password, session['user_id'])
        )
        
        connection.commit()
        cursor.close()
        connection.close()
        
        flash('Password berhasil diubah', 'success')
        return redirect(request.referrer or url_for('admin.dashboard'))
        
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
        return redirect(request.referrer or url_for('admin.dashboard'))
