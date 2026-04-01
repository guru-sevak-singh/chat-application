let socket = null;
let onlineUsers = [];
let currentCallerId = null;
let peerConnection = null;
let stream = null;

import { CONTACT_USER } from "../index.js";

const userId = localStorage.getItem("user_id");


function initializeWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/rtc/${userId}`;

    socket = new WebSocket(wsUrl);

    socket.onopen = () => {
        console.log("WebSocket connection established, ready for RTC communication");
    }

    socket.onmessage = async (event) => {
        const eventData = JSON.parse(event.data);
        const msg_type = eventData.type;

        switch (msg_type) {
            case "incoming-call":
                const callerId = eventData.from;
                document.getElementById('caller-id-text').innerText = eventData.from;
                document.getElementById('incoming-modal').setAttribute('class', 'show');
                break;

            case "call-error":
                alert(eventData.message);
                break;

            case "call-rejected":
                alert(`${eventData.from} rejected your call`);
                break;

            case "call-accepted":
                await setUpPeerConnection(eventData.from);
                const offer = await peerConnection.createOffer();
                await peerConnection.setLocalDescription(offer);

                socket.send(
                    JSON.stringify({
                        type: 'offer',
                        target: eventData.from,
                        sdp: offer
                    })
                )
                break;

            case "offer":
                await peerConnection.setRemoteDescription(
                    new RTCSessionDescription(eventData.sdp)
                )

                const answer = await peerConnection.createAnswer();
                await peerConnection.setLocalDescription(answer);
                socket.send(
                    JSON.stringify({
                        type: "answer",
                        target: eventData.from,
                        sdp: answer
                    })
                )
                break;

            case "answer":
                await peerConnection.setRemoteDescription(
                    new RTCSessionDescription(eventData.sdp)
                )
                break;

            case "ice-candidate":
                if (peerConnection) {
                    await peerConnection.addIceCandidate(
                        new RTCIceCandidate(eventData.candidate)
                    )
                }
                break;
        }
    }

    socket.onclose = (event) => {
        console.error("WebSocket connection closed", event);
    }
}

async function setUpPeerConnection(targetId) {
    if (stream === null) {
        stream = await navigator.mediaDevices.getUserMedia({
            audio: true
        })
    }
    peerConnection = new RTCPeerConnection({
        iceServers: [
            {
                urls: "stun:stun.l.google.com:19302"
            }
        ]
    });

    peerConnection.onicecandidate = (event) => {
        if (event.candidate) {
            socket.send(
                JSON.stringify({
                    type: 'ice-candidate',
                    target: targetId,
                    candidate: event.candidate
                })
            )
        }
    }

    peerConnection.ontrack = (event) => {
        const audio = new Audio();
        audio.srcObject = event.streams[0];
        audio.play();
    }

    stream.getTracks().forEach(track => {
        peerConnection.addTrack(track, stream);
    });
}

initializeWebSocket();


// audio call features
const callBtn = document.getElementById('call-btn');
callBtn.addEventListener('click', () => {
    if (!socket) {
        alert('You are disconnect from the server');
        return;
    }
    socket.send(
        JSON.stringify({
            "type": "call-request",
            "to": CONTACT_USER.phone_number
        })
    );
});

// reject call feature
const rejectCallBtn = document.getElementById('reject-call-btn');
rejectCallBtn.addEventListener('click', () => {
    if (!socket) {
        alert('You are disconnect from the server');
        return;
    }

    socket.send(
        JSON.stringify({
            "type": "call-reject",
            "phone_number": document.getElementById('caller-id-text').innerText
        })
    )
    document.getElementById('caller-id-text').innerText = '—';
    document.getElementById('incoming-modal').setAttribute('class', '');
    return;
})

// accept call feature
const acceptCallBtn = document.getElementById('accept-call-btn');
acceptCallBtn.addEventListener('click', async () => {
    const callerId = document.getElementById('caller-id-text').innerText;
    socket.send(
        JSON.stringify({
            type: "call-accept",
            target: callerId
        })
    )
    document.getElementById('incoming-modal').setAttribute('class', '');
    await setUpPeerConnection(callerId);
    return;
})

// video call features
const videoCallBtn = document.getElementById('video-call-btn');
videoCallBtn.addEventListener('click', () => {
    alert('Video call feature coming soon!');
});