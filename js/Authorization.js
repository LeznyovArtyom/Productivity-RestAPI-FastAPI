// Example starter JavaScript for disabling form submissions if there are invalid fields
(function () {
    'use strict'
    // Fetch all the forms we want to apply custom Bootstrap validation styles to
    var forms = document.querySelectorAll('.needs-validation')

    // Loop over them and prevent submission
    Array.prototype.slice.call(forms)
        .forEach(function (form) {
            form.addEventListener('submit', function (event) {
                event.preventDefault()
                if (!form.checkValidity()) {
                    event.stopPropagation()
                } else {
                    let login_value = document.getElementById('login').value.trim();
                    let password_value = document.getElementById('password').value.trim();
                    authenticateUser(login_value, password_value);
                }
                form.classList.add('was-validated')
            }, false)
        })
})()


// Авторизировать пользователя
const authenticateUser = async (login_value, password_value) => {
    try {
        let response = await fetch(`/users/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                'login': login_value,
                'password': password_value
            })
        });

        if (response.ok) {
            let data = await response.json();
            setCookie('access_token', data.access_token); // Сохранение токена доступа авторизации в куки
            window.location.href = "/my_tasks";
        } else {
            let errorData = await response.json();
            alert(errorData.error || 'Произошла ошибка при авторизации. Попробуйте еще раз.');
        }
    } catch (error) {
        console.error('Ошибка:', error);
        alert('Произошла ошибка при авторизации. Попробуйте еще раз.');
    }
}


// Функция установки куки
const setCookie = (name, value, options = {}) => {
    options = {
        path: '/',
        ...options
    };

    if (options.expires instanceof Date) {
        options.expires = options.expires.toUTCString();
    }

    let updatedCookie = encodeURIComponent(name) + "=" + encodeURIComponent(value);

    for (let optionKey in options) {
        updatedCookie += "; " + optionKey;
        let optionValue = options[optionKey];
        if (optionValue !== true) {
            updatedCookie += "=" + optionValue;
        }
    }

    document.cookie = updatedCookie;
}


// Функция получения куки
const getCookie = (name) => {
    let matches = document.cookie.match(new RegExp(
        "(?:^|; )" + name.replace(/([\.$?*|{}\(\)\[\]\\\/\+^])/g, '\\$1') + "=([^;]*)"
    ));
    return matches ? decodeURIComponent(matches[1]) : undefined;
}