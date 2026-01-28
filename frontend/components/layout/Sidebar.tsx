'use client';

import { GlassCard } from "@/components/ui/GlassCard";
import { cn } from "@/lib/utils";
import {
    LayoutDashboard,
    Film,
    CheckSquare,
    Calendar,
    CreditCard,
    Camera,
    Users,
    Settings,
    LogOut,
    Bell
} from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion } from "framer-motion";

const menuItems = [
    { href: "/dashboard", label: "Genel Bakış", icon: LayoutDashboard },
    { href: "/projects", label: "Projeler", icon: Film },
    { href: "/tasks", label: "Görevler", icon: CheckSquare },
    { href: "/schedule", label: "Takvim & Plan", icon: Calendar },
    { href: "/finance", label: "Finans", icon: CreditCard },
    { href: "/inventory", label: "Ekipman", icon: Camera },
    { href: "/team", label: "Ekip", icon: Users },
];

import { useAuthStore } from "@/store/useAuthStore";

export const Sidebar = () => {
    const pathname = usePathname();
    const { user, logout } = useAuthStore();

    return (
        <aside className="fixed left-0 top-0 h-screen w-64 p-4 z-40">
            <GlassCard className="h-full flex flex-col justify-between backdrop-blur-3xl bg-glass-200/50 border-white/5" noPadding>

                {/* Logo Area */}
                <div className="p-6 pb-2">
                    <div className="flex items-center gap-3 mb-8">
                        <div className="w-8 h-8 bg-gradient-to-tr from-primary to-[#e92a67] rounded-lg flex items-center justify-center shadow-lg shadow-primary/30">
                            <span className="font-bold text-white text-lg">T</span>
                        </div>
                        <div>
                            <h1 className="font-bold text-white tracking-tight leading-none">Todo</h1>
                            <span className="text-[10px] text-gray-400 uppercase tracking-widest">Production</span>
                        </div>
                    </div>

                    {/* User Mini Profile */}
                    <div className="flex items-center gap-3 p-3 rounded-xl bg-white/5 border border-white/5 mb-6">
                        <div className="w-8 h-8 rounded-full bg-gray-700 overflow-hidden relative">
                            {user?.avatar ? (
                                <img src={user.avatar} alt={user.full_name} className="w-full h-full object-cover" />
                            ) : (
                                <div className="absolute inset-0 bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-[10px] font-bold text-white uppercase">
                                    {user?.first_name?.[0]}{user?.last_name?.[0]}
                                </div>
                            )}
                        </div>
                        <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium text-white truncate">{user?.full_name || 'Kullanıcı'}</p>
                            <p className="text-xs text-green-400">Online</p>
                        </div>
                        <button className="text-gray-400 hover:text-white transition-colors">
                            <Bell className="w-4 h-4" />
                        </button>
                    </div>

                    {/* Menu */}
                    <nav className="space-y-1">
                        <p className="px-4 text-[10px] font-semibold text-gray-500 uppercase tracking-wider mb-2">Menu</p>
                        {menuItems.map((item) => {
                            const isActive = pathname === item.href;
                            const Icon = item.icon;
                            return (
                                <Link key={item.href} href={item.href}>
                                    <div className={cn(
                                        "relative px-4 py-3 rounded-xl flex items-center gap-3 transition-all duration-300 group overflow-hidden",
                                        isActive ? "text-white" : "text-gray-400 hover:text-white hover:bg-white/5"
                                    )}>
                                        {isActive && (
                                            <motion.div
                                                layoutId="activeTab"
                                                className="absolute inset-0 bg-primary/20 border border-primary/20 rounded-xl"
                                                initial={false}
                                                transition={{ type: "spring", stiffness: 300, damping: 30 }}
                                            />
                                        )}
                                        <Icon className={cn("w-5 h-5 relative z-10", isActive && "text-primary-glow drop-shadow-[0_0_8px_rgba(139,92,246,0.5)]")} />
                                        <span className={cn("text-sm font-medium relative z-10", isActive && "text-white")}>
                                            {item.label}
                                        </span>
                                    </div>
                                </Link>
                            )
                        })}
                    </nav>
                </div>

                {/* Footer Actions */}
                <div className="p-4 space-y-1">
                    <Link href="/settings">
                        <div className="px-4 py-3 rounded-xl flex items-center gap-3 text-gray-400 hover:text-white hover:bg-white/5 transition-colors">
                            <Settings className="w-5 h-5" />
                            <span className="text-sm font-medium">Ayarlar</span>
                        </div>
                    </Link>
                    <button
                        onClick={logout}
                        className="w-full px-4 py-3 rounded-xl flex items-center gap-3 text-red-400 hover:text-red-300 hover:bg-red-500/10 transition-colors text-left"
                    >
                        <LogOut className="w-5 h-5" />
                        <span className="text-sm font-medium">Çıkış Yap</span>
                    </button>
                </div>

            </GlassCard>
        </aside>
    );
};
