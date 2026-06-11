import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "Satlav@76")
DB_PORT = int(os.getenv("DB_PORT", 3306))


def init_db():
    print(f"Connecting to MySQL at {DB_HOST}:{DB_PORT} as {DB_USER}...")
    print(f"Using Password: '{DB_PASSWORD}'")
    try:
        # Connect to MySQL server (no database selected)
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT
        )
        cursor = conn.cursor()
        print("Connected to MySQL server.")

        # 1. Create 'user' database
        print("Creating 'user' database...")
        cursor.execute("CREATE DATABASE IF NOT EXISTS user")
        cursor.execute("USE user")
        
        # Create 'users' table
        print("Creating 'users' table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                full_name VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL
            )
        """)
        
        # 2. Create 'medical_profiles' database
        print("Creating 'medical_profiles' database...")
        cursor.execute("CREATE DATABASE IF NOT EXISTS medical_profiles")
        cursor.execute("USE medical_profiles")
        
        # Create 'medical_profiles' table
        print("Creating 'medical_profiles' table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS medical_profiles (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                blood_group VARCHAR(10),
                allergies TEXT,
                FOREIGN KEY (user_id) REFERENCES user.users(id)
            )
        """)

        # 3. Create 'conversation' database
        print("Creating 'conversation' database...")
        cursor.execute("CREATE DATABASE IF NOT EXISTS conversation")
        cursor.execute("USE conversation")

        # Create 'conversations' table
        print("Creating 'conversations' table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                role VARCHAR(20) NOT NULL,
                message TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 4. Create 'DoctorDB' database
        print("Creating 'DoctorDB' database...")
        cursor.execute("CREATE DATABASE IF NOT EXISTS DoctorDB")
        cursor.execute("USE DoctorDB")

        # Create 'doctors' table
        print("Creating 'doctors' table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS doctors (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                specialty VARCHAR(255) NOT NULL,
                phone_number VARCHAR(50) NOT NULL,
                latitude DOUBLE NOT NULL,
                longitude DOUBLE NOT NULL
            )
        """)

        # Insert sample doctors/clinics
        print("Checking sample doctors data...")
        cursor.execute("SELECT COUNT(*) FROM doctors")
        count = cursor.fetchone()[0]
        if count == 0:
            print("Seeding sample doctors...")
            sample_doctors = [
                ("Rahul Sharma", "Cardiologist", "9876543210", 12.9716, 77.5946),
                ("Anita Verma", "Dermatologist", "9123456780", 12.9721, 77.5933),
                ("Vikram Rao", "General Physician", "9988776655", 12.9750, 77.5900),
                ("Sneha Reddy", "Pediatrician", "9880123456", 12.9300, 77.6200),
                ("Rohan Das", "Orthopedician", "9770987654", 12.9500, 77.6000),
                ("Priya Patel", "Gynecologist", "9660112233", 13.0000, 77.5800)
            ]
            cursor.executemany("""
                INSERT INTO doctors (name, specialty, phone_number, latitude, longitude)
                VALUES (%s, %s, %s, %s, %s)
            """, sample_doctors)
        
        conn.commit()
        cursor.close()
        conn.close()
        print("Database initialization completed successfully.")
        
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    init_db()
