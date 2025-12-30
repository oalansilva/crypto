// src/components/ui/Card.tsx
import { HTMLAttributes, ReactNode } from 'react'

interface CardProps extends HTMLAttributes<HTMLDivElement> {
    elevated?: boolean
    hoverable?: boolean
    children: ReactNode
}

export function Card({
    elevated = false,
    hoverable = true,
    className = '',
    children,
    ...props
}: CardProps) {
    const baseClasses = 'card'
    const elevatedClass = elevated ? 'card-elevated' : ''
    const hoverClass = hoverable ? '' : 'hover:bg-[rgba(255,255,255,0.03)] hover:border-[var(--border-subtle)]'

    return (
        <div
            className={`${baseClasses} ${elevatedClass} ${hoverClass} ${className}`}
            {...props}
        >
            {children}
        </div>
    )
}
