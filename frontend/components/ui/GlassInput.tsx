import { cn } from "@/lib/utils";
import React from "react";

interface GlassInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
    icon?: React.ReactNode;
    label?: string;
    error?: string;
}

export const GlassInput = React.forwardRef<HTMLInputElement, GlassInputProps>(
    ({ className, icon, label, error, ...props }, ref) => {
        return (
            <div className="w-full space-y-2">
                {label && (
                    <label className="text-sm font-medium text-gray-400 ml-1">
                        {label}
                    </label>
                )}

                <div className="relative group">
                    {icon && (
                        <div className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 group-focus-within:text-primary transition-colors">
                            {icon}
                        </div>
                    )}

                    <input
                        ref={ref}
                        className={cn(
                            "w-full bg-glass-100 border border-glass-border rounded-xl px-4 py-3 text-white placeholder-gray-500 backdrop-blur-sm transition-all duration-300",
                            "focus:outline-none focus:border-primary/50 focus:ring-2 focus:ring-primary/20 focus:bg-glass-200",
                            icon && "pl-10",
                            error && "border-red-500/50 focus:border-red-500 focus:ring-red-500/20",
                            className
                        )}
                        {...props}
                    />
                </div>

                {error && (
                    <p className="text-xs text-red-400 ml-1 animate-pulse">{error}</p>
                )}
            </div>
        );
    }
);

GlassInput.displayName = "GlassInput";
