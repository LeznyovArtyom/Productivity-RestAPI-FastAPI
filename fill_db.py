from database import get_session
from models import Importance, Status, Role

def fill_data():
    session = next(get_session())

    # Заполнение таблицы "Importance"
    importances = [
        Importance(name="Критическая"),
        Importance(name="Высокая"),
        Importance(name="Средняя"),
        Importance(name="Низкая"),
        Importance(name="Очень низкая"),
    ]
    session.add_all(importances)

    # Заполнение таблицы "Status"
    statuses = [
        Status(name="Открытая"),
        Status(name="В процессе"),
        Status(name="Выполнено"),
        Status(name="Удалено"),
    ]
    session.add_all(statuses)

    # Заполнение таблицы "Role"
    roles = [
        Role(name="Пользователь"),
        Role(name="Веб-разработчик"),
        Role(name="Дизайнер"),
        Role(name="Архитектор"),
        Role(name="Фотограф"),
        Role(name="Администратор"),
        Role(name="Проектный менеджер"),
        Role(name="Контент-менеджер"),
        Role(name="Тестировщик"),
        Role(name="Аналитик"),
        Role(name="SEO-специалист"),
        Role(name="Маркетолог"),
        Role(name="Системный администратор"),
        Role(name="Редактор"),
        Role(name="Копирайтер"),
    ]
    session.add_all(roles)

    session.commit()
    session.close()


if __name__ == "__main__":
    fill_data()
