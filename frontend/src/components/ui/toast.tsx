import * as React from "react"
import { X } from "lucide-react"

// Simplified Toast Primitives without Radix UI
// Mimics the API structure for compatibility

type ToastProps = React.HTMLAttributes<HTMLDivElement> & {
    variant?: "default" | "destructive"
    open?: boolean
    onOpenChange?: (open: boolean) => void
}

const ToastContext = React.createContext<{}>({})

export const ToastProvider = ({ children }: { children: React.ReactNode }) => {
    return <ToastContext.Provider value={{}}>{children}</ToastContext.Provider>
}

export const ToastViewport = React.forwardRef<
    HTMLOListElement,
    React.HTMLAttributes<HTMLOListElement>
>(({ className = "", ...props }, ref) => (
    <ol
        ref={ref}
        className={`fixed left-1/2 top-4 z-[100] flex max-h-screen w-[calc(100vw-2rem)] -translate-x-1/2 flex-col gap-2 p-0 sm:top-5 md:max-w-[420px] ${className}`}
        {...props}
    />
))
ToastViewport.displayName = "ToastViewport"

export const Toast = React.forwardRef<HTMLDivElement, ToastProps>(
    ({ className = "", variant, open, onOpenChange, ...props }, ref) => {
        // Simple visibility handling. 
        // In real radix, this handles animations/portaling. 
        // Here we just render normally or use CSS classes.

        // If open is false, we don't render? wrapper handles mapping.

        return (
            <div
                ref={ref}
                role={variant === "destructive" ? "alert" : "status"}
                aria-live={variant === "destructive" ? "assertive" : "polite"}
                className={`group pointer-events-auto relative flex w-full items-start justify-between gap-4 overflow-hidden rounded-lg border p-4 pr-10 shadow-[0_20px_60px_rgba(0,0,0,0.38)] backdrop-blur transition-all
                ${variant === 'destructive'
                        ? 'destructive border-red-400/35 bg-[rgba(54,20,24,0.96)] text-red-50'
                        : 'border-emerald-300/30 bg-[rgba(12,22,34,0.98)] text-[var(--text-primary)]'}
                ${className}`}
                {...props}
            />
        )
    }
)
Toast.displayName = "Toast"

export const ToastAction = React.forwardRef<
    HTMLButtonElement,
    React.ButtonHTMLAttributes<HTMLButtonElement>
>(({ className, ...props }, ref) => (
    <button
        ref={ref}
        className={`inline-flex h-8 shrink-0 items-center justify-center rounded-md border bg-transparent px-3 text-sm font-medium ring-offset-background transition-colors hover:bg-secondary focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 group-[.destructive]:border-muted/40 group-[.destructive]:hover:border-destructive/30 group-[.destructive]:hover:bg-destructive group-[.destructive]:hover:text-destructive-foreground group-[.destructive]:focus:ring-destructive ${className}`}
        {...props}
    />
))
ToastAction.displayName = "ToastAction"

export const ToastClose = React.forwardRef<
    HTMLButtonElement,
    React.ButtonHTMLAttributes<HTMLButtonElement>
>(({ className, ...props }, ref) => (
    <button
        ref={ref}
        type="button"
        aria-label="Fechar notificação"
        className={`absolute right-2 top-2 rounded-md p-1 text-[var(--text-secondary)] opacity-80 transition hover:text-[var(--text-primary)] hover:opacity-100 focus:opacity-100 focus:outline-none focus:ring-2 focus:ring-emerald-300/50 group-[.destructive]:text-red-200 group-[.destructive]:hover:text-red-50 group-[.destructive]:focus:ring-red-400 ${className}`}
        toast-close=""
        {...props}
    >
        <X className="h-4 w-4" />
    </button>
))
ToastClose.displayName = "ToastClose"

export const ToastTitle = React.forwardRef<
    HTMLHeadingElement,
    React.HTMLAttributes<HTMLHeadingElement>
>(({ className, ...props }, ref) => (
    <div
        ref={ref}
        className={`text-sm font-semibold ${className}`}
        {...props}
    />
))
ToastTitle.displayName = "ToastTitle"

export const ToastDescription = React.forwardRef<
    HTMLParagraphElement,
    React.HTMLAttributes<HTMLParagraphElement>
>(({ className, ...props }, ref) => (
    <div
        ref={ref}
        className={`text-sm opacity-90 ${className}`}
        {...props}
    />
))
ToastDescription.displayName = "ToastDescription"  
