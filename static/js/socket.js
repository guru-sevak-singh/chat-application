const getSocketUrl = () => {
    const access_token = localStorage.getItem('access_token');
    const token_type = localStorage.getItem('token_type');

    let SOCKET_URL = `${window.location.host}/ws/?token=${token_type} ${access_token}`
    if (window.location.href.includes('https://')) {
        SOCKET_URL = "wss://" + SOCKET_URL
    }
    else {
        SOCKET_URL = "ws://" + SOCKET_URL
    }
    return SOCKET_URL
}

var SOCKET;

function ConnectWebSocket() {
    const socket_url = getSocketUrl();
    console.log(socket_url);
    SOCKET = new WebSocket(socket_url);

    SOCKET.onopen = (e) => {
        console.log('socket is connected and first function is executed after connection open....');
    }
    SOCKET.onclose = (e) => {
        console.error('Socket Disconnected');
        console.log('again connected to socket');
        // ConnectWebSocket();
    }
}

function SendMessage(data) {
    SOCKET.send(JSON.stringify(data))
}

function getTime() {
    const d = new Date()

    let h = d.getHours()
    let m = d.getMinutes()

    if (m < 10) m = "0" + m

    return `${h}:${m}`
}

ConnectWebSocket()
export { SendMessage, SOCKET, getTime }

