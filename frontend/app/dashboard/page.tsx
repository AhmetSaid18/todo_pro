'use client';

import { useEffect, useState } from "react";
import { GlassCard } from "@/components/ui/GlassCard";
import { GlassButton } from "@/components/ui/GlassButton";
import {
    Film,
    CheckCircle2,
    AlertCircle,
    TrendingUp,
    Calendar as CalendarIcon,
    MoreHorizontal,
    Clock,
    MapPin,
    Play
} from "lucide-react";
import { motion } from "framer-motion";
import { useAuthStore } from "@/store/useAuthStore";
import { dashboardService, DashboardStats } from "@/services/dashboardService";
import { format } from "date-fns";
import { tr } from "date-fns/locale";

export default function DashboardPage() {
    const { user } = useAuthStore();
    const [data, setData] = useState<DashboardStats | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchDashboardData = async () => {
            try {
                const stats = await dashboardService.getStats();
                setData(stats);
            } catch (error) {
                console.error("Dashboard data fetch error:", error);
            } finally {
                setLoading(false);
            }
        };

        fetchDashboardData();
    }, []);

    const container = {
        hidden: { opacity: 0 },
        show: {
            opacity: 1,
            transition: {
                staggerChildren: 0.1
            }
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-[60vh]">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
            </div>
        );
    }

    return (
        <div className="space-y-8">

            {/* Header */}
            <div className="flex justify-between items-end">
                <div>
                    <h2 className="text-3xl font-bold bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">
                        Hoş Geldin, {user?.first_name || 'Kullanıcı'} 👋
                    </h2>
                    <p className="text-gray-400 mt-1">
                        Bugün {format(new Date(), "d MMMM, EEEE", { locale: tr })}. Harika bir iş günü olsun!
                    </p>
                </div>
                <div className="flex gap-3">
                    <GlassButton variant="secondary" size="sm">Raporlar</GlassButton>
                    <GlassButton size="sm">
                        <Play className="w-4 h-4 mr-2" /> Yeni Proje
                    </GlassButton>
                </div>
            </div>

            {/* Stats Grid */}
            <motion.div
                variants={container}
                initial="hidden"
                animate="show"
                className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
            >
                <StatCard
                    title="Aktif Projeler"
                    value={data?.stats.active_projects.value.toString() || "0"}
                    trend={data?.stats.active_projects.trend}
                    icon={<Film className="w-6 h-6 text-blue-400" />}
                    color="bg-blue-500/10 text-blue-400"
                />
                <StatCard
                    title="Bekleyen Görevler"
                    value={data?.stats.pending_tasks.value.toString() || "0"}
                    trend={data?.stats.pending_tasks.trend}
                    icon={<AlertCircle className="w-6 h-6 text-yellow-400" />}
                    color="bg-yellow-500/10 text-yellow-400"
                />
                <StatCard
                    title="Tamamlanan"
                    value={data?.stats.completed_tasks.value.toString() || "0"}
                    trend={data?.stats.completed_tasks.trend}
                    icon={<CheckCircle2 className="w-6 h-6 text-green-400" />}
                    color="bg-green-500/10 text-green-400"
                />
                <StatCard
                    title="Aylık Ciro"
                    value={data?.stats.monthly_revenue.value || "₺0"}
                    trend={data?.stats.monthly_revenue.trend}
                    icon={<TrendingUp className="w-6 h-6 text-primary-glow" />}
                    color="bg-primary/10 text-primary-glow"
                />
            </motion.div>

            {/* Main Content Split */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

                {/* Left Column (Projects) */}
                <div className="lg:col-span-2 space-y-6">
                    <div className="flex justify-between items-center">
                        <h3 className="text-xl font-semibold">Devam Eden Projeler</h3>
                        <button className="text-sm text-primary-glow hover:text-white transition-colors">Tümünü Gör</button>
                    </div>

                    <div className="space-y-4">
                        {data?.recent_projects.map((project) => (
                            <ProjectCard
                                key={project.id}
                                title={project.title}
                                client={project.client_name || "Bireysel"}
                                status={project.status_display || project.status}
                                progress={project.progress_percentage || 0}
                                date={`${format(new Date(project.start_date), "dd MMM")} - ${format(new Date(project.end_date), "dd MMM")}`}
                                team={project.team_members || []}
                            />
                        ))}
                        {data?.recent_projects.length === 0 && (
                            <div className="text-center py-12 text-gray-500">
                                Henüz aktif bir proje bulunmuyor.
                            </div>
                        )}
                    </div>
                </div>

                {/* Right Column (Schedule & Quick Actions) */}
                <div className="space-y-6">
                    <h3 className="text-xl font-semibold">Bugünün Programı</h3>

                    <GlassCard className="space-y-6">
                        {data?.schedule.map((item, index) => (
                            <div key={index} className="flex gap-4 items-start">
                                <div className="flex flex-col items-center">
                                    <span className="text-xs font-bold text-gray-500">{item.time}</span>
                                    <div className="w-0.5 h-full bg-gray-800 my-2 relative">
                                        <div className={`absolute top-0 left-1/2 -translate-x-1/2 w-2 h-2 rounded-full ${item.color === 'blue' ? 'bg-blue-500' :
                                            item.color === 'green' ? 'bg-green-500' : 'bg-purple-500'
                                            }`} />
                                    </div>
                                </div>
                                <div>
                                    <h4 className="font-medium text-white">{item.title}</h4>
                                    <p className="text-sm text-gray-400">{item.location}</p>
                                </div>
                            </div>
                        ))}
                        {data?.schedule.length === 0 && (
                            <div className="text-center py-6 text-gray-500 text-sm">
                                Bugün için bir program bulunmuyor.
                            </div>
                        )}
                    </GlassCard>

                    <GlassCard variant="neon" className="bg-primary/5 border-primary/20">
                        <h4 className="font-semibold mb-2">Hızlı Görev</h4>
                        <GlassButton variant="primary" size="sm" className="w-full">
                            + Görev Ekle
                        </GlassButton>
                    </GlassCard>

                </div>
            </div>

        </div>
    );
}

