import { motion, HTMLMotionProps } from "framer-motion";
import { cn } from "@/lib/utils";
import React from "react";
import { Loader2 } from "lucide-react";

interface GlassButtonProps extends HTMLMotionProps<"button"> {
    children: React.ReactNode;
    variant?: "primary" | "secondary" | "danger" | "ghost";
    size?: "sm" | "md" | "lg";
    isLoading?: boolean;
}

export const GlassButton = ({
    children,
    className,
    variant = "primary",
    size = "md",
    isLoading = false,
    disabled,
    ...props
}: GlassButtonProps) => {

    const variants = {
        primary: "bg-primary text-white border-transparent hover:bg-primary-glow shadow-[0_4px_14px_0_rgba(109,40,217,0.39)] hover:shadow-[0_6px_20px_rgba(109,40,217,0.23)]",
        secondary: "bg-glass-100 text-white border-glass-border hover:bg-glass-200 hover:border-white/20",
        danger: "bg-red-500/10 text-red-500 border-red-500/20 hover:bg-red-500/20",
        ghost: "bg-transparent text-gray-400 hover:text-white hover:bg-white/5 border-transparent"
    };

    const sizes = {
        sm: "px-3 py-1.5 text-sm",
        md: "px-6 py-2.5 text-base",
        lg: "px-8 py-3.5 text-lg"
    };

    return (
        <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className={cn(
                "relative rounded-xl font-medium border backdrop-blur-md flex items-center justify-center gap-2 transition-all duration-300",
                variants[variant],
                sizes[size],
                (isLoading || disabled) && "opacity-50 cursor-not-allowed",
                className
            )}
            disabled={isLoading || disabled}
            {...props}
        >
            {isLoading && <Loader2 className="w-4 h-4 animate-spin" />}
            {children}
        </motion.button>
    );
};
