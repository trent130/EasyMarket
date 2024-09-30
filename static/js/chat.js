// Function to connect to the WebSocket server
function connectToWebSocket() {
    var socket = new WebSocket('ws://' + window.location.host + '/ws/chat/');

    // Event listener for incoming messages
    socket.onmessage = function(event) {
        var data = JSON.parse(event.data);
        var message = data['message'];
        // Handle incoming message
        handleIncomingMessage(message);
    };

    // Event listener for WebSocket connection close
    socket.onclose = function(event) {
        console.error('Chat socket closed unexpectedly');
    };

    // Event listener for sending messages on pressing enter
    document.querySelector('#chat-message-input').addEventListener('keyup', function(event) {
        if (event.keyCode === 13) {  // Enter key
            sendMessage(socket);
        }
    });

    // Event listener for sending messages on button click
    document.querySelector('#chat-message-submit').addEventListener('click', function(event) {
        sendMessage(socket);
    });

    return socket;
}

// Function to handle incoming messages
function handleIncomingMessage(message) {
    // Do something with the incoming message
    console.log('Received message:', message);
}

// Function to send a message via WebSocket
function sendMessage(socket) {
    var messageInputDom = document.querySelector('#chat-message-input');
    var message = messageInputDom.value.trim(); // Trim whitespace
    if (message) {
        socket.send(JSON.stringify({
            'message': message
        }));
        messageInputDom.value = ''; // Clear message input
    }
}

// Connect to WebSocket when the page loads
var socket = connectToWebSocket();