// 📦 Helper Components

function StatCard({ title, value, trend, icon, color }: any) {
    return (
        <GlassCard className="hover:-translate-y-1 transition-transform duration-300">
            <div className="flex justify-between items-start mb-4">
                <div className={`p-3 rounded-xl ${color}`}>
                    {icon}
                </div>
                <button className="text-gray-500 hover:text-white">
                    <MoreHorizontal className="w-5 h-5" />
                </button>
            </div>
            <div>
                <p className="text-gray-400 text-sm mb-1">{title}</p>
                <div className="flex items-end gap-3">
                    <h3 className="text-2xl font-bold text-white">{value}</h3>
                    <span className="text-xs font-medium text-green-400 mb-1 bg-green-500/10 px-2 py-0.5 rounded-full">
                        {trend}
                    </span>
                </div>
            </div>
        </GlassCard>
    )
}

function ProjectCard({ title, client, status, progress, date, team }: any) {
    const statusColors: any = {
        'Hazırlık': 'bg-gray-500/20 text-gray-300',
        'Çekimde': 'bg-blue-500/20 text-blue-300',
        'Kurguda': 'bg-purple-500/20 text-purple-300',
        'Tamamlandı': 'bg-green-500/20 text-green-300',
    };

    return (
        <GlassCard className="group cursor-pointer hover:bg-glass-200">
            <div className="flex flex-col md:flex-row gap-6 items-center">
                {/* Image Placeholder */}
                <div className="w-full md:w-16 h-16 rounded-xl bg-gradient-to-br from-gray-700 to-gray-800 flex items-center justify-center shrink-0 shadow-inner group-hover:scale-105 transition-transform duration-300">
                    <Film className="w-8 h-8 text-gray-500" />
                </div>

                <div className="flex-1 min-w-0 w-full">
                    <div className="flex justify-between items-start mb-2">
                        <div>
                            <h4 className="font-bold text-lg text-white group-hover:text-primary-glow transition-colors">{title}</h4>
                            <p className="text-sm text-gray-400">{client}</p>
                        </div>
                        <span className={`text-xs px-3 py-1 rounded-full font-medium ${statusColors[status] || 'bg-gray-700 text-gray-400'}`}>
                            {status}
                        </span>
                    </div>

                    <div className="flex items-center gap-6 text-sm text-gray-500">
                        <div className="flex items-center gap-1.5">
                            <Clock className="w-4 h-4" />
                            {date}
                        </div>
                        <div className="flex items-center gap-2 flex-1">
                            <div className="h-1.5 w-full bg-gray-800 rounded-full overflow-hidden">
                                <div
                                    className="h-full bg-primary rounded-full transition-all duration-1000"
                                    style={{ width: `${progress}%` }}
                                />
                            </div>
                            <span className="text-xs font-medium w-8">{progress}%</span>
                        </div>
                    </div>
                </div>

                {/* Team Avatars */}
                <div className="flex -space-x-2">
                    {team.map((_: any, i: number) => (
                        <div key={i} className="w-8 h-8 rounded-full bg-gray-700 border-2 border-[#0a0a0a] flex items-center justify-center text-[10px] text-white font-bold">
                            {/* Placeholder for now */}
                            U{i + 1}
                        </div>
                    ))}
                    <div className="w-8 h-8 rounded-full bg-gray-800 border-2 border-[#0a0a0a] flex items-center justify-center text-[10px] text-gray-400 font-bold">
                        +2
                    </div>
                </div>
            </div>
        </GlassCard>
    )
}
