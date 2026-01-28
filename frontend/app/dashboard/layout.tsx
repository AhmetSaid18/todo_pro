import { Sidebar } from "@/components/layout/Sidebar";
import React from "react";

export default function DashboardLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <div className="relative min-h-screen bg-[#050505] text-white overflow-x-hidden font-sans selection:bg-primary/30">

            {/* Background Ambience */}
            <div className="fixed inset-0 z-0 pointer-events-none">
                <div className="absolute inset-0 bg-[url('/grid.svg')] opacity-[0.03]" />
                {/* Top Right Glow */}
                <div className="absolute top-[-20%] right-[-10%] w-[800px] h-[800px] bg-primary/10 rounded-full blur-[150px]" />
                {/* Bottom Left Glow */}
                <div className="absolute bottom-[-20%] left-[-10%] w-[600px] h-[600px] bg-blue-600/10 rounded-full blur-[150px]" />
            </div>

            {/* Sidebar */}
            <Sidebar />

            {/* Main Content */}
            <main className="relative z-10 pl-72 pr-8 py-8 min-h-screen">
                {/* Top Bar (Optional search/notifications could go here) */}
                <div className="max-w-7xl mx-auto">
                    {children}
                </div>
            </main>

        </div>
    );
}
