async function getRequest(end_point) {
    try {
        const response = await fetch(end_point)

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const data = await response.json()
        return data
    }
    catch (error) {
        console.error('error -> ', error);
    }
}

async function secureGetRequest(end_point, token_type, access_token) {
    try {
        const response = await fetch(end_point, {
            method: 'GET',
            headers: {
                'Authorization': `${token_type} ${access_token}`,
                'Content-Type': 'application/json'
            }
        })
        return await response.json()
    }

    catch (error) {
        console.log('error -> ', error);
    }
}

async function postRequest(end_point, data) {
    'Function send post request to the url with the data as payload'
    try {
        const response = await fetch(end_point, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })

        // if (response.ok) {
        //     return await response.json()
        // }
        return await response.json()
        // throw new Error(`Http Error ! Status : ${response.status}`)

    }
    catch (error) {
        console.error('error -> ', error)
    }
}

function logoutUser() {
    localStorage.clear();
    window.location.href = window.location.href
}

export { getRequest, postRequest, secureGetRequest, logoutUser }