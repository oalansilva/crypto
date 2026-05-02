// src/components/ui/Input.tsx
import type { InputHTMLAttributes, ReactNode } from 'react'

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
    label?: string
    error?: string
    icon?: ReactNode
}

export function Input({
    label,
    error,
    icon,
    className = '',
    ...props
}: InputProps) {
    return (
        <div className="w-full">
            {label && (
                <label className="mb-2 block text-xs font-semibold uppercase tracking-[0.08em] text-[var(--text-muted)]">
                    {label}
                </label>
            )}
            <div className="relative">
                {icon && (
                    <div className="absolute left-4 top-1/2 -translate-y-1/2 text-[var(--text-muted)]">
                        {icon}
                    </div>
                )}
                <input
                    className={`input ${icon ? 'pl-12' : ''} ${error ? 'border-red-500 ring-2 ring-red-500/20 focus:border-red-500 focus:ring-red-500/20' : ''} ${className}`}
                    {...props}
                />
            </div>
            {error && (
                <p className="mt-1 text-xs text-red-400">{error}</p>
            )}
        </div>
    )
}
