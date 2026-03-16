import { postRequest } from "./requests.js";

const RegisterForm = document.getElementById('register-form');
RegisterForm.addEventListener('submit', async (event) => {
    event.preventDefault();

    const name = document.getElementById('full-name-input').value;
    const phone_number = document.getElementById('phone_number-input').value;
    const password = document.getElementById('password-input').value;
    const confirm_password = document.getElementById('confirm-password-input').value;

    if (confirm_password !== password) {
        alert('Both Password Fields are Miss match, Recheck the Password and Recreate the User');
        return
    }

    const payload = {
        "name": name,
        "phone_number": phone_number,
        "password": password
    }

    const register_end_point = "/auth/register";
    const response = await postRequest(register_end_point, payload);
    console.log(response);
    
    const success_message = response?.message ?? null
    const detail = response?.detail ?? null

    if (detail !== null) {
        alert(detail)
        return
    }

    else if (success_message !== null) {
        alert(success_message);
        const home_url = document.location.origin
        window.location.href = home_url;
        return
    }
})