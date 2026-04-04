let socket = null;
let peerConnection = null;
let stream = null;

import { CONTACT_USER } from "/static/js/index.js";


function initializeWebSocket() {
    const userId = localStorage.getItem("user_id");
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/video-call/${userId}`;
    socket = new WebSocket(wsUrl);

    socket.onopen = () => {
        console.log("websocket for video call is connected...");
    }

    socket.onmessage = async (event) => {
        const eventData = JSON.parse(event.data);
        const msg_type = eventData.type;

        switch (msg_type) {
            case "error":
                const msg = eventData.msg
                alert(msg);
                break

            case "incoming-call":
                // open the video call popup
                const videoCallPopup = document.getElementById('incoming-video-call-modal')
                document.getElementById('caller-id-text-for-video').innerText = eventData.from;
                videoCallPopup.setAttribute('class', 'show');
                break;

            case "call-reject":
                alert(`Your call is rejected by ${eventData.by}`)
                break;

            case "call-accepted":
                // setup peer connection and get offer and send offer another peer connection
                await setUpPeerConnection(eventData.from);
                const offer = await peerConnection.createOffer();
                await peerConnection.setLocalDescription(offer);

                socket.send(
                    JSON.stringify({
                        type: "offer",
                        targetId: eventData.from,
                        sdp: offer
                    })
                )

                document.getElementById("caller-id-text-for-video").innerText = '—';
                document.getElementById('incoming-video-call-modal').setAttribute('class', '');

                document.getElementById('video-call-screen').setAttribute('class', 'show');

                break;

            case "offer":
                await peerConnection.setRemoteDescription(
                    new RTCSessionDescription(eventData.sdp)
                );
                const asnwer = await peerConnection.createAnswer();
                await peerConnection.setLocalDescription(asnwer);

                socket.send(
                    JSON.stringify({
                        type: "answer",
                        targetId: eventData.from,
                        sdp: asnwer
                    })
                );
                break;
            
            case "answer":
                await peerConnection.setRemoteDescription(
                    new RTCSessionDescription(eventData.sdp)
                );
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
}

async function setUpPeerConnection(targetId) {
    if (stream === null) {
        stream = await navigator.mediaDevices.getUserMedia({
            audio: true,
            video: true
        })
    }

    document.getElementById('localVideo').srcObject = stream;

    peerConnection = new RTCPeerConnection({
        iceServers: [{
            urls: "stun:stun.l.google.com:19302"
        }]
    })

    peerConnection.onicecandidate = (event) => {
        if (event.candidate) {
            socket.send(
                JSON.stringify({
                    type: 'ice-candidate',
                    targetId: targetId,
                    candidate: event.candidate
                })
            )
        }
    }

    peerConnection.ontrack = (event) => {
        const remoteVideo = document.getElementById('remoteVideo');
        remoteVideo.srcObject = event.streams[0];
    }

    stream.getTracks().forEach(track => {
        peerConnection.addTrack(track, stream);
    })
}

initializeWebSocket();


// video call features
const videoCallBtn = document.getElementById('video-call-btn');
videoCallBtn.addEventListener('click', () => {
    if (!socket) {
        alert("You are disconnect from server, please ensure your internet connection and try again");
        return
    }

    socket.send(
        JSON.stringify({
            "type": "call-request",
            "to": CONTACT_USER.phone_number
        })
    )
});

const rejectCallBtn = document.getElementById('reject-video-btn');
rejectCallBtn.addEventListener('click', () => {
    if (!socket) {
        alert("You are disconnected from the server");
        return
    }

    socket.send(
        JSON.stringify(
            {
                "type": "call-reject",
                "whose": document.getElementById('caller-id-text-for-video').innerText
            }
        )
    );

    document.getElementById("caller-id-text-for-video").innerText = '—';
    document.getElementById('incoming-video-call-modal').setAttribute('class', '');
    return
})

const acceptCallBtn = document.getElementById('accept-video-btn');
acceptCallBtn.addEventListener('click', async () => {
    const callerId = document.getElementById('caller-id-text-for-video').innerText;
    document.getElementById("caller-id-text-for-video").innerText = '—';
    document.getElementById('incoming-video-call-modal').setAttribute('class', '');
    
    document.getElementById('video-call-screen').setAttribute('class', 'show');
    
    await setUpPeerConnection(callerId);
    socket.send(
        JSON.stringify({
            type: "call-accept",
            targetId: callerId
        })
    )
    return
})