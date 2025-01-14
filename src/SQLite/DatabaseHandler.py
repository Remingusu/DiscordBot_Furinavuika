import sqlite3
from interactions import StringSelectOption


class DatabaseHandler:
    def __init__(self):
        self.conn = sqlite3.connect("database.db")

    def add_character(self, character, year, month, day, game, duration, user):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO CHD (name, release, game, duration, user) VALUES (?, ?, ?, ?, ?)",
                       (character, f"{year}/{month}/{day}", game, duration, user))
        self.conn.commit()
        cursor.close()

    def remove_character(self, character):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM CHD WHERE name = ?", (character,))
        self.conn.commit()
        cursor.close()

    def update_character(self, character, year, month, day, game, duration):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE CHD SET release = ?, game = ?, duration = ? WHERE name = ?",
                       (f"{year}/{month}/{day}", game, duration, character))
        self.conn.commit()
        cursor.close()

    def get_names(self):
        return [StringSelectOption(label=row[0], value=row[0])
                for row in self.conn.cursor().execute("SELECT name FROM CHD").fetchall()]

    def get_informations(self, character):
        return self.conn.cursor().execute("SELECT * FROM CHD WHERE name = ?", (character,)).fetchone()

    def get_user_list(self, user):
        return self.conn.cursor().execute("SELECT name FROM CHD WHERE user = ?", (user,)).fetchall()

    def get_list(self):
        return self.conn.cursor().execute("SELECT name FROM CHD").fetchall()
