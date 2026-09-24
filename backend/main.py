from pathlib import Path
import sqlite3
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from database import get_connection, init_database, seed_rooms


# =========================================================
# 🌱 ECO SCHOOL POPIM
# Backend v4.0 — Eco Score System
# =========================================================

app = FastAPI(
    title="Eco School PopIm API",
    version="4.0.0",
    description="Eco School PopIm — raqamli ekologik maktab tizimi"
)


# =========================================================
# 🌐 CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# 🔐 ADMIN
# =========================================================

ADMIN_CODE = "popim242526"


# =========================================================
# 🗄️ DATABASE
# =========================================================

init_database()
seed_rooms()


# =========================================================
# 📦 MODELLAR
# =========================================================

class RoomCreate(BaseModel):
    class_name: str
    room_number: str
    teacher: str
    responsible: str = ""
    password: str


class RoomUpdate(BaseModel):
    class_name: str
    room_number: str
    teacher: str
    responsible: str = ""
    password: str


class LoginRequest(BaseModel):
    password: str


class PlantCreate(BaseModel):
    name: str
    count: int = 1
    image: Optional[str] = None


class PlantUpdate(BaseModel):
    name: str
    count: int = 1
    image: Optional[str] = None


class SocketCreate(BaseModel):
    socket_type: str
    count: int = 1


class AdminRequest(BaseModel):
    code: str


class AdminRoomCreate(BaseModel):
    code: str
    class_name: str
    room_number: str
    teacher: str
    responsible: str = ""
    password: str


class CompetitionCreate(BaseModel):
    code: str
    name: str
    description: str = ""
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class CompetitionUpdate(BaseModel):
    code: str
    name: str
    description: str = ""
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    status: str = "active"


class ScoreCreate(BaseModel):
    code: str
    room_id: int
    competition_id: Optional[int] = None
    points: int
    reason: str = ""


class ScoreUpdate(BaseModel):
    code: str
    points: int
    reason: str = ""


# =========================================================
# 🧰 YORDAMCHI FUNKSIYALAR
# =========================================================

def check_admin(code: str):

    if code != ADMIN_CODE:
        raise HTTPException(
            status_code=403,
            detail="Admin kodi noto‘g‘ri"
        )


def get_floor(room_number: str):

    try:

        number = int(room_number)

        if number >= 400:
            return 4

        if number >= 300:
            return 3

        if number >= 200:
            return 2

        if number >= 100:
            return 1

        return 1

    except:

        return 1


def room_dict(room, include_password=False):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            COALESCE(SUM(count), 0)
            AS total
        FROM plants
        WHERE room_id = ?
        """,
        (room["id"],)
    )

    plant_count = cursor.fetchone()["total"]

    cursor.execute(
        """
        SELECT
            COALESCE(SUM(count), 0)
            AS total
        FROM sockets
        WHERE room_id = ?
        """,
        (room["id"],)
    )

    socket_count = cursor.fetchone()["total"]

    result = {
        "id": room["id"],
        "class_name": room["class_name"],
        "room_number": room["room_number"],
        "teacher": room["teacher"],
        "responsible": room["responsible"],
        "floor": get_floor(room["room_number"]),
        "plant_count": plant_count,
        "socket_count": socket_count
    }

    if include_password:
        result["password"] = room["password"]

    connection.close()

    return result


def get_room(room_id: int):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM rooms
        WHERE id = ?
        """,
        (room_id,)
    )

    room = cursor.fetchone()

    connection.close()

    return room


def get_full_room(room_id: int, include_password=False):

    room = get_room(room_id)

    if room is None:

        raise HTTPException(
            status_code=404,
            detail="Xona topilmadi"
        )

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM plants
        WHERE room_id = ?
        ORDER BY id DESC
        """,
        (room_id,)
    )

    plants = [
        dict(row)
        for row in cursor.fetchall()
    ]

    cursor.execute(
        """
        SELECT *
        FROM sockets
        WHERE room_id = ?
        ORDER BY id DESC
        """,
        (room_id,)
    )

    sockets = [
        dict(row)
        for row in cursor.fetchall()
    ]

    connection.close()

    result = room_dict(
        room,
        include_password=include_password
    )

    result["plants"] = plants
    result["sockets"] = sockets

    return result


# =========================================================
# 🏠 ROOT
# =========================================================

@app.get("/")
def root():

    return {
        "status": "success",
        "message": "🌱 Eco School PopIm backend ishlayapti!",
        "version": "4.0.0",
        "features": [
            "rooms",
            "plants",
            "sockets",
            "qr",
            "competitions",
            "eco_score"
        ]
    }


# =========================================================
# ❤️ HEALTH
# =========================================================

@app.get("/api/health")
def health():

    return {
        "status": "ok",
        "database": "connected",
        "version": "4.0.0"
    }


# =========================================================
# 🏫 ROOMS
# =========================================================

@app.get("/api/rooms")
def get_rooms():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM rooms
        ORDER BY
            CAST(room_number AS INTEGER),
            class_name
        """
    )

    rooms = cursor.fetchall()

    connection.close()

    return [
        room_dict(room)
        for room in rooms
    ]


