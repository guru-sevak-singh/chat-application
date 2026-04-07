//API Key for the credential: 9984594a0f4f83827d573ff45656a13ebcb9

// Calling the REST API TO fetch the TURN Server Credentials
const response = 
  await fetch("https://guru-sevak-singh.metered.live/api/v1/turn/credentials?apiKey=9984594a0f4f83827d573ff45656a13ebcb9");

// Saving the response in the iceServers array
const iceServers = await response.json();

// Using the iceServers array in the RTCPeerConnection method
var myPeerConnection = new RTCPeerConnection({
  iceServers: iceServers
});