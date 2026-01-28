'use client';

import { motion } from 'framer-motion';
import { GlassCard } from '@/components/ui/GlassCard';
import { GlassInput } from '@/components/ui/GlassInput';
import { GlassButton } from '@/components/ui/GlassButton';
import { Mail, Lock, ArrowRight, Zap, AlertTriangle } from 'lucide-react';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { authService } from '@/services/authService';

export default function LoginPage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      await authService.login(formData.email, formData.password);
      // Başarılı giriş -> Dashboard'a yönlendir
      router.push('/dashboard');
    } catch (err: any) {
      console.error("Login Error:", err);
      // Backend'den gelen hatayı göster
      setError(err.response?.data?.error || "Giriş başarısız. Lütfen bilgileri kontrol edin.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="relative min-h-screen w-full flex items-center justify-center overflow-hidden bg-[#050505]">

      {/* 🌌 Background Effects */}
      <div className="absolute inset-0 w-full h-full">
        {/* Animated Orbs */}
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

        {/* Grid Pattern Overlay */}
        <div className="absolute inset-0 bg-[url('/grid.svg')] opacity-[0.05] pointer-events-none" />
      </div>

      {/* 📦 Login Content */}
      <div className="relative z-10 w-full max-w-md px-6">
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
              transition={{ delay: 0.2 }}
              className="text-3xl font-bold text-white mb-2 tracking-tight"
            >
              Todo Production
            </motion.h1>
            <motion.p
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.3 }}
              className="text-gray-400"
            >
              Prodüksiyon yönetiminde yeni çağ
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
          <form onSubmit={handleLogin} className="space-y-6">
            <motion.div
              initial={{ x: -20, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              transition={{ delay: 0.4 }}
            >
              <GlassInput
                icon={<Mail className="w-5 h-5" />}
                placeholder="ornek@prod.com"
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
              transition={{ delay: 0.5 }}
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
              <div className="flex justify-end mt-2">
                <a href="#" className="text-xs text-primary-glow hover:text-white transition-colors">
                  Şifremi Unuttum?
                </a>
              </div>
            </motion.div>

            <motion.div
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.6 }}
              className="pt-2"
            >
              <GlassButton
                type="submit"
                className="w-full group"
                size="lg"
                isLoading={isLoading}
              >
                Giriş Yap
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </GlassButton>
            </motion.div>
          </form>

          {/* Footer */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.8 }}
            className="text-center mt-8 space-y-2"
          >
            <p className="text-sm text-gray-500">
              Hesabın yok mu?{' '}
              <Link href="/register" className="text-primary-glow hover:text-white transition-colors font-medium">
                Kayıt Ol
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
