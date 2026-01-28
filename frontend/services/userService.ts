import api from '@/lib/axios';

export const userService = {
    getMe: async () => {
        const response = await api.get('/users/me/');
        return response.data;
    },
    getTeam: async () => {
        const response = await api.get('/users/team/');
        return response.data;
    },
    invite: async (email: string, role_id?: number) => {
        const response = await api.post('/users/invite/', { email, role_id });
        return response.data;
    },
};