@app.get("/api/rooms/{room_id}")
def get_room_details(room_id: int):

    return get_full_room(
        room_id,
        include_password=False
    )


# =========================================================
# 🔐 ROOM LOGIN
# =========================================================

@app.post("/api/rooms/{room_id}/login")
def room_login(
    room_id: int,
    request: LoginRequest
):

    room = get_room(room_id)

    if room is None:

        raise HTTPException(
            status_code=404,
            detail="Xona topilmadi"
        )

    if request.password != room["password"]:

        raise HTTPException(
            status_code=401,
            detail="Xona paroli noto‘g‘ri"
        )

    return get_full_room(
        room_id,
        include_password=True
    )


# =========================================================
# 🔐 ADMIN VERIFY
# =========================================================

@app.post("/api/admin/verify")
def verify_admin(request: AdminRequest):

    check_admin(request.code)

    return {
        "success": True,
        "message": "Admin tasdiqlandi"
    }


# =========================================================
# ➕ ADMIN — YANGI XONA
# =========================================================

@app.post("/api/admin/rooms")
def create_room(request: AdminRoomCreate):

    check_admin(request.code)

    if not request.class_name.strip():
        raise HTTPException(
            status_code=400,
            detail="Sinf nomi kiritilmagan"
        )

    if not request.room_number.strip():
        raise HTTPException(
            status_code=400,
            detail="Xona raqami kiritilmagan"
        )

    if not request.teacher.strip():
        raise HTTPException(
            status_code=400,
            detail="O‘qituvchi kiritilmagan"
        )

    if not request.password.strip():
        raise HTTPException(
            status_code=400,
            detail="Xona paroli kiritilmagan"
        )

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id
        FROM rooms
        WHERE class_name = ?
        AND room_number = ?
        """,
        (
            request.class_name,
            request.room_number
        )
    )

    if cursor.fetchone():

        connection.close()

        raise HTTPException(
            status_code=409,
            detail="Bu sinf va xona allaqachon mavjud"
        )

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
        (
            request.class_name,
            request.room_number,
            request.teacher,
            request.responsible,
            request.password
        )
    )

    room_id = cursor.lastrowid

    connection.commit()

    cursor.execute(
        """
        SELECT *
        FROM rooms
        WHERE id = ?
        """,
        (room_id,)
    )

    room = cursor.fetchone()

    connection.close()

    return room_dict(
        room,
        include_password=True
    )


# =========================================================
# ✏️ ROOM UPDATE
# =========================================================

@app.put("/api/rooms/{room_id}")
def update_room(
    room_id: int,
    room: RoomUpdate
):

    existing = get_room(room_id)

    if existing is None:

        raise HTTPException(
            status_code=404,
            detail="Xona topilmadi"
        )

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE rooms
        SET
            class_name = ?,
            room_number = ?,
            teacher = ?,
            responsible = ?,
            password = ?
        WHERE id = ?
        """,
        (
            room.class_name,
            room.room_number,
            room.teacher,
            room.responsible,
            room.password,
            room_id
        )
    )

    connection.commit()

    cursor.execute(
        """
        SELECT *
        FROM rooms
        WHERE id = ?
        """,
        (room_id,)
    )

    updated = cursor.fetchone()

    connection.close()

    return room_dict(
        updated,
        include_password=True
    )


# =========================================================
# 🗑️ ADMIN — ROOM DELETE
# =========================================================

