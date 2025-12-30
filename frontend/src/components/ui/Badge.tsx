// src/components/ui/Badge.tsx
import { HTMLAttributes, ReactNode } from 'react'

interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
    variant?: 'primary' | 'success' | 'warning' | 'danger'
    children: ReactNode
}

export function Badge({
    variant = 'primary',
    className = '',
    children,
    ...props
}: BadgeProps) {
    const baseClasses = 'badge'
    const variantClasses = {
        primary: 'badge-primary',
        success: 'badge-success',
        warning: 'badge-warning',
        danger: 'badge-danger'
    }

    return (
        <span
            className={`${baseClasses} ${variantClasses[variant]} ${className}`}
            {...props}
        >
            {children}
        </span>
    )
}
