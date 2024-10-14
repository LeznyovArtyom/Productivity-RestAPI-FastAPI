// При загрузке страницы
document.addEventListener('DOMContentLoaded', function () {
    // Получаем информацию о пользователе из базы данных
    getUser();
    // Отображаем текущую дату
    displayCurrentDate();
    // Получаем информацию о задаче
    getTask()

    // Добавляем обработчик для кнопки сохранения изменений
    document.getElementById('saveTaskButton').addEventListener('click', saveTask);
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
        if (response.status === 403) {
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


// Получение информации о задаче
function getTask() {
    const accessToken = getCookie('access_token');
    // Получение значения идентификатора из URL
    let urlParams = new URLSearchParams(window.location.search);
    let task_id = urlParams.get('id');

    // Отправляем AJAX запрос к API
    fetch(`/tasks/${task_id}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${accessToken}`
        }
    })
    .then(response => {
        if (response.status === 403) {
            window.location.href = "/";
        }
        return response.json()
    })
    .then(data => {
        displayTaskDetails(data.Task);
    })
    .catch(error => console.error('Ошибка при получении данных:', error));
}


// Отобразить информацию о задаче
function displayTaskDetails(task) {
    document.getElementById("task_name").value = task.name;
    document.getElementById("importance_value").value = task.importance_id;
    document.getElementById("status_value").value = task.status_id;
    document.getElementById("deadline_value").value = task.deadline.split('T')[0];

    let importanceImage = {
        "Критическая": "/images/critical_importance.png", 
        "Высокая": "/images/high_importance.png",
        "Средняя": "/images/medium_importance.jpg",
        "Низкая": "/images/low_importance.png", 
        "Очень низкая": "/images/very_low_importance.jpg"
    };
    let statusColor = {
        "Открытая": "status-open",
        "В процессе": "status-in-progress",
        "Выполнено": "status-completed"
    };

    document.getElementById("importance_image").src = importanceImage[task.importance];
    document.getElementById("status_filling").classList.add(statusColor[task.status]);
    document.getElementById("task_description").value = task.description;
}


// Сохранение изменений задачи
function saveTask() {
    const accessToken = getCookie('access_token');
    let urlParams = new URLSearchParams(window.location.search);
    let task_id = urlParams.get('id');

    const task_name = document.getElementById('task_name').value;
    const task_description = document.getElementById('task_description').value;
    const task_importance_id = document.getElementById('importance_value').value;
    const task_status_id = document.getElementById('status_value').value;
    const task_deadline = document.getElementById('deadline_value').value;

    const updatedTask = {
        name: task_name,
        description: task_description,
        importance_id: task_importance_id,
        status_id: task_status_id,
        deadline: task_deadline
    };

    fetch(`/tasks/${task_id}/update`, {
        method: 'PUT',
        body: JSON.stringify(updatedTask),
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${accessToken}`
        }
    })
    .then(response => {
        if (response.status === 403) {
            window.location.href = "/";
        }
        if (response.ok) {
            window.location.reload();
        } else {
            throw new Error('Ошибка при обновлении задачи');
        }
    })
    .catch(error => {
        console.error('Ошибка при обновлении задачи:', error);
    });
}


// Функция форматирования даты
function formatDate(dateString) {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('ru-RU', options).format(date);
}


// Перемещение задачи в корзину
document.getElementById('deleteButton').addEventListener('click', function() {
    const accessToken = getCookie('access_token');
    let urlParams = new URLSearchParams(window.location.search);
    let task_id = urlParams.get('id');

    fetch(`/tasks/${task_id}/update`, {
        method: 'PUT',
        body: JSON.stringify({'status_id': 4}),
        headers: {
            'Authorization': `Bearer ${accessToken}`
        }
    })
    .then(response => {
        if (response.status === 403) {
            window.location.href = "/";
        }
        window.location.href = '/my_tasks';
    })
    .catch(error => {
        console.error('Ошибка при удалении задачи:', error);
    })
});


// Функция получения куки
const getCookie = (name) => {
    let matches = document.cookie.match(new RegExp(
        "(?:^|; )" + name.replace(/([\.$?*|{}\(\)\[\]\\\/\+^])/g, '\\$1') + "=([^;]*)"
    ));
    return matches ? decodeURIComponent(matches[1]) : undefined;
}