import { fetchWrapper } from '../../utils/fetchWrapper';
import { GroupChat, GroupMessage } from '../../types/common';
import { WebSocketService, WebSocketMessageType } from '../../../lib/websocket';



// interface GroupChatParams {
//     page?: number;
//     pageSize?: number;
//     search?: string;
// }

export const groupChatApi = {
    // Group Management
    createGroup: (data: { name: string; description?: string; memberIds: number[] }) =>
        fetchWrapper<GroupChat>('/api/chat/groups', {
            method: 'POST',
            body: JSON.stringify(data)
        }),

    updateGroup: (groupId: number, data: Partial<GroupChat>) =>
        fetchWrapper<GroupChat>(`/api/chat/groups/${groupId}`, {
            method: 'PUT',
            body: JSON.stringify(data)
        }),

    // Member Management
    addMembers: (groupId: number, memberIds: number[]) =>
        fetchWrapper<GroupChat>(`/api/chat/groups/${groupId}/members`, {
            method: 'POST',
            body: JSON.stringify({ memberIds })
        }),

    removeMembers: (groupId: number, memberIds: number[]) =>
        fetchWrapper<GroupChat>(`/api/chat/groups/${groupId}/members`, {
            method: 'DELETE',
            body: JSON.stringify({ memberIds })
        }),

    // Message Management
    getGroupMessages: (groupId: number, params?: Record<string, string | number>) =>
        fetchWrapper<GroupMessage[]>(`/api/chat/groups/${groupId}/messages`, { params }),

    sendGroupMessage: (groupId: number, content: string, attachments?: File[]) => {
        const formData = new FormData();
        formData.append('content', content);
        attachments?.forEach(file => formData.append('attachments', file));

        return fetchWrapper<GroupMessage>(`/api/chat/groups/${groupId}/messages`, {
            method: 'POST',
            body: formData,
            headers: {} // Let browser set content-type for FormData
        });
    },

    // Reactions
    addReaction: (groupId: number, messageId: number, emoji: string) =>
        fetchWrapper<GroupMessage>(`/api/chat/groups/${groupId}/messages/${messageId}/reactions`, {
            method: 'POST',
            body: JSON.stringify({ emoji })
        }),

    removeReaction: (groupId: number, messageId: number, emoji: string) =>
        fetchWrapper<GroupMessage>(`/api/chat/groups/${groupId}/messages/${messageId}/reactions`, {
            method: 'DELETE',
            body: JSON.stringify({ emoji })
        }),

    // Real-time features using WebSocket
    subscribeToGroupUpdates: (groupId: number, wsService: WebSocketService) => {
        wsService.subscribe(WebSocketMessageType.CHAT_MESSAGE, (message: unknown) => {
            const groupMessage = message as GroupMessage;
            if (groupMessage.groupId === groupId) {
              // Handle new message
              console.log('New group message:', groupMessage);
            }
          });
    }
};

export type GroupChatApi = typeof groupChatApi;

// implimentation of the backend generally needed here for the urls and so in the marketplace app
