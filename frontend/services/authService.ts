import api from '@/lib/axios';
import { useAuthStore } from '@/store/useAuthStore';

export const authService = {
    // Login
    login: async (email: string, password: string) => {
        const response = await api.post('/auth/login/', { email, password });

        // Tokenları kaydet
        localStorage.setItem('access_token', response.data.tokens.access);
        localStorage.setItem('refresh_token', response.data.tokens.refresh);

        // Global state güncelle
        useAuthStore.getState().setAuth(response.data.user, response.data.agency);

        return response.data;
    },

    // Register
    register: async (data: any) => {
        const response = await api.post('/auth/register/', data);

        if (response.data.tokens) {
            localStorage.setItem('access_token', response.data.tokens.access);
            localStorage.setItem('refresh_token', response.data.tokens.refresh);
            useAuthStore.getState().setAuth(response.data.user, response.data.agency);
        }

        return response.data;
    },

    // Logout
    logout: () => {
        useAuthStore.getState().logout();
        window.location.href = '/';
    }
};
