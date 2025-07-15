import sqlite3


def show_user_table_columns(db_path="bot.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(users);")
    columns = cursor.fetchall()
    print("users jadvalidagi ustunlar:")
    for col in columns:
        print(f"{col[1]} ({col[2]})")
    conn.close()


# chaqiramiz
show_user_table_columns()
