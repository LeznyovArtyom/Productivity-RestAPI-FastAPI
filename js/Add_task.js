// При загрузке страницы
document.addEventListener('DOMContentLoaded', function () {
    // Получаем информацию о пользователе из базы данных
    getUser();
    // Отображаем текущую дату
    displayCurrentDate();
});


// Получение информации о пользователе
function getUser() {
    const accessToken = getCookie('access_token');
    
    // Отправляем AJAX запрос к API
    fetch(`/users/me`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${accessToken}`
        }
    })
    .then(response => {
        if (response.status === 401) {
            window.location.href = "/";
        }
        return response.json()
    })
    .then(data => {
        displayUserInfo(data.User);
    })
    .catch(error => console.error('Ошибка при получении данных:', error));
}


// Отображение данных о текущем пользователе
function displayUserInfo(user) {
    const userImage = document.getElementById('user_image');
    const userName = document.getElementById('user_name');
    const userRole = document.getElementById('user_role');

    userImage.src = "data:image/jpeg;base64," + user.image;
    userName.innerText = user.name;
    userRole.innerText = user.role;
}


// Функция для получения текущей даты и форматирования её в строку
function displayCurrentDate() {
    const currentDateElement = document.getElementById('current_date');
    const currentDate = new Date();

    // Опции для форматирования даты
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    const formattedDate = currentDate.toLocaleDateString('ru-RU', options);

    // Вставка форматированной даты в элемент
    currentDateElement.textContent = formattedDate;
}


// Добавить задачу
const form = document.getElementById('add_task_form');
form.addEventListener("submit", async e => {
    e.preventDefault();
    const accessToken = getCookie('access_token');

    // Получаем данные из формы добавления фильма
    const task_name = document.getElementById('task_name');
    const task_description = document.getElementById('task_description');
    const task_importance_id = document.getElementById('task_importance');
    const task_deadline = document.getElementById('task_deadline');

    // Подготавливаем данные
    const newTask = {
        name: task_name.value,
        description: task_description.value,
        importance_id: task_importance_id.value,
        deadline: task_deadline.value
    };

    // Отправляем данные на сервер
    fetch(`/users/me/tasks/add`, {
        method: 'POST',
        body: JSON.stringify(newTask),
        headers: {
            'Content-Type': 'application/json; charset=utf-8',
            'Authorization': `Bearer ${accessToken}`
        }
    })
    .then(response => {
        if (response.status === 401) {
            window.location.href = "/";
        }
        form.reset(); // Очищаем форму
        window.location.href = "/my_tasks";
    })
    .catch(error => {
        console.error('Ошибка при добавлении задачи:', error);
    });
});


// Функция получения куки
const getCookie = (name) => {
    let matches = document.cookie.match(new RegExp(
        "(?:^|; )" + name.replace(/([\.$?*|{}\(\)\[\]\\\/\+^])/g, '\\$1') + "=([^;]*)"
    ));
    return matches ? decodeURIComponent(matches[1]) : undefined;
}