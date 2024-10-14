// При загрузке страницы
document.addEventListener('DOMContentLoaded', function () {
    // Получаем роли и информацию о пользователе из базы данных
    loadUserAndRoles()
    // Отображаем текущую дату
    displayCurrentDate();
});


// Получение информации о пользователе и списка ролей
function loadUserAndRoles() {
    const accessToken = getCookie('access_token');
    
    // Получаем информацию о пользователе
    const userRequest = fetch(`/users/me`, {
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
    });

    // Получаем список ролей
    const rolesRequest = fetch(`/roles`, {
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
    });

    // Ожидаем завершения обоих запросов
    Promise.all([userRequest, rolesRequest])
        .then(([userData, rolesData]) => {
            populateRoles(rolesData.Roles);
            displayUserInfo(userData.User);
        })
        .catch(error => console.error('Ошибка при загрузке данных:', error));
}


// Заполнение выпадающего списка ролей
function populateRoles(roles) {
    const roleSelect = document.getElementById('role_select');

    roles.forEach(role => {
        const option = document.createElement('option');
        option.value = role.id;
        option.textContent = role.name;
        roleSelect.appendChild(option);
    });
}


// Отображение данных о текущем пользователе
function displayUserInfo(user) {
    const userImage = document.getElementById('user_image');
    const userName = document.getElementById('user_name');
    const userRole = document.getElementById('user_role');

    userImage.src = "data:image/jpeg;base64," + user.image;
    userName.innerText = user.name;
    userRole.innerText = user.role;

    document.getElementById('text_name').placeholder = user.name;
    document.getElementById('text_login').placeholder = user.login;
    document.getElementById('role_select').value = user.role_id;
    document.getElementById('profile_image').src = "data:image/jpeg;base64," + user.image;
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


// Валидация логина
function validateLogin(login) {
    const regex = /^[a-zA-Z0-9]{3,}$/;
    return regex.test(login);
}

// Валидация пароля
function validatePassword(password) {
    return password.length >= 6;
}


// Изменение информации о пользователе
document.getElementById('changeName').addEventListener('click', async e => {
    e.preventDefault();
    await updateUser('name', document.getElementById('text_name').value);
});
document.getElementById('changeLogin').addEventListener('click', async e => {
    e.preventDefault();
    const loginInput = document.getElementById('text_login');
    if (validateLogin(loginInput.value)) {
        await updateUser('login', loginInput.value);
        loginInput.classList.remove('is-invalid');
    } else {
        loginInput.classList.add('is-invalid');
    }
});
document.getElementById('changePassword').addEventListener('click', async e => {
    e.preventDefault();
    const passwordInput = document.getElementById('text_password');
    if (validatePassword(passwordInput.value)) {
        await updateUser('password', passwordInput.value);
        passwordInput.classList.remove('is-invalid');
    } else {
        passwordInput.classList.add('is-invalid');
    }
});
document.getElementById('changeRole').addEventListener('click', async e => {
    e.preventDefault();
    await updateUser('role_id', document.getElementById('role_select').value);
});
document.getElementById('changeImage').addEventListener('click', async e => {
    e.preventDefault();
    const account_image = document.getElementById('account_image');
    const reader = new FileReader();
    reader.readAsDataURL(account_image.files[0]);
    reader.onload = async function() {
        await updateUser('image', reader.result.split(',')[1]);
    };
});


// Загрузить изображение, чтобы отобразить в предпросмотре при обновлении изображения пользователя
function download(input) {
    let file = input.files[0];
    let reader = new FileReader();
    reader.readAsDataURL(file);

    reader.onload = function() {
        let img = document.getElementById("profile_image");
        img.src = reader.result;

    }
}


// Обновить информацию о пользователе
async function updateUser(field, value) {
    const accessToken = getCookie('access_token');

    fetch(`/users/me/update`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${accessToken}`
        },
        body: JSON.stringify({[field]: value})
    })
    .then(response => {
        if (response.status === 403) {
            window.location.href = "/";
        }
        alert('Данные успешно обновлены');
        window.location.reload();
    })
    .catch(error => {
        console.error('Ошибка при обновлении данных пользователя:', error);
    })
}


// Удалить аккаунт
document.getElementById('deleteButton').addEventListener('click', function() {
    const accessToken = getCookie('access_token');
    fetch(`/users/me/delete`, {
        method: 'DELETE',
        headers: {
            'Authorization': `Bearer ${accessToken}`
        }
    })
    .then(response => {
        if (response.status === 403) {
            window.location.href = "/";
        }
        deleteCookie('access_token'); // Удаляем куки с токеном доступа
        window.location.href = '/';
    })
    .catch(error => {
        console.error('Ошибка при удалении аккаунта:', error);
    })
});


// Выход из аккаунта
document.getElementById('go_out_button').addEventListener('click', function() {
    deleteCookie('access_token'); // Удаляем куки с токеном доступа
    window.location.href = '/';
});


// Функция получения куки
const getCookie = (name) => {
    let matches = document.cookie.match(new RegExp(
        "(?:^|; )" + name.replace(/([\.$?*|{}\(\)\[\]\\\/\+^])/g, '\\$1') + "=([^;]*)"
    ));
    return matches ? decodeURIComponent(matches[1]) : undefined;
}


// Функция удаления куки
const deleteCookie = (name) => {
    document.cookie = name + '=; Max-Age=-99999999; path=/';
}