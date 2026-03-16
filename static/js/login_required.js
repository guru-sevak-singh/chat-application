const access_token = localStorage.getItem('access_token');
const token_type = localStorage.getItem('token_type');

if (access_token === null && token_type === null) {
    localStorage.clear()
    window.location.href = `${window.location.origin}/login`
}

export {access_token, token_type}