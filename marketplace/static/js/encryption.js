
<script src="https://cdnjs.cloudflare.com/ajax/libs/crypto-js/4.1.1/crypto-js.min.js"></script>

// Function to encrypt message using AES
function encryptMessage(message, key) {
    // Convert key and message to WordArray
    var keyHex = CryptoJS.enc.Utf8.parse(key);
    var messageUtf8 = CryptoJS.enc.Utf8.parse(message);

    // Encrypt message using AES
    var encrypted = CryptoJS.AES.encrypt(messageUtf8, keyHex, {
        mode: CryptoJS.mode.ECB,
        padding: CryptoJS.pad.Pkcs7
    });

    // Return base64-encoded encrypted message
    return encrypted.toString();
}

// Example usage
var message = 'Hello, world!';
var key = 'supersecretkey';
var encryptedMessage = encryptMessage(message, key);
console.log('Encrypted message:', encryptedMessage);

