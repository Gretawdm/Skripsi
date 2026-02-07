# API Documentation - Authentication & User Management

## Base URL
```
http://localhost:5000
```

## Authentication Endpoints

### 1. Register User (API - untuk Postman)

**Endpoint:** `POST /auth/api/register`

**Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
    "username": "admin1",
    "password": "admin123",
    "full_name": "Admin Utama",
    "email": "admin@example.com",
    "role": "admin"
}
```

**Response (Success - 201):**
```json
{
    "success": true,
    "message": "User admin1 berhasil didaftarkan sebagai admin",
    "data": {
        "username": "admin1",
        "full_name": "Admin Utama",
        "email": "admin@example.com",
        "role": "admin"
    }
}
```

**Response (Error - Username Exists - 409):**
```json
{
    "success": false,
    "message": "Username admin1 sudah digunakan"
}
```

**Response (Error - Validation - 400):**
```json
{
    "success": false,
    "message": "Password minimal 6 karakter"
}
```

---

### 2. List All Users (untuk debugging)

**Endpoint:** `GET /auth/api/users`

**Response:**
```json
{
    "success": true,
    "count": 2,
    "data": [
        {
            "id": 1,
            "username": "admin",
            "full_name": "Administrator",
            "email": "admin@example.com",
            "role": "admin",
            "is_active": true,
            "created_at": "2026-02-03T12:00:00"
        },
        {
            "id": 2,
            "username": "user1",
            "full_name": "User Biasa",
            "email": "user@example.com",
            "role": "user",
            "is_active": true,
            "created_at": "2026-02-03T12:30:00"
        }
    ]
}
```

---

### 3. Login (Web Form)

**Endpoint:** `POST /auth/login`

**Form Data:**
- username
- password

**Redirect:**
- Admin → `/admin/dashboard`
- User → `/`

---

### 4. Logout

**Endpoint:** `GET /auth/logout`

**Redirect:** `/`

---

## Role Permissions

### Admin
- Access: `/admin/dashboard`, `/admin/scraping-data`, `/admin/update-model`, `/admin/riwayat`
- Can: Update data, train model, view all history

### User
- Access: `/`, `/prediksi`, `/metode`, public pages
- Can: View predictions, view methodology

---

## Setup Instructions

### 1. Create Users Table
```bash
python create_users_table.py
```

This will:
- Create `users` table
- Create default admin (username: `admin`, password: `admin123`)

### 2. Register Admin via Postman

**Step 1:** Open Postman

**Step 2:** Create new POST request
```
URL: http://localhost:5000/auth/api/register
Method: POST
Headers: Content-Type = application/json
```

**Step 3:** Add JSON body
```json
{
    "username": "admin_baru",
    "password": "password123",
    "full_name": "Admin Baru",
    "email": "admin_baru@example.com",
    "role": "admin"
}
```

**Step 4:** Send request

### 3. Register Regular User

Same as above, but change `"role": "user"`

---

## Security Notes

1. Passwords are hashed using `werkzeug.security.generate_password_hash`
2. Session-based authentication
3. `@login_required` decorator for protected routes
4. `@admin_required` decorator for admin-only routes
5. Change `app.secret_key` in production

---

## Database Schema

```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    email VARCHAR(100),
    role ENUM('admin', 'user') DEFAULT 'user',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

---

## Example Postman Collection

### Register Admin
```
POST http://localhost:5000/auth/api/register
Body (raw JSON):
{
    "username": "superadmin",
    "password": "secure123",
    "full_name": "Super Admin",
    "email": "super@admin.com",
    "role": "admin"
}
```

### Register User
```
POST http://localhost:5000/auth/api/register
Body (raw JSON):
{
    "username": "johndoe",
    "password": "user123",
    "full_name": "John Doe",
    "email": "john@example.com",
    "role": "user"
}
```

### List Users
```
GET http://localhost:5000/auth/api/users
```
