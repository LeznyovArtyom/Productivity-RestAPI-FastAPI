// При загрузке страницы
document.addEventListener('DOMContentLoaded', function () {
    // Получаем информацию о пользователе из базы данных
    getUser();
    // Отображаем текущую дату
    displayCurrentDate();
    // Получаем задачи из базы данных
    getTasks()
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


// Получаем задачи из базы данных
function getTasks() {  
    const accessToken = getCookie('access_token');
    
    // Отправляем AJAX запрос к API
    fetch(`/users/me/tasks`, {
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
        tasksData = data.Tasks;
        displayTasks(tasksData);
    })
    .catch(error => console.error('Ошибка при получении данных:', error));
}


// Отображаем задачи
function displayTasks(tasks) {
    // Очищаем контейнер перед добавлением новых задач
    var tasksContainer = document.getElementById('tasks_container');
    tasksContainer.innerHTML = '';

    let importanceImage = {
        "Критическая": "/images/critical_importance.png", 
        "Высокая": "/images/high_importance.png",
        "Средняя": "/images/medium_importance.jpg",
        "Низкая": "/images/low_importance.png", 
        "Очень низкая": "/images/very_low_importance.jpg"
    };

    tasks.forEach(function (task) {
        if (task.status === "Удалено") {
            let taskElement = document.createElement('a');
            taskElement.href = "/the_task?id=" + task.id;
            taskElement.innerHTML = `
                <div class="task w-100 d-flex align-items-center justify-content-between pe-5 ps-3 py-3 mb-4">
                    <div class="d-flex task_elems">
                        <img src="${importanceImage[task.importance]}" alt="Важность" class="importance" />
                        <div class=" d-flex flex-column justify-content-between my-2 ms-3">
                            <div class="task_name">${truncateString(task.name, 70)}</div>
                            <div class="task_deadline">${formatDate(task.deadline)}</div>
                        </div>
                    </div>
                    <div class="task_description py-2 px-4 w-100">${truncateString(task.description, 150)}</div>
                    <div class="task_buttons text-white d-flex justify-content-end">
                        <button type="button" class="btn text-white me-3 resume_button" data-task-id="${task.id}">Возобновить</button>
                        <button type="button" class="btn text-white in_complete_button" data-task-id="${task.id}">В завершенные</button>
                    </div>
                </div>
            `;
            tasksContainer.appendChild(taskElement);
        }
    });

    // Добавляем обработчики событий для кнопок
    document.querySelectorAll('.resume_button').forEach(button => {
        button.addEventListener('click', function() {
            updateTaskStatus(this.getAttribute('data-task-id'), 'Открытая');
        });
    });

    document.querySelectorAll('.in_complete_button').forEach(button => {
        button.addEventListener('click', function() {
            updateTaskStatus(this.getAttribute('data-task-id'), 'Выполнено');
        });
    });
}


// Функция для обрезки строки и добавления троеточия, если длина строки больше 70 символов
function truncateString(str, num) {
    return str.length > num ? str.slice(0, num) + "..." : str;
}


// Функция для обновления статуса задачи
function updateTaskStatus(taskId, status) {
    const accessToken = getCookie('access_token');
    let statusId;

    // Определение статус_id по статусу
    switch (status) {
        case 'Открытая':
            statusId = 1;
            break;
        case 'Выполнено':
            statusId = 3;
            break;
        default:
            return;
    }

    fetch(`/tasks/${taskId}/update`, {
        method: 'PUT',
        body: JSON.stringify({ 'status_id': statusId }),
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
            throw new Error('Ошибка при изменении статуса задачи');
        }
    })
    .catch(error => {
        console.error('Ошибка при изменении статуса задачи:', error);
    });
}


// Функция форматирования даты
function formatDate(dateString) {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('ru-RU', options).format(date);
}


// Функция получения куки
const getCookie = (name) => {
    let matches = document.cookie.match(new RegExp(
        "(?:^|; )" + name.replace(/([\.$?*|{}\(\)\[\]\\\/\+^])/g, '\\$1') + "=([^;]*)"
    ));
    return matches ? decodeURIComponent(matches[1]) : undefined;
}