@app.delete("/api/admin/rooms/{room_id}")
def delete_room(
    room_id: int,
    request: AdminRequest
):

    check_admin(request.code)

    existing = get_room(room_id)

    if existing is None:

        raise HTTPException(
            status_code=404,
            detail="Xona topilmadi"
        )

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM rooms
        WHERE id = ?
        """,
        (room_id,)
    )

    connection.commit()
    connection.close()

    return {
        "success": True,
        "message": "Xona o‘chirildi"
    }


# =========================================================
# 🌱 PLANTS
# =========================================================

@app.post("/api/rooms/{room_id}/plants")
def create_plant(
    room_id: int,
    plant: PlantCreate
):

    if get_room(room_id) is None:

        raise HTTPException(
            status_code=404,
            detail="Xona topilmadi"
        )

    if plant.count < 1:

        raise HTTPException(
            status_code=400,
            detail="O‘simlik soni kamida 1 bo‘lishi kerak"
        )

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO plants
        (
            room_id,
            name,
            count,
            image
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            room_id,
            plant.name,
            plant.count,
            plant.image
        )
    )

    plant_id = cursor.lastrowid

    connection.commit()

    cursor.execute(
        """
        SELECT *
        FROM plants
        WHERE id = ?
        """,
        (plant_id,)
    )

    result = dict(cursor.fetchone())

    connection.close()

    return result


@app.put("/api/plants/{plant_id}")
def update_plant(
    plant_id: int,
    plant: PlantUpdate
):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM plants
        WHERE id = ?
        """,
        (plant_id,)
    )

    existing = cursor.fetchone()

    if existing is None:

        connection.close()

        raise HTTPException(
            status_code=404,
            detail="O‘simlik topilmadi"
        )

    cursor.execute(
        """
        UPDATE plants
        SET
            name = ?,
            count = ?,
            image = ?
        WHERE id = ?
        """,
        (
            plant.name,
            plant.count,
            plant.image,
            plant_id
        )
    )

    connection.commit()

    cursor.execute(
        """
        SELECT *
        FROM plants
        WHERE id = ?
        """,
        (plant_id,)
    )

    result = dict(cursor.fetchone())

    connection.close()

    return result


@app.delete("/api/plants/{plant_id}")
def delete_plant(plant_id: int):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM plants
        WHERE id = ?
        """,
        (plant_id,)
    )

    if cursor.rowcount == 0:

        connection.close()

        raise HTTPException(
            status_code=404,
            detail="O‘simlik topilmadi"
        )

    connection.commit()
    connection.close()

    return {
        "success": True,
        "message": "O‘simlik o‘chirildi"
    }


# =========================================================
# 🔌 SOCKETS
# =========================================================

@app.post("/api/rooms/{room_id}/sockets")
def create_socket(
    room_id: int,
    socket: SocketCreate
):

    if get_room(room_id) is None:

        raise HTTPException(
            status_code=404,
            detail="Xona topilmadi"
        )

    if socket.count < 1:

        raise HTTPException(
            status_code=400,
            detail="Rozetka soni noto‘g‘ri"
        )

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO sockets
        (
            room_id,
            socket_type,
            count
        )
        VALUES (?, ?, ?)
        """,
        (
            room_id,
            socket.socket_type,
            socket.count
        )
    )

    socket_id = cursor.lastrowid

    connection.commit()

    cursor.execute(
        """
        SELECT *
        FROM sockets
        WHERE id = ?
        """,
        (socket_id,)
    )

    result = dict(cursor.fetchone())

    connection.close()

    return result


@app.delete("/api/sockets/{socket_id}")
def delete_socket(socket_id: int):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM sockets
        WHERE id = ?
        """,
        (socket_id,)
    )

    if cursor.rowcount == 0:

        connection.close()

        raise HTTPException(
            status_code=404,
            detail="Rozetka topilmadi"
        )

    connection.commit()
    connection.close()

    return {
        "success": True,
        "message": "Rozetka o‘chirildi"
    }


# =========================================================
# 📊 STATISTICS
# =========================================================

@app.get("/api/statistics")
def statistics():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT COUNT(*) AS total
        FROM rooms
        """
    )

    total_rooms = cursor.fetchone()["total"]

    cursor.execute(
        """
        SELECT COALESCE(SUM(count), 0) AS total
        FROM plants
        """
    )

    total_plants = cursor.fetchone()["total"]

    cursor.execute(
        """
        SELECT COALESCE(SUM(count), 0) AS total
        FROM sockets
        """
    )

    total_sockets = cursor.fetchone()["total"]

    cursor.execute(
        """
        SELECT DISTINCT room_number
        FROM rooms
        """
    )

    room_numbers = [
        row["room_number"]
        for row in cursor.fetchall()
    ]

    floors = set()

    for room_number in room_numbers:
        floors.add(get_floor(room_number))

    # ⭐ JAMI ECO SCORE

    cursor.execute(
        """
        SELECT COALESCE(SUM(points), 0) AS total
        FROM scores
        """
    )

    total_score = cursor.fetchone()["total"]

    # 🏆 MUSOBAQALAR

    cursor.execute(
        """
        SELECT COUNT(*) AS total
        FROM competitions
        """
    )

    total_competitions = cursor.fetchone()["total"]

    connection.close()

    return {
        "rooms": total_rooms,
        "plants": total_plants,
        "sockets": total_sockets,
        "floors": len(floors),
        "eco_score": total_score,
        "competitions": total_competitions
    }


