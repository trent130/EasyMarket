import { fetchWrapper } from '../../utils/fetchWrapper';
import { User } from '../../types/common';

interface Message {
    id: number;
    senderId: number;
    receiverId: number;
    content: string;
    attachments?: string[];
    read: boolean;
    createdAt: string;
}

interface Conversation {
    id: number;
    participants: User[];
    lastMessage: Message;
    unreadCount: number;
    updatedAt: string;
}

interface ChatParams {
    page?: number;
    pageSize?: number;
    before?: string;
    after?: string;
}

export const chatApi = {
    getConversations: (params?: Record<string, string | number>) =>
        fetchWrapper<Conversation[]>('/api/chat/conversations', { params }),
    
    getMessages: (conversationId: number, params?: Record<string, string | number>) =>
        fetchWrapper<Message[]>(`/api/chat/conversations/${conversationId}/messages`, { params }),
    sendMessage: (conversationId: number, content: string, attachments?: File[]) => {
        const formData = new FormData();
        formData.append('content', content);
        attachments?.forEach(file => formData.append('attachments', file));
        
        return fetchWrapper<Message>(`/api/chat/conversations/${conversationId}/messages`, {
            method: 'POST',
            body: formData,
            headers: {} // Let browser set content-type for FormData
        });
    },
    
    markAsRead: (conversationId: number) =>
        fetchWrapper<void>(`/api/chat/conversations/${conversationId}/read`, {
            method: 'PUT'
        }),
};

export type ChatApi = typeof chatApi;

// backend implimentations of the same needed
