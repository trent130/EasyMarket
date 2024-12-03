

export enum WebSocketMessageType {
    CHAT_MESSAGE = 'CHAT_MESSAGE',
    NOTIFICATION = 'NOTIFICATION',
    ORDER_UPDATE = 'ORDER_UPDATE',
    PRODUCT_UPDATE = 'PRODUCT_UPDATE',
    USER_STATUS = 'USER_STATUS'
}

interface WebSocketMessage<T = unknown> {
    type: WebSocketMessageType;
    payload: T;
    timestamp: string;
}

export class WebSocketService {
    
    private socket: WebSocket | null = null;
    private messageHandlers: Map<WebSocketMessageType, ((data: unknown) => void)[]> = new Map();
    private reconnectAttempts = 0;
    private readonly maxReconnectAttempts = 5;

    constructor(private readonly url: string) {}

    /**
     * Connects to the WebSocket endpoint and sets up event listeners.
     * @remarks
     * When the connection is closed, the library will attempt to reconnect
     * up to `maxReconnectAttempts` times, with an exponential backoff time
     * between attempts.
     */
    connect() {
        this.socket = new WebSocket(this.url);
        
        // Handles WebSocket message event. The library expects the incoming
        // message to be a JSON object with a "type" field and a "payload" field.
        // The message is dispatched to all registered handlers for the given
        // message type.
        this.socket.onmessage = (event) => {
            const message: WebSocketMessage = JSON.parse(event.data);
            this.handleMessage(message);
        };

        // Handles WebSocket close event.
        // If the connection is closed, the library will attempt to reconnect
        // up to `maxReconnectAttempts` times, with an exponential backoff time
        // between attempts.
        this.socket.onclose = () => {
            this.handleDisconnect();
        };

        // Handles WebSocket errors, logging the error to the console.
        this.socket.onerror = (error) => {
            console.error('WebSocket error:', error, 'URL:', this.url, 'ReadyState:', this.socket?.readyState);
        };
    }

/**
 * Handles incoming WebSocket messages by dispatching them to the appropriate handlers.
 *
 * @param message - The WebSocket message containing a type and payload.
 * @remarks
 * This function retrieves all handlers registered for the message type and executes
 * them with the message payload.
 */
    private handleMessage(message: WebSocketMessage) {
        const handlers = this.messageHandlers.get(message.type) || [];
        handlers.forEach(handler => handler(message.payload));
    }

/**
 * Handles the WebSocket disconnection event by attempting to reconnect.
 *
 * @remarks
 * This function checks if the current number of reconnection attempts is less
 * than the maximum allowed. If so, it schedules a reconnection after a delay
 * using exponential backoff. The delay increases with each failed attempt.
 */
    private handleDisconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            setTimeout(() => {
                this.reconnectAttempts++;
                this.connect();
            }, 1000 * Math.pow(2, this.reconnectAttempts));
        }
    }

    /**
     * Subscribes to incoming WebSocket messages of the given type.
     *
     * @param type - The type of WebSocket message to subscribe to.
     * @param handler - The function to execute when a message of the given type is received.
     * @template T - The expected type of the message payload.
     */
    subscribe<T>(type: WebSocketMessageType, handler: (data: T) => void) {
        const handlers = this.messageHandlers.get(type) || [];
        handlers.push(handler);
        this.messageHandlers.set(type, handlers);
    }

    /**
     * Unsubscribes from incoming WebSocket messages of the given type.
     *
     * @param type - The type of WebSocket message to unsubscribe from.
     * @param handler - The function to remove from the subscription list.
     */
    unsubscribe<T>(type: WebSocketMessageType, handler: (data: T) => void) {
        const handlers = this.messageHandlers.get(type) || [];
        this.messageHandlers.set(
            type,
            handlers.filter(h => h !== handler)
        );
    }

    /**
     * Sends a WebSocket message of the given type with the given payload.
     *
     * @param type - The type of WebSocket message to send.
     * @param payload - The payload of the message to send.
     * @remarks
     * This function will only send a message if the WebSocket connection is open.
     * If the connection is not open, the message will not be sent and this function
     * will not throw an error.
     */
    send(type: WebSocketMessageType, payload: unknown) {
        if (this.socket?.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify({
                type,
                payload,
                timestamp: new Date().toISOString()
            }));
        }
    }

    /**
     * Disconnects from the WebSocket endpoint, closing the connection and clearing
     * all registered message handlers.
     */
    disconnect() {
        this.socket?.close();
        this.socket = null;
        this.messageHandlers.clear();
    }
}
