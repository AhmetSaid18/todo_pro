import { motion, HTMLMotionProps } from "framer-motion";
import { cn } from "@/lib/utils";
import React from "react";

interface GlassCardProps extends HTMLMotionProps<"div"> {
    children: React.ReactNode;
    variant?: "default" | "hover" | "neon";
    noPadding?: boolean;
}

export const GlassCard = ({
    children,
    className,
    variant = "default",
    noPadding = false,
    ...props
}: GlassCardProps) => {

    const variants = {
        default: "bg-glass-100 border-glass-border",
        hover: "bg-glass-100 border-glass-border hover:bg-glass-200 transition-colors duration-300",
        neon: "bg-glass-200 border-primary/30 shadow-[0_0_15px_rgba(109,40,217,0.1)]"
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
            className={cn(
                "relative overflow-hidden rounded-2xl border backdrop-blur-xl",
                variants[variant],
                noPadding ? "p-0" : "p-6",
                className
            )}
            {...props}
        >
            {/* Subtle Gradient Overlay */}
            <div className="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent pointer-events-none" />

            {/* Content */}
            <div className="relative z-10">
                {children}
            </div>
        </motion.div>
    );
};
