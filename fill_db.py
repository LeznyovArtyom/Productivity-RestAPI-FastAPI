import mysql.connector
from config import data


connection = mysql.connector.connect(
    host=data["host"],
    port=data["port"],
    user=data["user"],
    password=data["password"],
    database=data["database"]
)


cursor = connection.cursor()


importances = [("Критическая",), ("Высокая",), ("Средняя",), ("Низкая",), ("Очень низкая",)]
cursor.executemany("INSERT INTO importance (name) VALUES (%s)", importances)

statuses = [("Открытая",), ("В процессе",), ("Выполнено",), ("Удалено",)]
cursor.executemany("INSERT INTO status (name) VALUES (%s)", statuses)

roles = [("Пользователь",), ("Веб-разработчик",), ("Дизайнер",), ("Архитектор",), ("Фотограф",), ("Администратор",), 
         ("Проектный менеджер",), ("Контент-менеджер",), ("Тестировщик",), ("Аналитик",), ("SEO-специалист",), 
         ("Маркетолог",), ("Системный администратор",), ("Редактор",), ("Копирайтер",)]
cursor.executemany("INSERT INTO role (name) VALUES (%s)", roles)


connection.commit()
cursor.close()
connection.close()