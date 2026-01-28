import api from '@/lib/axios';

export interface Project {
    id: number;
    title: string;
    description: string;
    client_name: string;
    status: string;
    priority: string;
    start_date: string;
    end_date: string;
    location: string;
    budget_estimated: string;
    created_at: string;
    tags: string[];
    task_count?: number;
    completed_tasks?: number;
}

export const projectService = {
    getAll: async () => {
        const response = await api.get('/projects/');
        return response.data;
    },
    getActive: async () => {
        const response = await api.get('/projects/active/');
        return response.data;
    },
    getById: async (id: number) => {
        const response = await api.get(`/projects/${id}/`);
        return response.data;
    },
    create: async (data: Partial<Project>) => {
        const response = await api.post('/projects/', data);
        return response.data;
    },
};
