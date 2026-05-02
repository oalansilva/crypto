import * as React from 'react'
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/lib/utils'

// Popover Context
type PopoverContextValue = {
  open: boolean
  onOpenChange: (open: boolean) => void
}

const PopoverContext = React.createContext<PopoverContextValue | null>(null)

function usePopoverContext() {
  const context = React.useContext(PopoverContext)
  if (!context) {
    throw new Error('Popover components must be used within Popover')
  }
  return context
}

// Popover Root
interface PopoverProps {
  open?: boolean
  onOpenChange?: (open: boolean) => void
  children: React.ReactNode
}

function Popover({ open, onOpenChange, children }: PopoverProps) {
  return (
    <PopoverContext.Provider value={{ open: !!open, onOpenChange: onOpenChange || (() => {}) }}>
      {children}
    </PopoverContext.Provider>
  )
}

// Popover Trigger
interface PopoverTriggerProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  asChild?: boolean
}

const PopoverTrigger = React.forwardRef<HTMLButtonElement, PopoverTriggerProps>(
  ({ className, children, asChild, ...props }, ref) => {
    const { onOpenChange } = usePopoverContext()
    const [isOpen, setIsOpen] = React.useState(false)

    const handleClick = () => {
      setIsOpen(!isOpen)
      onOpenChange(!isOpen)
    }

    return (
      <button
        type="button"
        ref={ref}
        className={cn('', className)}
        onClick={handleClick}
        aria-expanded={isOpen}
        {...props}
      >
        {children}
      </button>
    )
  }
)
PopoverTrigger.displayName = 'PopoverTrigger'

// Popover Content
interface PopoverContentProps extends React.HTMLAttributes<HTMLDivElement> {
  align?: 'start' | 'center' | 'end'
  sideOffset?: number
}

const PopoverContent = React.forwardRef<HTMLDivElement, PopoverContentProps>(
  ({ className, align = 'center', sideOffset = 4, children, ...props }, ref) => {
    const { open, onOpenChange } = usePopoverContext()

    if (!open) return null

    const alignClasses = {
      start: 'left-0',
      center: 'left-1/2 -translate-x-1/2',
      end: 'right-0',
    }

    return (
      <>
        {/* Backdrop */}
        <div 
          className="fixed inset-0 z-40" 
          onClick={() => onOpenChange(false)}
        />
        <div
          ref={ref}
          className={cn(
            'absolute z-50 min-w-[180px] rounded-xl border border-[var(--border-default)] bg-[var(--bg-elevated)] p-1 shadow-xl backdrop-blur-xl',
            alignClasses[align],
            'top-full',
            className
          )}
          style={{ marginTop: sideOffset }}
          onClick={(e) => e.stopPropagation()}
          {...props}
        >
          {children}
        </div>
      </>
    )
  }
)
PopoverContent.displayName = 'PopoverContent'

// Dropdown Menu
type DropdownMenuContextValue = {
  open: boolean
  onOpenChange: (open: boolean) => void
}

const DropdownMenuContext = React.createContext<DropdownMenuContextValue | null>(null)

function useDropdownMenuContext() {
  const context = React.useContext(DropdownMenuContext)
  if (!context) {
    throw new Error('DropdownMenu components must be used within DropdownMenu')
  }
  return context
}

// Dropdown Menu Root
interface DropdownMenuProps {
  open?: boolean
  onOpenChange?: (open: boolean) => void
  children: React.ReactNode
}

function DropdownMenu({ open, onOpenChange, children }: DropdownMenuProps) {
  return (
    <DropdownMenuContext.Provider value={{ open: !!open, onOpenChange: onOpenChange || (() => {}) }}>
      {children}
    </DropdownMenuContext.Provider>
  )
}

// Dropdown Menu Trigger
interface DropdownMenuTriggerProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {}

const DropdownMenuTrigger = React.forwardRef<HTMLButtonElement, DropdownMenuTriggerProps>(
  ({ className, children, ...props }, ref) => {
    const { onOpenChange } = useDropdownMenuContext()
    const [isOpen, setIsOpen] = React.useState(false)

    const handleClick = () => {
      setIsOpen(!isOpen)
      onOpenChange(!isOpen)
    }

    return (
      <button
        type="button"
        ref={ref}
        className={cn('', className)}
        onClick={handleClick}
        aria-expanded={isOpen}
        {...props}
      >
        {children}
      </button>
    )
  }
)
DropdownMenuTrigger.displayName = 'DropdownMenuTrigger'

// Dropdown Menu Content
interface DropdownMenuContentProps extends React.HTMLAttributes<HTMLDivElement> {
  align?: 'start' | 'center' | 'end'
  sideOffset?: number
}

const DropdownMenuContent = React.forwardRef<HTMLDivElement, DropdownMenuContentProps>(
  ({ className, align = 'center', sideOffset = 4, children, ...props }, ref) => {
    const { open, onOpenChange } = useDropdownMenuContext()

    if (!open) return null

    const alignClasses = {
      start: 'left-0',
      center: 'left-1/2 -translate-x-1/2',
      end: 'right-0',
    }

    return (
      <>
        <div className="fixed inset-0 z-40" onClick={() => onOpenChange(false)} />
        <div
          ref={ref}
          className={cn(
            'absolute z-50 min-w-[180px] rounded-xl border border-[var(--border-default)] bg-[var(--bg-elevated)] p-1 shadow-xl backdrop-blur-xl',
            alignClasses[align],
            'top-full',
            className
          )}
          style={{ marginTop: sideOffset }}
          onClick={(e) => e.stopPropagation()}
          {...props}
        >
          {children}
        </div>
      </>
    )
  }
)
DropdownMenuContent.displayName = 'DropdownMenuContent'

