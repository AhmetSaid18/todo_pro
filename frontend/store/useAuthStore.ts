import { create } from 'zustand';

interface User {
    id: number;
    email: string;
    first_name: string;
    last_name: string;
    full_name: string;
    avatar: string | null;
    role_name?: string;
}

interface Agency {
    id: number;
    name: string;
    role: string;
    is_owner: boolean;
}

interface AuthState {
    user: User | null;
    agency: Agency | null;
    isAuthenticated: boolean;
    setAuth: (user: User, agency: Agency | null) => void;
    logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
    user: null,
    agency: null,
    isAuthenticated: false,

    setAuth: (user, agency) => {
        localStorage.setItem('user', JSON.stringify(user));
        localStorage.setItem('agency', JSON.stringify(agency));
        set({ user, agency, isAuthenticated: true });
    },

    logout: () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
        localStorage.removeItem('agency');
        set({ user: null, agency: null, isAuthenticated: false });
    },
}));