# =========================================================
# 📊 OVERVIEW
# =========================================================

@app.get("/api/overview")
def overview():

    connection = get_connection()
    cursor = connection.cursor()

    # -----------------------------------------
    # 🏢 QAVATLAR
    # -----------------------------------------

    cursor.execute(
        """
        SELECT *
        FROM rooms
        ORDER BY room_number
        """
    )

    rooms = cursor.fetchall()

    floors = {}

    for room in rooms:

        floor = get_floor(room["room_number"])

        if floor not in floors:

            floors[floor] = {
                "floor": floor,
                "rooms": 0,
                "classes": []
            }

        floors[floor]["rooms"] += 1

        floors[floor]["classes"].append({
            "class_name": room["class_name"],
            "room_number": room["room_number"],
            "teacher": room["teacher"]
        })

    # -----------------------------------------
    # 🌱 O'SIMLIK TURLARI
    # -----------------------------------------

    cursor.execute(
        """
        SELECT
            name,
            SUM(count) AS total
        FROM plants
        GROUP BY name
        ORDER BY total DESC
        """
    )

    plants_by_type = [
        dict(row)
        for row in cursor.fetchall()
    ]

    # -----------------------------------------
    # 🔌 ROZETKA TURLARI
    # -----------------------------------------

    cursor.execute(
        """
        SELECT
            socket_type AS type,
            SUM(count) AS total
        FROM sockets
        GROUP BY socket_type
        ORDER BY total DESC
        """
    )

    sockets_by_type = [
        dict(row)
        for row in cursor.fetchall()
    ]

    # -----------------------------------------
    # ⭐ ECO SCORE
    # -----------------------------------------

    cursor.execute(
        """
        SELECT
            rooms.id AS room_id,
            rooms.class_name,
            rooms.room_number,
            COALESCE(SUM(scores.points), 0) AS total_score
        FROM rooms

        LEFT JOIN scores
        ON rooms.id = scores.room_id

        GROUP BY rooms.id

        ORDER BY total_score DESC
        """
    )

    leaderboard = [
        dict(row)
        for row in cursor.fetchall()
    ]

    # -----------------------------------------
    # 🏆 MUSOBAQALAR
    # -----------------------------------------

    cursor.execute(
        """
        SELECT
            id,
            name,
            description,
            start_date,
            end_date,
            status,
            created_at
        FROM competitions
        ORDER BY id DESC
        """
    )

    competitions = [
        dict(row)
        for row in cursor.fetchall()
    ]

    connection.close()

    return {
        "floors": list(
            sorted(
                floors.values(),
                key=lambda x: x["floor"]
            )
        ),

        "plants_by_type": plants_by_type,

        "sockets_by_type": sockets_by_type,

        "leaderboard": leaderboard,

        "competitions": competitions
    }


# =========================================================
# 🏆 COMPETITIONS
# =========================================================

