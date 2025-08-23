import pymysql

connection = pymysql.connect(
    host="hopper.proxy.rlwy.net",
    user="root",
    password="DjijtRCyVJOKljAAWkUuabRyJWCmjXqf",
    database="railway",
    port=39270
)

cursor = connection.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    role ENUM('user', 'admin') DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
 );
""")


cursor.execute("""
CREATE TABLE IF NOT EXISTS shows (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(200) NOT NULL,
    category ENUM('movie', 'concert', 'theater', 'sports') NOT NULL,
    description TEXT,
    venue VARCHAR(200) NOT NULL,
    show_date DATE NOT NULL,
    show_time TIME NOT NULL,
    duration INT NOT NULL, -- in minutes
    price DECIMAL(10,2) NOT NULL,
    total_seats INT NOT NULL,
    available_seats INT NOT NULL,
    image_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS bookings (
    id INT PRIMARY KEY AUTO_INCREMENT,
    booking_id VARCHAR(50) UNIQUE NOT NULL,
    user_id INT NOT NULL,
    show_id INT NOT NULL,
    seats JSON NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    status ENUM('confirmed', 'cancelled') DEFAULT 'confirmed',
    booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (show_id) REFERENCES shows(id)
);
""")

connection.commit()
print("✅ Tables created successfully!")

cursor.close()
connection.close()
