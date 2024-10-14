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
                    let userInputs = getUserInputs();
                    addUser(userInputs);
                }
                form.classList.add('was-validated')
            }, false)
        })
})()


// Валидация на подтверждение пароля
document.getElementById('confirmPassword').addEventListener('input', function () {
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    if (password !== confirmPassword) {
        document.getElementById('confirmPassword').setCustomValidity('Пароли должны совпадать');
    } else {
        document.getElementById('confirmPassword').setCustomValidity('');
    }
});


// Валиция логина
document.getElementById('login').addEventListener('input', function () {
    const login = document.getElementById('login').value;
    const loginPattern = /^[a-zA-Z0-9]{3,}$/; // Не менее 3 символов, только буквы и цифры
    if (!loginPattern.test(login)) {
        document.getElementById('login').setCustomValidity('Логин должен быть не менее 3 символов и содержать только буквы и цифры');
    } else {
        document.getElementById('login').setCustomValidity('');
    }
});
 
 
// Получаем данные из формы
function getUserInputs() {
    const userInputs = {
        name: document.getElementById('name').value.trim(),
        login: document.getElementById('login').value.trim(),
        password: document.getElementById('password').value.trim(),
    }
    return userInputs;
}


// Добавить пользователя
async function addUser(userInputs) {
    const newUser = {
        name: userInputs.name,
        login: userInputs.login,
        password: userInputs.password
    };
    
    try {
        let response = await fetch(`/users/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(newUser)
        });

        if (response.ok) {
            document.getElementById('registration_form').reset();
            window.location.href = '/';
        } else {
            let errorData = await response.json();
            alert(errorData.error || 'Произошла ошибка при регистрации. Попробуйте еще раз.');
        }
    } catch (error) {
        console.error('Ошибка:', error);
        alert('Произошла ошибка при регистрации. Попробуйте еще раз.');
    }
}