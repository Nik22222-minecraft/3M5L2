import sqlite3
from config import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature


class DB_Map():
    def __init__(self, database):
        self.database = database

    def create_user_table(self):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS users_cities (
                    user_id INTEGER,
                    city_id TEXT
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS users_settings (
                    user_id INTEGER PRIMARY KEY,
                    color TEXT
                )
            ''')
            conn.commit()

    # ---------- НАСТРОЙКИ ПОЛЬЗОВАТЕЛЯ ----------
    def set_color(self, user_id, color):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute('''
                INSERT OR REPLACE INTO users_settings
                VALUES (?, ?)
            ''', (user_id, color))
            conn.commit()

    def get_color(self, user_id):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT color FROM users_settings WHERE user_id=?",
                (user_id,)
            )
            res = cursor.fetchone()
            return res[0] if res else "red"

    # ---------- ГОРОДА ----------
    def get_coordinates(self, city_name):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT lat, lng FROM cities WHERE city=?",
                (city_name,)
            )
            return cursor.fetchone()

    def create_graph(self, path, cities, color="red"):
        fig = plt.figure(figsize=(13, 7))
        ax = plt.axes(projection=ccrs.PlateCarree())

        # 🌍 ЗАЛИВКА КОНТИНЕНТОВ И ОКЕАНОВ
        ax.add_feature(cfeature.OCEAN, facecolor="#a6cee3")
        ax.add_feature(cfeature.LAND, facecolor="#b2df8a")
        ax.add_feature(cfeature.COASTLINE)
        ax.add_feature(cfeature.BORDERS, linestyle=':')
        ax.add_feature(cfeature.RIVERS)

        ax.set_global()
        ax.gridlines(draw_labels=True)

        # 📍 ГОРОДА
        for city in cities:
            coords = self.get_coordinates(city)
            if coords:
                lat, lng = coords
                ax.plot(
                    lng, lat,
                    marker="o",
                    color=color,
                    markersize=7,
                    transform=ccrs.PlateCarree()
                )
                ax.text(
                    lng + 1,
                    lat + 1,
                    city,
                    fontsize=9
                )

        plt.savefig(path)
        plt.close()
