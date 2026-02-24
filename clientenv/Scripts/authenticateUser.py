import hashlib
import connectionInfo

def authenticate_user(username_attempt, password_attempt):
    cursor = None

    try:
        conn = connectionInfo.get_connection()
        cursor = conn.cursor()

        query = """
            SELECT user_id, user_password, user_role, username
            FROM users
            WHERE userid = %s
        """

        cursor.execute(query, (username_attempt,))
        result = cursor.fetchone()

        if not result:
            return False

        stored_hash = result[1]

        attempt_hash = hashlib.sha256(
            password_attempt.encode()
        ).hexdigest()

        if attempt_hash == stored_hash:
            return result
        else:
            return False

    except Exception as e:
        print(f"Database error: {e}")
        return False

    finally:
        if cursor:
            cursor.close()