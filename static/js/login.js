import {postRequest} from "./requests.js"

const LoginForm = document.getElementById('login-form');

LoginForm.addEventListener('submit', async (event)=> {
    event.preventDefault();
    const phone_number = document.getElementById('phone-number-input').value;
    const password = document.getElementById('password-input').value;

    const payload = {
        "username": phone_number,
        "password": password
    }

    const login_end_point = "/auth/login";
    const response = await postRequest(login_end_point, payload);
    
    const message = response?.detail ?? null

    if (message !== null) {
        alert(message);
        return
    }

    const access_token = response?.access_token ?? null;
    const token_type = response?.token_type ?? null;

    if (access_token !== null && token_type !== null) {
        localStorage.setItem('access_token', response.access_token);
        localStorage.setItem('token_type', response.token_type);
        localStorage.setItem('user_id', phone_number);
        const home_url = window.location.origin;
        window.location.href = home_url;
        return
    }
    else {
        console.log(response);
    }

})