@app.get("/api/competitions")
def get_competitions():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            name,
            description,
            start_date,
            end_date,
            status,
            created_at
        FROM competitions
        ORDER BY id DESC
        """
    )

    competitions = [
        dict(row)
        for row in cursor.fetchall()
    ]

    connection.close()

    return competitions


@app.post("/api/admin/competitions")
def create_competition(
    competition: CompetitionCreate
):

    check_admin(competition.code)

    if not competition.name.strip():

        raise HTTPException(
            status_code=400,
            detail="Musobaqa nomini kiriting"
        )

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO competitions
        (
            name,
            description,
            start_date,
            end_date,
            status
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            competition.name,
            competition.description,
            competition.start_date,
            competition.end_date,
            "active"
        )
    )

    competition_id = cursor.lastrowid

    connection.commit()

    cursor.execute(
        """
        SELECT *
        FROM competitions
        WHERE id = ?
        """,
        (competition_id,)
    )

    result = dict(cursor.fetchone())

    connection.close()

    return result


@app.put("/api/admin/competitions/{competition_id}")
def update_competition(
    competition_id: int,
    competition: CompetitionUpdate
):

    check_admin(competition.code)

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id
        FROM competitions
        WHERE id = ?
        """,
        (competition_id,)
    )

    if cursor.fetchone() is None:

        connection.close()

        raise HTTPException(
            status_code=404,
            detail="Musobaqa topilmadi"
        )

    cursor.execute(
        """
        UPDATE competitions
        SET
            name = ?,
            description = ?,
            start_date = ?,
            end_date = ?,
            status = ?
        WHERE id = ?
        """,
        (
            competition.name,
            competition.description,
            competition.start_date,
            competition.end_date,
            competition.status,
            competition_id
        )
    )

    connection.commit()

    cursor.execute(
        """
        SELECT *
        FROM competitions
        WHERE id = ?
        """,
        (competition_id,)
    )

    result = dict(cursor.fetchone())

    connection.close()

    return result


@app.delete("/api/admin/competitions/{competition_id}")
def delete_competition(
    competition_id: int,
    request: AdminRequest
):

    check_admin(request.code)

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM competitions
        WHERE id = ?
        """,
        (competition_id,)
    )

    if cursor.rowcount == 0:

        connection.close()

        raise HTTPException(
            status_code=404,
            detail="Musobaqa topilmadi"
        )

    connection.commit()
    connection.close()

    return {
        "success": True,
        "message": "Musobaqa o‘chirildi"
    }


# =========================================================
# ⭐ SCORES
# =========================================================

@app.get("/api/scores")
def get_scores():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            scores.id,
            scores.room_id,
            rooms.class_name,
            rooms.room_number,

            scores.competition_id,

            competitions.name
            AS competition_name,

            scores.points,
            scores.reason,
            scores.created_at

        FROM scores

        INNER JOIN rooms
        ON rooms.id = scores.room_id

        LEFT JOIN competitions
        ON competitions.id = scores.competition_id

        ORDER BY scores.id DESC
        """
    )

    scores = [
        dict(row)
        for row in cursor.fetchall()
    ]

    connection.close()

    return scores


@app.get("/api/rooms/{room_id}/scores")
def get_room_scores(room_id: int):

    if get_room(room_id) is None:

        raise HTTPException(
            status_code=404,
            detail="Xona topilmadi"
        )

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            scores.id,
            scores.points,
            scores.reason,
            scores.created_at,

            scores.competition_id,

            competitions.name
            AS competition_name

        FROM scores

        LEFT JOIN competitions
        ON competitions.id = scores.competition_id

        WHERE scores.room_id = ?

        ORDER BY scores.id DESC
        """,
        (room_id,)
    )

    scores = [
        dict(row)
        for row in cursor.fetchall()
    ]

    # Jami ball

    cursor.execute(
        """
        SELECT
            COALESCE(SUM(points), 0)
            AS total
        FROM scores
        WHERE room_id = ?
        """,
        (room_id,)
    )

    total = cursor.fetchone()["total"]

    connection.close()

    return {
        "room_id": room_id,
        "total_score": total,
        "scores": scores
    }


@app.post("/api/admin/scores")
def create_score(
    score: ScoreCreate
):

    check_admin(score.code)

    if score.points == 0:

        raise HTTPException(
            status_code=400,
            detail="Ball 0 bo‘lishi mumkin emas"
        )

    if get_room(score.room_id) is None:

        raise HTTPException(
            status_code=404,
            detail="Xona topilmadi"
        )

    if score.competition_id is not None:

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT id
            FROM competitions
            WHERE id = ?
            """,
            (score.competition_id,)
        )

        competition = cursor.fetchone()

        connection.close()

        if competition is None:

            raise HTTPException(
                status_code=404,
                detail="Musobaqa topilmadi"
            )

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO scores
        (
            room_id,
            competition_id,
            points,
            reason
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            score.room_id,
            score.competition_id,
            score.points,
            score.reason
        )
    )

    score_id = cursor.lastrowid

    connection.commit()

    cursor.execute(
        """
        SELECT
            scores.id,
            scores.room_id,
            rooms.class_name,
            rooms.room_number,
            scores.competition_id,
            competitions.name
            AS competition_name,
            scores.points,
            scores.reason,
            scores.created_at

        FROM scores

        INNER JOIN rooms
        ON rooms.id = scores.room_id

        LEFT JOIN competitions
        ON competitions.id = scores.competition_id

        WHERE scores.id = ?
        """,
        (score_id,)
    )

    result = dict(cursor.fetchone())

    connection.close()

    return result


