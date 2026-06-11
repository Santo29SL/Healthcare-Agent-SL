from backend.app.database import get_connection

def create_medical_profiles(user_id, blood_group, allergies):
    conn = get_connection("medical_profiles")
    try:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO medical_profiles (user_id, blood_group, allergies) VALUES (%s, %s, %s)",
                (user_id, blood_group, allergies)
            )
            conn.commit()
        finally:
            cursor.close()
    finally:
        conn.close()

def get_medical_profiles(user_id):
    conn = get_connection("medical_profiles")
    try:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM medical_profiles WHERE user_id = %s", (user_id,))
            return cursor.fetchall()
        finally:
            cursor.close()
    finally:
        conn.close()

def update_medical_profiles(user_id, blood_group, allergies):
    conn = get_connection("medical_profiles")
    try:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "UPDATE medical_profiles SET blood_group = %s, allergies = %s WHERE user_id = %s",
                (blood_group, allergies, user_id)
            )
            conn.commit()
        finally:
            cursor.close()
    finally:
        conn.close()

def delete_medical_profiles(user_id):
    conn = get_connection("medical_profiles")
    try:
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM medical_profiles WHERE user_id = %s", (user_id,))
            conn.commit()
        finally:
            cursor.close()
    finally:
        conn.close()
