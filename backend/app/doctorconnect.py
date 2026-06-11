import geocoder
from math import radians, sin, cos, sqrt, atan2
from backend.app.database import get_connection


def user_location():
    g = geocoder.ip('me')
    return g.latlng


def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0  # Earth radius in KM

    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c


def find_nearest_doctors(user_lat, user_lon, specialty=None):
    conn = get_connection("DoctorDB")
    try:
        cursor = conn.cursor()
        try:
            if specialty:
                query = """
                    SELECT name, specialty, latitude, longitude, phone_number
                    FROM doctors
                    WHERE specialty = %s
                """
                cursor.execute(query, (specialty,))
            else:
                query = """
                    SELECT name, specialty, latitude, longitude, phone_number
                    FROM doctors
                """
                cursor.execute(query)

            doctors = cursor.fetchall()
        finally:
            cursor.close()
    finally:
        conn.close()

    nearest_doctors = []

    for name, specialty, lat, lon, phone in doctors:
        distance = haversine(user_lat, user_lon, lat, lon)
        nearest_doctors.append((name, specialty, phone, distance))

    nearest_doctors.sort(key=lambda x: x[3])

    return nearest_doctors[:5]
