var myPeerConnection = new RTCPeerConnection({
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
});
