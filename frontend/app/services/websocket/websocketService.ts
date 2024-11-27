export enum WebSocketMessageType {
    CHAT_MESSAGE = 'CHAT_MESSAGE',
    NOTIFICATION = 'NOTIFICATION',
    ORDER_UPDATE = 'ORDER_UPDATE',
    PRODUCT_UPDATE = 'PRODUCT_UPDATE',
    USER_STATUS = 'USER_STATUS'
}

interface WebSocketMessage<T = any> {
    type: WebSocketMessageType;
    payload: T;
    timestamp: string;
}

export class WebSocketService {
    private socket: WebSocket | null = null;
    private messageHandlers: Map<WebSocketMessageType, ((data: any) => void)[]> = new Map();
    private reconnectAttempts = 0;
    private readonly maxReconnectAttempts = 5;

    constructor(private readonly url: string) {}

    connect() {
        this.socket = new WebSocket(this.url);
        
        this.socket.onmessage = (event) => {
            const message: WebSocketMessage = JSON.parse(event.data);
            this.handleMessage(message);
        };

        this.socket.onclose = () => {
            this.handleDisconnect();
        };

        this.socket.onerror = (error) => {
            console.error('WebSocket error:', error);
        };
    }

    private handleMessage(message: WebSocketMessage) {
        const handlers = this.messageHandlers.get(message.type) || [];
        handlers.forEach(handler => handler(message.payload));
    }

    private handleDisconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            setTimeout(() => {
                this.reconnectAttempts++;
                this.connect();
            }, 1000 * Math.pow(2, this.reconnectAttempts));
        }
    }

    subscribe<T>(type: WebSocketMessageType, handler: (data: T) => void) {
        const handlers = this.messageHandlers.get(type) || [];
        handlers.push(handler);
        this.messageHandlers.set(type, handlers);
    }

    unsubscribe(type: WebSocketMessageType, handler: (data: any) => void) {
        const handlers = this.messageHandlers.get(type) || [];
        this.messageHandlers.set(
            type,
            handlers.filter(h => h !== handler)
        );
    }

    send(type: WebSocketMessageType, payload: any) {
        if (this.socket?.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify({
                type,
                payload,
                timestamp: new Date().toISOString()
            }));
        }
    }

    disconnect() {
        this.socket?.close();
        this.socket = null;
        this.messageHandlers.clear();
    }
} 