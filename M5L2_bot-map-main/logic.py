import sqlite3
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import requests
from datetime import datetime
import pytz
from config import DATABASE, WEATHER_API_KEY


class DB_Map:
    def __init__(self, database):
        self.database = database

    # ---------- ТАБЛИЦЫ ----------
    def create_tables(self):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users_cities (
                    user_id INTEGER,
                    city_id TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users_settings (
                    user_id INTEGER PRIMARY KEY,
                    color TEXT
                )
            """)
            conn.commit()

    # ---------- НАСТРОЙКИ ----------
    def set_color(self, user_id, color):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute(
                "INSERT OR REPLACE INTO users_settings VALUES (?, ?)",
                (user_id, color)
            )
            conn.commit()

    def get_color(self, user_id):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT color FROM users_settings WHERE user_id=?",
                (user_id,)
            )
            res = cur.fetchone()
            return res[0] if res else "red"

    # ---------- ГОРОДА ----------
    def get_coordinates(self, city):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT lat, lng FROM cities WHERE city=?",
                (city,)
            )
            return cur.fetchone()

    def get_cities_by_country(self, country):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT city FROM cities WHERE country=?",
                (country,)
            )
            return [row[0] for row in cur.fetchall()]

    def get_cities_by_population(self, population):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT city FROM cities WHERE population >= ?",
                (population,)
            )
            return [row[0] for row in cur.fetchall()]

    def get_cities_by_country_population(self, country, population):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT city FROM cities
                WHERE country=? AND population>=?
                """,
                (country, population)
            )
            return [row[0] for row in cur.fetchall()]

    # ---------- КАРТА ----------
    def create_graph(self, path, cities, color="red"):
        fig = plt.figure(figsize=(13, 7))
        ax = plt.axes(projection=ccrs.PlateCarree())

        ax.add_feature(cfeature.OCEAN, facecolor="#a6cee3")
        ax.add_feature(cfeature.LAND, facecolor="#b2df8a")
        ax.add_feature(cfeature.COASTLINE)
        ax.add_feature(cfeature.BORDERS, linestyle=":")
        ax.add_feature(cfeature.RIVERS)

        ax.set_global()
        ax.gridlines(draw_labels=True)

        for city in cities:
            coords = self.get_coordinates(city)
            if coords:
                lat, lng = coords
                ax.plot(lng, lat, "o", color=color, markersize=7)
                ax.text(lng + 1, lat + 1, city, fontsize=9)

        plt.savefig(path)
        plt.close()

    # ---------- ПОГОДА ----------
    def get_weather(self, city):
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": city,
            "appid": WEATHER_API_KEY,
            "units": "metric",
            "lang": "ru"
        }
        r = requests.get(url, params=params).json()

        if "main" in r:
            temp = r["main"]["temp"]
            desc = r["weather"][0]["description"]
            return f"{temp}°C, {desc}"
        return "Нет данных"

    # ---------- ВРЕМЯ ----------
    def get_time(self, timezone):
        tz = pytz.timezone(timezone)
        return datetime.now(tz).strftime("%H:%M:%S")