// Dropdown Menu Item
interface DropdownMenuItemProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  inset?: boolean
}

const DropdownMenuItem = React.forwardRef<HTMLButtonElement, DropdownMenuItemProps>(
  ({ className, inset, children, ...props }, ref) => {
    return (
      <button
        type="button"
        ref={ref}
        className={cn(
          'flex w-full cursor-pointer items-center rounded-md px-3 py-2 text-sm text-[var(--text-secondary)] transition-colors',
          'hover:bg-[var(--bg-input)] hover:text-[var(--text-primary)]',
          'focus:bg-[var(--bg-input)] focus:text-[var(--text-primary)] focus:outline-none',
          inset && 'pl-8',
          className
        )}
        {...props}
      >
        {children}
      </button>
    )
  }
)
DropdownMenuItem.displayName = 'DropdownMenuItem'

// Dropdown Menu Separator
interface DropdownMenuSeparatorProps extends React.HTMLAttributes<HTMLDivElement> {}

const DropdownMenuSeparator = React.forwardRef<HTMLDivElement, DropdownMenuSeparatorProps>(
  ({ className, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn('-mx-1 my-1 h-px bg-[var(--border-subtle)]', className)}
        {...props}
      />
    )
  }
)
DropdownMenuSeparator.displayName = 'DropdownMenuSeparator'

// Dropdown Menu Label
interface DropdownMenuLabelProps extends React.HTMLAttributes<HTMLDivElement> {
  inset?: boolean
}

const DropdownMenuLabel = React.forwardRef<HTMLDivElement, DropdownMenuLabelProps>(
  ({ className, inset, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          'px-3 py-2 text-xs font-semibold text-[var(--text-muted)] uppercase tracking-wider',
          inset && 'pl-8',
          className
        )}
        {...props}
      />
    )
  }
)
DropdownMenuLabel.displayName = 'DropdownMenuLabel'

// Custom Dropdown (Simple Select Replacement)
interface DropdownOption {
  value: string
  label: string
  icon?: React.ReactNode
}

interface DropdownProps {
  options: DropdownOption[]
  value: string
  onChange: (value: string) => void
  placeholder?: string
  disabled?: boolean
  className?: string
}

function Dropdown({ options, value, onChange, placeholder = 'Selecionar...', disabled, className }: DropdownProps) {
  const [isOpen, setIsOpen] = React.useState(false)
  const containerRef = React.useRef<HTMLDivElement>(null)

  const selectedOption = options.find((opt) => opt.value === value)

  React.useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  return (
    <div ref={containerRef} className={cn('relative', className)}>
      <button
        type="button"
        disabled={disabled}
        onClick={() => !disabled && setIsOpen(!isOpen)}
        className={cn(
          'flex h-9 min-w-[140px] items-center justify-between gap-2 rounded-md border border-[var(--border-default)] bg-[var(--bg-elevated)] px-3 text-sm transition-colors',
          'hover:bg-[var(--bg-input)] hover:border-[rgba(252,213,53,0.28)]',
          'focus:outline-none focus:ring-2 focus:ring-[rgba(59,130,246,0.24)]',
          'disabled:opacity-50 disabled:cursor-not-allowed',
          isOpen && 'border-[rgba(252,213,53,0.4)] ring-2 ring-[rgba(252,213,53,0.14)]'
        )}
      >
        <span className={cn('truncate', selectedOption ? 'text-[var(--text-primary)]' : 'text-[var(--text-muted)]')}>
          {selectedOption ? (
            <span className="flex items-center gap-2">
              {selectedOption.icon}
              {selectedOption.label}
            </span>
          ) : (
            placeholder
          )}
        </span>
        <ChevronDown className={cn('h-4 w-4 text-[var(--text-muted)] transition-transform', isOpen && 'rotate-180')} />
      </button>

      {isOpen && (
        <>
          <div className="fixed inset-0 z-40" onClick={() => setIsOpen(false)} />
          <div className="absolute z-50 mt-1 min-w-full rounded-xl border border-[var(--border-default)] bg-[var(--bg-elevated)] p-1 shadow-xl backdrop-blur-xl">
            {options.map((option) => (
              <button
                key={option.value}
                type="button"
                onClick={() => {
                  onChange(option.value)
                  setIsOpen(false)
                }}
                className={cn(
                  'flex w-full items-center gap-2 rounded-md px-3 py-2 text-sm transition-colors',
                  'hover:bg-[var(--bg-input)] hover:text-[var(--text-primary)]',
                  'focus:bg-[var(--bg-input)] focus:text-[var(--text-primary)] focus:outline-none',
                  option.value === value ? 'bg-[rgba(252,213,53,0.1)] text-[var(--text-primary)]' : 'text-[var(--text-secondary)]'
                )}
              >
                {option.icon}
                {option.label}
              </button>
            ))}
          </div>
        </>
      )}
    </div>
  )
}

// Chevron icons
const ChevronDown = ({ className }: { className?: string }) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    className={className}
  >
    <path d="m6 9 6 6 6-6" />
  </svg>
)

export {
  Popover,
  PopoverTrigger,
  PopoverContent,
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuLabel,
  Dropdown,
}
