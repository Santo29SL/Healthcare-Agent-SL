from backend.app.database import get_connection
from langchain_core.messages import HumanMessage, AIMessage

def store_conversation(user_id, role, message):
    conn = get_connection("conversation")
    try:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO conversations (user_id, role, message) VALUES (%s, %s, %s)",
                (user_id, role, message)
            )
            conn.commit()
        finally:
            cursor.close()
    finally:
        conn.close()
