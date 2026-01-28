import api from '@/lib/axios';

export interface DashboardStats {
    stats: {
        active_projects: { value: number; trend: string };
        pending_tasks: { value: number; trend: string };
        completed_tasks: { value: number; trend: string };
        monthly_revenue: { value: string; trend: string };
    };
    recent_projects: any[];
    schedule: {
        type: string;
        time: string;
        title: string;
        location: string;
        color: string;
    }[];
}

export const dashboardService = {
    getStats: async (): Promise<DashboardStats> => {
        const response = await api.get('/dashboard/stats/');
        return response.data;
    },
};
