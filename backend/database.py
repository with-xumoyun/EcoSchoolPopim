
import sqlite3
from pathlib import Path


# =========================================================
# 🌱 ECO SCHOOL POPIM — DATABASE
# =========================================================

BASE_DIR = Path(__file__).resolve().parent

DB_PATH = BASE_DIR / "eco_school.db"


# =========================================================
# 🔌 DATABASE CONNECTION
# =========================================================

def get_connection():
    conn = sqlite3.connect(DB_PATH)

    conn.row_factory = sqlite3.Row

    conn.execute("PRAGMA foreign_keys = ON")

    return conn


# =========================================================
# 🏗 DATABASE INITIALIZATION
# =========================================================

def init_db():

    conn = get_connection()

    cur = conn.cursor()

    # =====================================================
    # 🏫 ROOMS
    # =====================================================

    cur.execute("""
        CREATE TABLE IF NOT EXISTS rooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            class_name TEXT NOT NULL,

            room_number TEXT NOT NULL,

            teacher TEXT NOT NULL,

            responsible TEXT,

            password TEXT NOT NULL,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            UNIQUE(class_name, room_number)
        )
    """)

    # =====================================================
    # 🌱 PLANTS
    # =====================================================

    cur.execute("""
        CREATE TABLE IF NOT EXISTS plants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            room_id INTEGER NOT NULL,

            name TEXT NOT NULL,

            count INTEGER NOT NULL DEFAULT 1,

            image TEXT,

            FOREIGN KEY(room_id)
                REFERENCES rooms(id)
                ON DELETE CASCADE
        )
    """)

    # =====================================================
    # 🔌 SOCKETS
    # =====================================================

    cur.execute("""
        CREATE TABLE IF NOT EXISTS sockets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            room_id INTEGER NOT NULL,

            socket_type TEXT NOT NULL,

            count INTEGER NOT NULL DEFAULT 1,

            FOREIGN KEY(room_id)
                REFERENCES rooms(id)
                ON DELETE CASCADE
        )
    """)

    # =====================================================
    # 🏆 COMPETITIONS
    # =====================================================

    cur.execute("""
        CREATE TABLE IF NOT EXISTS competitions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            description TEXT,

            start_date TEXT,

            end_date TEXT,

            status TEXT DEFAULT 'active',

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # =====================================================
    # ⭐ SCORES
    # =====================================================

    cur.execute("""
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            room_id INTEGER NOT NULL,

            competition_id INTEGER,

            points INTEGER NOT NULL DEFAULT 0,

            reason TEXT,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY(room_id)
                REFERENCES rooms(id)
                ON DELETE CASCADE,

            FOREIGN KEY(competition_id)
                REFERENCES competitions(id)
                ON DELETE SET NULL
        )
    """)

    conn.commit()

    conn.close()

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


# =========================================================
# 🏫 14 TA SINFNI YARATISH / YANGILASH
# =========================================================

def seed_rooms():

    rooms = [

        # 5-SINF
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

        # 6-SINF
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

        # 7-SINF
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

        # 8-SINF
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

        # 9-SINF
        (
            "9.01",
            "115",
            "Pulatova Shahnoza",
            "9.01 sinfi",
            "P-Sh-901-115"
        ),

        # 10-SINF
        (
            "10.01",
            "301",
            "Sultova Iroda",
            "10.01 sinfi",
            "S-I-1001-301"
        ),

        # 11-SINF
        (
            "11.01",
            "206",
            "Mirzatillayeva Munira",
            "11.01 sinfi",
            "M-M-1101-206"
        )
    ]

    conn = get_connection()

    cur = conn.cursor()

    # =====================================================
    # HAR BIR SINFNI TEKSHIRAMIZ
    # =====================================================

    for class_name, room_number, teacher, responsible, password in rooms:

        cur.execute("""
            SELECT id
            FROM rooms
            WHERE class_name = ?
              AND room_number = ?
        """, (
            class_name,
            room_number
        ))

        existing = cur.fetchone()

        # =================================================
        # AGAR SINF MAVJUD BO'LSA
        # MA'LUMOTLARINI YANGILAYMIZ
        # =================================================

        if existing:

            cur.execute("""
                UPDATE rooms

                SET
                    teacher = ?,
                    responsible = ?,
                    password = ?

                WHERE id = ?
            """, (
                teacher,
                responsible,
                password,
                existing["id"]
            ))

        # =================================================
        # AGAR SINF YO'Q BO'LSA
        # YANGI SINF YARATAMIZ
        # =================================================

        else:

            cur.execute("""
                INSERT INTO rooms (
                    class_name,
                    room_number,
                    teacher,
                    responsible,
                    password
                )

                VALUES (?, ?, ?, ?, ?)
            """, (
                class_name,
                room_number,
                teacher,
                responsible,
                password
            ))

    conn.commit()

    conn.close()

    print("==========================================")
    print("🏫 14 TA SINF TEKSHIRILDI")
    print("🔐 14 TA PAROL YANGILANDI")
    print("==========================================")


# =========================================================
# 🚀 DATABASE START
# =========================================================

if __name__ == "__main__":

    init_db()

    seed_rooms()

    print("")
    print("==========================================")
    print("✅ ECO SCHOOL POPIM DATABASE TAYYOR!")
    print("==========================================")