@app.put("/api/admin/scores/{score_id}")
def update_score(
    score_id: int,
    score: ScoreUpdate
):

    check_admin(score.code)

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id
        FROM scores
        WHERE id = ?
        """,
        (score_id,)
    )

    if cursor.fetchone() is None:

        connection.close()

        raise HTTPException(
            status_code=404,
            detail="Ball yozuvi topilmadi"
        )

    cursor.execute(
        """
        UPDATE scores
        SET
            points = ?,
            reason = ?
        WHERE id = ?
        """,
        (
            score.points,
            score.reason,
            score_id
        )
    )

    connection.commit()

    cursor.execute(
        """
        SELECT
            scores.id,
            scores.room_id,
            rooms.class_name,
            rooms.room_number,
            scores.competition_id,
            competitions.name
            AS competition_name,
            scores.points,
            scores.reason,
            scores.created_at

        FROM scores

        INNER JOIN rooms
        ON rooms.id = scores.room_id

        LEFT JOIN competitions
        ON competitions.id = scores.competition_id

        WHERE scores.id = ?
        """,
        (score_id,)
    )

    result = dict(cursor.fetchone())

    connection.close()

    return result


@app.delete("/api/admin/scores/{score_id}")
def delete_score(
    score_id: int,
    request: AdminRequest
):

    check_admin(request.code)

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM scores
        WHERE id = ?
        """,
        (score_id,)
    )

    if cursor.rowcount == 0:

        connection.close()

        raise HTTPException(
            status_code=404,
            detail="Ball yozuvi topilmadi"
        )

    connection.commit()
    connection.close()

    return {
        "success": True,
        "message": "Ball yozuvi o‘chirildi"
    }


# =========================================================
# 🏆 LEADERBOARD
# =========================================================

@app.get("/api/leaderboard")
def leaderboard():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT

            rooms.id AS room_id,

            rooms.class_name,

            rooms.room_number,

            rooms.teacher,

            COALESCE(
                SUM(scores.points),
                0
            ) AS total_score

        FROM rooms

        LEFT JOIN scores
        ON rooms.id = scores.room_id

        GROUP BY rooms.id

        ORDER BY total_score DESC
        """
    )

    result = [
        dict(row)
        for row in cursor.fetchall()
    ]

    connection.close()

    # 🏅 O'RINLARNI BERISH

    for index, item in enumerate(result):

        item["rank"] = index + 1

    return result


# =========================================================
# 🏆 MUSOBAQA LEADERBOARD
# =========================================================

@app.get("/api/competitions/{competition_id}/leaderboard")
def competition_leaderboard(
    competition_id: int
):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id
        FROM competitions
        WHERE id = ?
        """,
        (competition_id,)
    )

    if cursor.fetchone() is None:

        connection.close()

        raise HTTPException(
            status_code=404,
            detail="Musobaqa topilmadi"
        )

    cursor.execute(
        """
        SELECT

            rooms.id AS room_id,

            rooms.class_name,

            rooms.room_number,

            rooms.teacher,

            COALESCE(
                SUM(scores.points),
                0
            ) AS total_score

        FROM rooms

        LEFT JOIN scores

        ON rooms.id = scores.room_id

        AND scores.competition_id = ?

        GROUP BY rooms.id

        ORDER BY total_score DESC
        """,
        (competition_id,)
    )

    result = [
        dict(row)
        for row in cursor.fetchall()
    ]

    connection.close()

    for index, item in enumerate(result):

        item["rank"] = index + 1

    return result


# =========================================================
# 🌐 FRONTEND
# =========================================================

BASE_DIR = Path(__file__).resolve().parent

FRONTEND_DIR = BASE_DIR.parent / "frontend"


if FRONTEND_DIR.exists():

    app.mount(
        "/app",
        StaticFiles(
            directory=str(FRONTEND_DIR),
            html=True
        ),
        name="frontend"
    )