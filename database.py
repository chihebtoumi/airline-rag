import sqlite3

connection = sqlite3.connect("airline.db")
cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS flights (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    flight_number TEXT UNIQUE,
    departure TEXT,
    destination TEXT,
    date TEXT,
    departure_time TEXT,
    arrival_time TEXT,
    status TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS bookings (
    confirmation INTEGER PRIMARY KEY,
    first_name TEXT,
    last_name TEXT,
    flight_number TEXT
)
""")

cursor.executemany("""
INSERT OR IGNORE INTO flights
    (flight_number, departure, destination, date, departure_time, arrival_time, status)
VALUES (?, ?, ?, ?, ?, ?, ?)
""", [
    ("TU701", "Tunis", "Paris", "2026-11-15", "09:30 AM", "12:30 PM", "On Time"),
    ("TU702", "Tunis", "London", "2026-11-16", "02:15 PM", "04:45 PM", "Delayed"),
    ("AF123", "Paris", "New York", "2026-11-17", "11:00 AM", "01:30 PM", "On Time"),
    ("TU703", "Tunis", "Rome", "2026-11-18", "06:45 PM", "08:30 PM", "Cancelled"),
    ("AF456", "London", "Paris", "2026-11-19", "08:00 AM", "10:20 AM", "On Time"),
])

cursor.executemany("""
INSERT OR IGNORE INTO bookings (confirmation, first_name, last_name, flight_number)
VALUES (?, ?, ?, ?)
""", [
    (12345, "Jane", "Doe", "TU701"),
    (54321, "John", "Smith", "TU702"),
    (98765, "Alice", "Johnson", "AF123"),
    (56789, "Bob", "Brown", "TU703"),
    (11111, "Chiheb", "Toumi", "TU701"),
])

connection.commit()
connection.close()
print("Database ready!")