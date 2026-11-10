import sqlite3
from contextlib import closing
from pathlib import Path

DB_PATH = Path(__file__).parent / "airline.db"

def get_flight_info(d: dict) -> str:
    req_keys = ["first_name", "last_name", "confirmation"]
    assert all(k in d for k in req_keys), f"Expected keys {req_keys}, got {d}"

    with closing(sqlite3.connect(DB_PATH)) as conn:
        row = conn.execute("""
            SELECT b.first_name, b.last_name, f.flight_number,
                   f.departure, f.destination, f.date,
                   f.departure_time, f.arrival_time, f.status
            FROM bookings b
            JOIN flights f ON f.flight_number = b.flight_number
            WHERE b.confirmation = ?
              AND LOWER(b.first_name) = LOWER(?)
              AND LOWER(b.last_name) = LOWER(?)
        """, (d["confirmation"], d["first_name"], d["last_name"])).fetchone()

    if row is None:
        return (
            f"No booking found for {d['first_name']} {d['last_name']} "
            f"with confirmation {d['confirmation']}. "
            "If it matters, ask the user to confirm their first name, last name and confirmation number."
        )

    first, last, number, dep, dest, date, dep_time, arr_time, status = row
    return (
        f"{first} {last}'s flight {number} from {dep} to {dest} "
        f"departs at {dep_time} on {date} and lands at {arr_time} (local time). "
        f"Current status: {status}."
    )