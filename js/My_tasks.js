// При загрузке страницы
document.addEventListener('DOMContentLoaded', function () {
    const accessToken = getCookie('access_token');

    if (!accessToken) {
        window.location.href = "/";
    }

    // Получаем задачи из базы данных
    getTasks();
    // Получаем информацию о пользователе из базы данных
    getUser();
    // Отображаем текущую дату
    displayCurrentDate();

    // Добавляем обработчики для элементов сортировки и фильтрации
    document.getElementById('priority_select').addEventListener('change', applySortAndFilter);
    document.getElementById('deadline_select').addEventListener('change', applySortAndFilter);
    document.getElementById('importance_select').addEventListener('change', applySortAndFilter);
    document.getElementById('status_select').addEventListener('change', applySortAndFilter);
});


let tasksData = []
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
        if (response.status === 401) {
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
    let statusColor = {
        "Открытая": "status-open",
        "В процессе": "status-in-progress",
        "Выполнено": "status-completed"
    };

    tasks.forEach(function (task) {
        if (task.status !== "Удалено") {    
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
                    <div class="task_status_container d-flex justify-content-end"><div class="task_status text-white text-center py-2 px-4 ${statusColor[task.status]}">${task.status}</div></div>
                </div>
            `;
            tasksContainer.appendChild(taskElement);
        }
    });
}


// Функция для обрезки строки и добавления троеточия, если длина строки больше 70 символов
function truncateString(str, num) {
    return str.length > num ? str.slice(0, num) + "..." : str;
}


// Функция для применения сортировки и фильтрации
function applySortAndFilter() {
    let filteredTasks = tasksData.slice();

    // Фильтрация по важности
    const importanceFilter = document.getElementById('importance_select').value;
    if (importanceFilter !== 'default') {
        filteredTasks = filteredTasks.filter(task => task.importance_id == importanceFilter);
    }

    // Фильтрация по статусу
    const statusFilter = document.getElementById('status_select').value;
    if (statusFilter !== 'default') {
        filteredTasks = filteredTasks.filter(task => task.status === statusFilter);
    }

    // Сортировка по приоритету
    const prioritySort = document.getElementById('priority_select').value;
    if (prioritySort === 'highest') {
        filteredTasks.sort((a, b) => a.importance_id - b.importance_id);
    } else if (prioritySort === 'lowest') {
        filteredTasks.sort((a, b) => b.importance_id - a.importance_id);
    }

    // Сортировка по дедлайну
    const deadlineSort = document.getElementById('deadline_select').value;
    if (deadlineSort === 'soonest') {
        filteredTasks.sort((a, b) => new Date(a.deadline) - new Date(b.deadline));
    } else if (deadlineSort === 'latest') {
        filteredTasks.sort((a, b) => new Date(b.deadline) - new Date(a.deadline));
    }

    // Отображаем задачи с примененной сортировкой и фильтрацией
    displayTasks(filteredTasks);
}


// Функция форматирования даты
function formatDate(dateString) {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('ru-RU', options).format(date);
}


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


// Функция получения куки
const getCookie = (name) => {
    let matches = document.cookie.match(new RegExp(
        "(?:^|; )" + name.replace(/([\.$?*|{}\(\)\[\]\\\/\+^])/g, '\\$1') + "=([^;]*)"
    ));
    return matches ? decodeURIComponent(matches[1]) : undefined;
}