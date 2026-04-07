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
                document.getElementById('remote-user-name').innerText = eventData.from;
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

            case "call-end":
                if (peerConnection) {
                    document.getElementById('remote-user-name').innerText = '—'
                    document.getElementById('video-call-screen').setAttribute('class', '');
                }
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
        iceServers: [
            {
                urls: "stun:stun.relay.metered.ca:80",
            },
            {
                urls: "turn:global.relay.metered.ca:80",
                username: "2b2719f9ca1ea7b6a7df3a2f",
                credential: "o5xajszcOs3pmr3X",
            },
            {
                urls: "turn:global.relay.metered.ca:80?transport=tcp",
                username: "2b2719f9ca1ea7b6a7df3a2f",
                credential: "o5xajszcOs3pmr3X",
            },
            {
                urls: "turn:global.relay.metered.ca:443",
                username: "2b2719f9ca1ea7b6a7df3a2f",
                credential: "o5xajszcOs3pmr3X",
            },
            {
                urls: "turns:global.relay.metered.ca:443?transport=tcp",
                username: "2b2719f9ca1ea7b6a7df3a2f",
                credential: "o5xajszcOs3pmr3X",
            },
        ],
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
    document.getElementById('remote-user-name').innerText = callerId

    await setUpPeerConnection(callerId);
    socket.send(
        JSON.stringify({
            type: "call-accept",
            targetId: callerId
        })
    )
    return
})


const toggleMicBtn = document.getElementById('toggle-mic-btn');
toggleMicBtn.addEventListener('click', () => {
    const audioTrack = stream.getAudioTracks()[0];
    audioTrack.enabled = !audioTrack.enabled //toggle
    const style_classes = audioTrack.enabled ? "ctrl-btn" : "ctrl-btn end-call-btn";
    toggleMicBtn.setAttribute('class', style_classes);
});

const toogleCameraBtn = document.getElementById('toggle-cam-btn');
toogleCameraBtn.addEventListener('click', () => {
    const videoTrack = stream.getVideoTracks()[0];
    videoTrack.enabled = !videoTrack.enabled; // toogle
    const style_classes = videoTrack.enabled ? "ctrl-btn" : "ctrl-btn end-call-btn";
    toogleCameraBtn.setAttribute('class', style_classes)
});

function endCall() {
    // stop all tracks;
    stream.getTracks().forEach(track => track.stop());

    // close the peer to peer connection
    peerConnection.close();

    socket.send(JSON.stringify(
        {
            type: 'call-end',
            targetId: document.getElementById('remote-user-name').innerText.trim()
        }
    ))
    document.getElementById('remote-user-name').innerText = '—'
    document.getElementById('video-call-screen').setAttribute('class', '');
}

const endCallBtn = document.getElementById('end-video-call-btn');
endCallBtn.addEventListener('click', () => {
    endCall();
})
