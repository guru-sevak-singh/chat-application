import { access_token, token_type } from "./login_required.js";
import { postRequest, secureGetRequest, logoutUser } from "./requests.js";
import { SendMessage, SOCKET, getTime } from "./socket.js";

const contactsDiv = document.getElementById("contacts")
const messages = document.getElementById("messages")
const chatName = document.getElementById("chatName")
const chatAvatar = document.getElementById("chatAvatar")

const contactsPanel = document.querySelector(".contacts")
const chatPanel = document.getElementById("chat")

var CONTACT_USER;
var ALL_CONTACTS

const checkRomPresent = (room_id) => {

}

async function getAllUsers() {
    const api_endpoint = `/rooms/`

    const response = await secureGetRequest(api_endpoint, token_type, access_token);

    if (Array.isArray(response)) {
        console.log(response);
        renderChats(response);
        return
    }

    const detail = response?.detail ?? null

    if (detail === 'Unauthorised Access') {
        logoutUser();
    }
}

window.onload = async () => {
    await getAllUsers();
}

function renderChats(contacts) {
    ALL_CONTACTS = contacts;
    contactsDiv.innerHTML = "";

    contacts.forEach(c => {

        let div = document.createElement("div")
        div.className = "contact"

        const complete_name = c['name'];
        const first_letter = complete_name[0];

        div.innerHTML = `
        <div class="avatar">
            ${first_letter}
        </div>
        <span>
            ${complete_name}
        </span>
        `
        div.onclick = () => OpenChat(c);
        contactsDiv.appendChild(div);
    });
}

function OpenChat(user) {
    CONTACT_USER = user;

    chatName.textContent = user.name;
    chatAvatar.textContent = user.name[0]

    messages.innerHTML = ""

    /* mobile switch */

    if (window.innerWidth <= 768) {
        contactsPanel.classList.add("hide");
        chatPanel.classList.add("active");
    }
}

function backToContacts() {
    contactsPanel.classList.remove("hide");
    chatPanel.classList.remove("active");
}

const backBtn = document.getElementById('back-btn')
backBtn.addEventListener('click', () => {
    backToContacts()
})

function openPopup() {
    document.getElementById("newUserName").value = "";
    document.getElementById("popup").style.display = "flex";
}

const popupBtn = document.getElementById('open-popup-btn');
popupBtn.addEventListener('click', () => {
    openPopup();
})

function closePopup() {
    document.getElementById("popup").style.display = "none";
}

function addUser() {
    let phone_number = document.getElementById("newUserName").ariaValueMax.trim();
    ALL_CONTACTS.foreach(contact => {
        if (contact.phone_number === phone_number) {
            alert("This user is Already Exist in Your Contacts");
        }
    })
    closePopup();
}

const addUserBtn = document.getElementById('add-user-btn');
addUserBtn.addEventListener('click', () => {
    addUser();
})

const closePopupBtn = document.getElementById('close-popup');
closePopupBtn.addEventListener('click', () => {
    closePopup();
})

function send_message() {
    const input = document.getElementById('msgInput');
    const text = input.value.trim();

    if (!text) return;

    let wrapper = document.createElement("div");
    wrapper.className = "message-wrapper sent";

    wrapper.innerHTML = `
        <div class="message">${text}</div>
        <div class="timestamp">${getTime()}</div>
    `
    messages.appendChild(wrapper);
    messages.scrollTop = messages.scrollHeight;
    input.value = "";

    const websocket_broadcast_data = { "message": text, "room_id": CONTACT_USER.id }
    SendMessage(websocket_broadcast_data);

}

const SendMsgBtn = document.getElementById('send-message-btn')
SendMsgBtn.addEventListener('click', () => {
    send_message();
})

SOCKET.onmessage = (e) => {
    console.log('event =>', e);
    const msgData = JSON.parse(e.data);
    console.log(msgData);
    const room_id = msgData.room_id;

    const idExists = ALL_CONTACTS.some(contact => contact.id === room_id)

    if (idExists) {
        // have to show message
        if (CONTACT_USER.id == room_id) {
            let wrapper = document.createElement("div");
            wrapper.className = "message-wrapper";

            wrapper.innerHTML = `
                <div class="received">${msgData.message}</div>
                <div class="timestamp">${getTime()}</div>
            `
            messages.appendChild(wrapper);
            messages.scrollTop = messages.scrollHeight;
            input.value = "";

        }
    }
}

export { CONTACT_USER, ALL_CONTACTS }