import pymysql
from flask import Flask, request, jsonify
import uuid, json
from decimal import Decimal
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# --- Database configuration ---
db_config = {
    'host': 'hopper.proxy.rlwy.net',
    'user': 'root',
    'password': 'DjijtRCyVJOKljAAWkUuabRyJWCmjXqf',
    'database': 'railway',
    'port': 39270,
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

def get_db_connection():
    try:
        conn = pymysql.connect(**db_config)
        return conn
    except pymysql.MySQLError as err:
        print(f"Database Connection Error: {err}")
        return None

# -------------------------
# Authentication
# -------------------------
@app.route('/api/register', methods=['POST'])
def register_user():
    data = request.get_json()
    required_fields = ['name', 'email', 'password']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    try:
        password_hash = generate_password_hash(data['password'])
        cursor.execute("INSERT INTO users (name, email, password_hash, role) VALUES (%s, %s, %s, %s)", 
                       (data['name'], data['email'], password_hash, 'user'))
        conn.commit()
        return jsonify({"message": "User registered successfully", "user_id": cursor.lastrowid}), 201
    except pymysql.err.IntegrityError:
        return jsonify({"error": "Email already exists"}), 409
    finally:
        cursor.close()
        conn.close()

@app.route('/api/login', methods=['POST'])
def login_user():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, password_hash FROM users WHERE email=%s AND role='user'", (email,))
        user = cursor.fetchone()
        if not user or not check_password_hash(user['password_hash'], password):
            return jsonify({"error": "Invalid credentials"}), 401
        return jsonify({"message": "Login successful", "user_id": user['id']}), 200
    finally:
        cursor.close()
        conn.close()

@app.route('/api/register/admin', methods=['POST'])
def register_admin():
    data = request.get_json()
    required_fields = ['name', 'email', 'password']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        password_hash = generate_password_hash(data['password'])
        cursor.execute("INSERT INTO users (name, email, password_hash, role) VALUES (%s, %s, %s, %s)", 
                       (data['name'], data['email'], password_hash, 'admin'))
        conn.commit()
        return jsonify({"message": "Admin registered successfully", "admin_id": cursor.lastrowid}), 201
    except pymysql.err.IntegrityError:
        return jsonify({"error": "Email already exists"}), 409
    finally:
        cursor.close()
        conn.close()

@app.route('/api/login/admin', methods=['POST'])
def login_admin():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, password_hash FROM users WHERE email=%s AND role='admin'", (email,))
        admin = cursor.fetchone()
        if not admin or not check_password_hash(admin['password_hash'], password):
            return jsonify({"error": "Invalid credentials"}), 401
        return jsonify({"message": "Admin login successful", "admin_id": admin['id']}), 200
    finally:
        cursor.close()
        conn.close()

# -------------------------
# Shows
# -------------------------
@app.route('/api/shows', methods=['GET'])
def get_shows():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM shows ORDER BY show_date, show_time")
        shows = cursor.fetchall()
        for s in shows:
            s['show_date'] = s['show_date'].isoformat()
            s['show_time'] = str(s['show_time'])
            s['price'] = str(s['price'])
        return jsonify(shows), 200
    finally:
        cursor.close()
        conn.close()

@app.route('/api/shows/<int:show_id>', methods=['GET'])
def get_show(show_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM shows WHERE id=%s", (show_id,))
        show = cursor.fetchone()
        if not show:
            return jsonify({"error": "Show not found"}), 404
        show['show_date'] = show['show_date'].isoformat()
        show['show_time'] = str(show['show_time'])
        show['price'] = str(show['price'])
        return jsonify(show), 200
    finally:
        cursor.close()
        conn.close()

# Admin CRUD routes for shows
@app.route('/api/admin/shows', methods=['POST'])
def add_show():
    data = request.get_json()
    required_fields = ['title', 'category', 'venue', 'show_date', 'show_time', 'duration', 'price', 'total_seats']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query = """INSERT INTO shows 
        (title, category, description, venue, show_date, show_time, duration, price, total_seats, available_seats, image_url) 
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
        cursor.execute(query, (data['title'], data['category'], data.get('description'), data['venue'],
                               data['show_date'], data['show_time'], data['duration'], data['price'],
                               data['total_seats'], data['total_seats'], data.get('image_url')))
        conn.commit()
        return jsonify({"message": "Show added", "show_id": cursor.lastrowid}), 201
    finally:
        cursor.close()
        conn.close()

@app.route('/api/admin/shows/<int:show_id>', methods=['PUT'])
def update_show(show_id):
    data = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query = """UPDATE shows SET title=%s, category=%s, description=%s, venue=%s, show_date=%s,
                   show_time=%s, duration=%s, price=%s, total_seats=%s, available_seats=%s, image_url=%s
                   WHERE id=%s"""
        cursor.execute(query, (data['title'], data['category'], data.get('description'), data['venue'],
                               data['show_date'], data['show_time'], data['duration'], data['price'],
                               data['total_seats'], data['available_seats'], data.get('image_url'), show_id))
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({"error": "Show not found"}), 404
        return jsonify({"message": "Show updated"}), 200
    finally:
        cursor.close()
        conn.close()

@app.route('/api/admin/shows/<int:show_id>', methods=['DELETE'])
def delete_show(show_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM shows WHERE id=%s", (show_id,))
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({"error": "Show not found"}), 404
        return jsonify({"message": "Show deleted"}), 200
    finally:
        cursor.close()
        conn.close()

@app.route('/api/admin/check-conflict', methods=['POST'])
def check_conflict():
    data = request.get_json()
    venue = data.get('venue')
    show_date = data.get('show_date')
    show_time = data.get('show_time')
    duration = data.get('duration')
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query = """SELECT id, title FROM shows
                   WHERE venue=%s AND show_date=%s AND
                   (%s < ADDTIME(show_time, SEC_TO_TIME(duration*60)) AND
                   ADDTIME(%s, SEC_TO_TIME(%s*60)) > show_time)"""
        cursor.execute(query, (venue, show_date, show_time, show_time, duration))
        conflicts = cursor.fetchall()
        return jsonify({"conflict": bool(conflicts), "conflicting_shows": conflicts}), 200
    finally:
        cursor.close()
        conn.close()

# -------------------------
# Bookings
# -------------------------
@app.route('/api/bookings', methods=['POST'])
def create_booking():
    data = request.get_json()
    user_id = data.get('user_id')
    show_id = data.get('show_id')
    seats = data.get('seats')
    total_amount = data.get('total_amount')
    if not all([user_id, show_id, seats, total_amount]):
        return jsonify({"error": "user_id, show_id, seats, total_amount are required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        conn.begin()
        cursor.execute("SELECT available_seats, price FROM shows WHERE id=%s FOR UPDATE", (show_id,))
        show = cursor.fetchone()
        if not show:
            conn.rollback()
            return jsonify({"error": "Show not found"}), 404
        if show['available_seats'] < len(seats):
            conn.rollback()
            return jsonify({"error": "Not enough available seats"}), 409
        expected_amount = show['price'] * len(seats)
        if Decimal(total_amount) != expected_amount:
            conn.rollback()
            return jsonify({"error": f"Incorrect total amount. Expected {expected_amount}"}), 400
        booking_uuid = str(uuid.uuid4())
        seats_json = json.dumps(seats)
        cursor.execute("INSERT INTO bookings (booking_id, user_id, show_id, seats, total_amount) VALUES (%s,%s,%s,%s,%s)",
                       (booking_uuid, user_id, show_id, seats_json, total_amount))
        cursor.execute("UPDATE shows SET available_seats=available_seats-%s WHERE id=%s", (len(seats), show_id))
        conn.commit()
        return jsonify({"message": "Booking created", "booking_id": booking_uuid}), 201
    finally:
        cursor.close()
        conn.close()

@app.route('/api/bookings/user/<int:user_id>', methods=['GET'])
def get_user_bookings(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""SELECT b.id, b.booking_id, b.seats, b.total_amount, b.status, b.booking_date,
                          s.title, s.category, s.venue, s.show_date, s.show_time
                          FROM bookings b JOIN shows s ON b.show_id=s.id
                          WHERE b.user_id=%s ORDER BY s.show_date, s.show_time""", (user_id,))
        bookings = cursor.fetchall()
        for b in bookings:
            b['show_date'] = b['show_date'].isoformat()
            b['show_time'] = str(b['show_time'])
            b['booking_date'] = b['booking_date'].isoformat()
            b['total_amount'] = str(b['total_amount'])
        return jsonify(bookings), 200
    finally:
        cursor.close()
        conn.close()

@app.route('/api/admin/bookings', methods=['GET'])
def get_all_bookings():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""SELECT b.id, b.booking_id, b.total_amount, b.status, b.booking_date,
                          s.title, s.category, s.venue, u.name as user_name, u.email as user_email
                          FROM bookings b JOIN shows s ON b.show_id=s.id
                          JOIN users u ON b.user_id=u.id ORDER BY b.booking_date DESC""")
        bookings = cursor.fetchall()
        for b in bookings:
            b['booking_date'] = b['booking_date'].isoformat()
            b['total_amount'] = str(b['total_amount'])
        return jsonify(bookings), 200
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
