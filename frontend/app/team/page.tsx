'use client';

import { useState, useEffect } from "react";
import { GlassCard } from "@/components/ui/GlassCard";
import { GlassButton } from "@/components/ui/GlassButton";
import { Users, Mail, Plus, Shield, ShieldCheck, UserPlus } from "lucide-react";
import { userService } from "@/services/userService";

export default function TeamPage() {
    const [team, setTeam] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [inviteEmail, setInviteEmail] = useState("");
    const [isInviting, setIsInviting] = useState(false);
    const [message, setMessage] = useState("");

    const fetchTeam = async () => {
        try {
            const data = await userService.getTeam();
            setTeam(data.team_members);
        } catch (error) {
            console.error("Team fetch error:", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchTeam();
    }, []);

    const handleInvite = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsInviting(true);
        setMessage("");
        try {
            await userService.invite(inviteEmail);
            setMessage("Davet başarıyla gönderildi!");
            setInviteEmail("");
            fetchTeam(); // Listeyi yenile
        } catch (error: any) {
            setMessage(error.response?.data?.error || "Davet gönderilemedi.");
        } finally {
            setIsInviting(false);
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
            <div className="flex justify-between items-end">
                <div>
                    <h2 className="text-3xl font-bold text-white">Ekip Yönetimi</h2>
                    <p className="text-gray-400 mt-1">Ajansınızdaki tüm profesyonelleri yönetin.</p>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Team List */}
                <div className="lg:col-span-2 space-y-4">
                    <h3 className="text-xl font-semibold flex items-center gap-2">
                        <Users className="w-5 h-5 text-primary-glow" />
                        Aktif Üyeler ({team.length})
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {team.map((member) => (
                            <GlassCard key={member.id} className="flex items-center gap-4">
                                <div className="w-12 h-12 rounded-full overflow-hidden bg-gradient-to-br from-primary to-purple-600 flex items-center justify-center text-white font-bold">
                                    {member.avatar ? (
                                        <img src={member.avatar} alt={member.name} className="w-full h-full object-cover" />
                                    ) : member.name[0]}
                                </div>
                                <div className="flex-1 min-w-0">
                                    <h4 className="font-bold text-white truncate">{member.name}</h4>
                                    <p className="text-xs text-gray-400 truncate">{member.email}</p>
                                    <div className="flex items-center gap-1 mt-1">
                                        {member.is_owner ? (
                                            <ShieldCheck className="w-3 h-3 text-yellow-500" />
                                        ) : (
                                            <Shield className="w-3 h-3 text-blue-400" />
                                        )}
                                        <span className="text-[10px] uppercase tracking-wider text-gray-500 font-bold">
                                            {member.role}
                                        </span>
                                    </div>
                                </div>
                            </GlassCard>
                        ))}
                    </div>
                </div>

                {/* Invite Form */}
                <div className="space-y-4">
                    <h3 className="text-xl font-semibold flex items-center gap-2">
                        <UserPlus className="w-5 h-5 text-green-400" />
                        Yeni Üye Davet Et
                    </h3>
                    <GlassCard variant="neon">
                        <form onSubmit={handleInvite} className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-400 mb-2">E-posta Adresi</label>
                                <div className="relative">
                                    <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                                    <input
                                        type="email"
                                        required
                                        value={inviteEmail}
                                        onChange={(e) => setInviteEmail(e.target.value)}
                                        className="w-full bg-white/5 border border-white/10 rounded-xl py-3 pl-10 pr-4 text-white focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all"
                                        placeholder="ornek@ajans.com"
                                    />
                                </div>
                            </div>
                            <GlassButton disabled={isInviting} className="w-full">
                                {isInviting ? "Gönderiliyor..." : "Davet Gönder"}
                            </GlassButton>
                            {message && (
                                <p className={`text-center text-sm ${message.includes('başarıyla') ? 'text-green-400' : 'text-red-400'}`}>
                                    {message}
                                </p>
                            )}
                        </form>
                    </GlassCard>
                </div>
            </div>
        </div>
    );
}
