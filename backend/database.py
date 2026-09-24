import sqlite3

DATABASE = "eco_school.db"


def get_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row

    # Foreign key ishlashi uchun
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def init_database():
    connection = get_connection()
    cursor = connection.cursor()

    # ==========================================
    # 🏫 XONALAR
    # ==========================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_name TEXT NOT NULL,
            room_number TEXT NOT NULL,
            teacher TEXT NOT NULL,
            responsible TEXT,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ==========================================
    # 🌱 O'SIMLIKLAR
    # ==========================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS plants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            count INTEGER NOT NULL DEFAULT 1,
            image TEXT,
            FOREIGN KEY (room_id) REFERENCES rooms(id)
            ON DELETE CASCADE
        )
    """)

    # ==========================================
    # 🔌 ROZETKALAR
    # ==========================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sockets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_id INTEGER NOT NULL,
            socket_type TEXT NOT NULL,
            count INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY (room_id) REFERENCES rooms(id)
            ON DELETE CASCADE
        )
    """)

    # ==========================================
    # 🏆 MUSOBAQALAR
    # ==========================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS competitions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            description TEXT,

            start_date TEXT,

            end_date TEXT,

            status TEXT NOT NULL DEFAULT 'active',

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ==========================================
    # ⭐ BALLAR
    # ==========================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            room_id INTEGER NOT NULL,

            competition_id INTEGER,

            points INTEGER NOT NULL,

            reason TEXT,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (room_id)
                REFERENCES rooms(id)
                ON DELETE CASCADE,

            FOREIGN KEY (competition_id)
                REFERENCES competitions(id)
                ON DELETE SET NULL
        )
    """)

    connection.commit()
    connection.close()


# ==========================================
# 🏫 BOSHLANG'ICH XONALAR
# ==========================================

def seed_rooms():

    connection = get_connection()
    cursor = connection.cursor()

    rooms = [

        (
            "5.01",
            "213",
            "Toshtemirova Latofat",
            "5.01 sinfi",
            "T-L-501-213"
        ),

        (
            "5.02",
            "104",
            "Asqarova Noila",
            "5.02 sinfi",
            "A-N-502-104"
        ),

        (
            "6.01",
            "103",
            "Yunusova Dilnoza",
            "6.01 sinfi",
            "Y-D-601-103"
        ),

        (
            "6.02",
            "217",
            "Raximov Nohidjon",
            "6.02 sinfi",
            "R-N-602-217"
        ),

        (
            "7.01",
            "307",
            "Usmonova Dilafruz",
            "7.01 sinfi",
            "U-D-701-307"
        ),

        (
            "7.02",
            "204",
            "Yuldasheva Mastura",
            "7.02 sinfi",
            "Y-M-702-204"
        ),

        (
            "7.03",
            "303",
            "Abdullayeva Shahnoza",
            "7.03 sinfi",
            "A-Sh-703-303"
        ),

        (
            "7.04",
            "218",
            "Botirova Shahnoza",
            "7.04 sinfi",
            "B-Sh-704-218"
        ),

        (
            "8.01",
            "216",
            "Mahmudova Noila",
            "8.01 sinfi",
            "M-N-801-216"
        ),

        (
            "8.02",
            "215",
            "Yusupova Gulhayo",
            "8.02 sinfi",
            "Y-G-802-215"
        ),

        (
            "8.03",
            "101",
            "Yo'ldasheva Feruza",
            "8.03 sinfi",
            "Y-F-803-101"
        ),

        (
            "9.01",
            "115",
            "Pulatova Shahnoza",
            "9.01 sinfi",
            "P-Sh-901-115"
        ),

        (
            "10.01",
            "301",
            "Sultova Iroda",
            "10.01 sinfi",
            "S-I-1001-301"
        ),

        (
            "11.01",
            "206",
            "Mirzatillayeva Munira",
            "11.01 sinfi",
            "M-M-1101-206"
        )
    ]


    # ==========================================
    # 🔎 XONALAR MAVJUDLIGINI TEKSHIRISH
    # ==========================================

    for room in rooms:

        cursor.execute(
            """
            SELECT id
            FROM rooms
            WHERE class_name = ?
            AND room_number = ?
            """,
            (
                room[0],
                room[1]
            )
        )

        existing_room = cursor.fetchone()


        # Agar xona mavjud bo'lmasa qo'shamiz
        if existing_room is None:

            cursor.execute(
                """
                INSERT INTO rooms
                (
                    class_name,
                    room_number,
                    teacher,
                    responsible,
                    password
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                room
            )


    connection.commit()
    connection.close()


# ==========================================
# 🚀 DATABASE ISHGA TUSHIRISH
# ==========================================

if __name__ == "__main__":

    init_database()

    seed_rooms()

    print()
    print("==========================================")
    print("🌱 Eco School PopIm")
    print("==========================================")
    print("✅ Database tayyor!")
    print("🏫 Xonalar jadvali tayyor")
    print("🌱 O'simliklar jadvali tayyor")
    print("🔌 Rozetkalar jadvali tayyor")
    print("🏆 Musobaqalar jadvali tayyor")
    print("⭐ Ballar jadvali tayyor")
    print("==========================================")