'use client';

import { motion } from 'framer-motion';
import { GlassCard } from '@/components/ui/GlassCard';
import { GlassInput } from '@/components/ui/GlassInput';
import { GlassButton } from '@/components/ui/GlassButton';
import { Mail, Lock, ArrowRight, Zap, AlertTriangle, User, Building } from 'lucide-react';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { authService } from '@/services/authService';
import Link from 'next/link';

export default function RegisterPage() {
    const router = useRouter();
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const [formData, setFormData] = useState({
        email: '',
        password: '',
        first_name: '',
        last_name: '',
        agency_name: ''
    });

    const handleRegister = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setError(null);

        try {
            await authService.register(formData);
            router.push('/dashboard');
        } catch (err: any) {
            console.error("Register Error:", err);
            setError(err.response?.data?.error || "Kayıt başarısız. Lütfen bilgileri kontrol edin.");
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <main className="relative min-h-screen w-full flex items-center justify-center overflow-hidden bg-[#050505]">

            {/* 🌌 Background Effects */}
            <div className="absolute inset-0 w-full h-full">
                <motion.div
                    animate={{
                        scale: [1, 1.2, 1],
                        opacity: [0.3, 0.5, 0.3],
                        x: [0, 50, 0],
                        y: [0, -30, 0]
                    }}
                    transition={{ duration: 10, repeat: Infinity, ease: "easeInOut" }}
                    className="absolute top-[-10%] left-[-10%] w-[500px] h-[500px] bg-primary/20 rounded-full blur-[120px]"
                />
                <motion.div
                    animate={{
                        scale: [1, 1.5, 1],
                        opacity: [0.2, 0.4, 0.2],
                        x: [0, -40, 0],
                    }}
                    transition={{ duration: 15, repeat: Infinity, ease: "easeInOut" }}
                    className="absolute bottom-[-10%] right-[-10%] w-[600px] h-[600px] bg-[#e92a67]/20 rounded-full blur-[150px]"
                />
                <div className="absolute inset-0 bg-[url('/grid.svg')] opacity-[0.05] pointer-events-none" />
            </div>

            {/* 📦 Register Content */}
            <div className="relative z-10 w-full max-w-lg px-6 py-12">
                <GlassCard className="w-full backdrop-blur-2xl border-white/10 shadow-[0_0_50px_-12px_rgba(109,40,217,0.25)]">

                    {/* Header */}
                    <div className="text-center mb-8">
                        <motion.div
                            initial={{ scale: 0.5, opacity: 0 }}
                            animate={{ scale: 1, opacity: 1 }}
                            transition={{ duration: 0.5 }}
                            className="w-16 h-16 bg-gradient-to-tr from-primary to-[#e92a67] rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg shadow-primary/30"
                        >
                            <Zap className="w-8 h-8 text-white fill-white" />
                        </motion.div>

                        <motion.h1
                            initial={{ y: 20, opacity: 0 }}
                            animate={{ y: 0, opacity: 1 }}
                            transition={{ delay: 0.1 }}
                            className="text-3xl font-bold text-white mb-2 tracking-tight"
                        >
                            Hemen Başla
                        </motion.h1>
                        <motion.p
                            initial={{ y: 20, opacity: 0 }}
                            animate={{ y: 0, opacity: 1 }}
                            transition={{ delay: 0.2 }}
                            className="text-gray-400"
                        >
                            Ajansını kur ve ekibini yönetmeye başla
                        </motion.p>
                    </div>

                    {/* Error Message */}
                    {error && (
                        <motion.div
                            initial={{ opacity: 0, y: -10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="mb-6 p-3 rounded-xl bg-red-500/10 border border-red-500/20 flex items-center gap-3 text-red-400 text-sm"
                        >
                            <AlertTriangle className="w-4 h-4 shrink-0" />
                            {error}
                        </motion.div>
                    )}

                    {/* Form */}
                    <form onSubmit={handleRegister} className="space-y-4">
                        <div className="grid grid-cols-2 gap-4">
                            <motion.div
                                initial={{ x: -20, opacity: 0 }}
                                animate={{ x: 0, opacity: 1 }}
                                transition={{ delay: 0.3 }}
                            >
                                <GlassInput
                                    icon={<User className="w-5 h-5" />}
                                    placeholder="Fatih"
                                    label="Ad"
                                    type="text"
                                    required
                                    value={formData.first_name}
                                    onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
                                />
                            </motion.div>
                            <motion.div
                                initial={{ x: 20, opacity: 0 }}
                                animate={{ x: 0, opacity: 1 }}
                                transition={{ delay: 0.3 }}
                            >
                                <GlassInput
                                    icon={<User className="w-5 h-5" />}
                                    placeholder="Gül"
                                    label="Soyad"
                                    type="text"
                                    required
                                    value={formData.last_name}
                                    onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
                                />
                            </motion.div>
                        </div>

                        <motion.div
                            initial={{ x: -20, opacity: 0 }}
                            animate={{ x: 0, opacity: 1 }}
                            transition={{ delay: 0.4 }}
                        >
                            <GlassInput
                                icon={<Building className="w-5 h-5" />}
                                placeholder="Limitless Production"
                                label="Ajans Adı"
                                type="text"
                                required
                                value={formData.agency_name}
                                onChange={(e) => setFormData({ ...formData, agency_name: e.target.value })}
                            />
                        </motion.div>

                        <motion.div
                            initial={{ x: -20, opacity: 0 }}
                            animate={{ x: 0, opacity: 1 }}
                            transition={{ delay: 0.5 }}
                        >
                            <GlassInput
                                icon={<Mail className="w-5 h-5" />}
                                placeholder="fatih@ajans.com"
                                label="E-posta Adresi"
                                type="email"
                                required
                                value={formData.email}
                                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                            />
                        </motion.div>

                        <motion.div
                            initial={{ x: -20, opacity: 0 }}
                            animate={{ x: 0, opacity: 1 }}
                            transition={{ delay: 0.6 }}
                        >
                            <GlassInput
                                icon={<Lock className="w-5 h-5" />}
                                placeholder="••••••••"
                                label="Şifre"
                                type="password"
                                required
                                value={formData.password}
                                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                            />
                        </motion.div>

                        <motion.div
                            initial={{ y: 20, opacity: 0 }}
                            animate={{ y: 0, opacity: 1 }}
                            transition={{ delay: 0.7 }}
                            className="pt-4"
                        >
                            <GlassButton
                                type="submit"
                                className="w-full group"
                                size="lg"
                                isLoading={isLoading}
                            >
                                Kayıt Ol ve Başla
                                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                            </GlassButton>
                        </motion.div>
                    </form>

                    {/* Footer */}
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 0.9 }}
                        className="text-center mt-8 space-y-2"
                    >
                        <p className="text-sm text-gray-500">
                            Zaten hesabın var mı?{' '}
                            <Link href="/" className="text-primary-glow hover:text-white transition-colors font-medium">
                                Giriş Yap
                            </Link>
                        </p>
                        <p className="text-xs text-gray-600">
                            Todo Production v1.0.0 &copy; 2026
                        </p>
                    </motion.div>

                </GlassCard>
            </div>
        </main>
    );
}
