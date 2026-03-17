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
            'absolute z-50 min-w-[180px] rounded-lg border border-white/10 bg-[rgba(20,28,45,0.95)] p-1 shadow-xl backdrop-blur-xl',
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
            'absolute z-50 min-w-[180px] rounded-lg border border-white/10 bg-[rgba(20,28,45,0.95)] p-1 shadow-xl backdrop-blur-xl',
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
          'flex w-full cursor-pointer items-center rounded-md px-3 py-2 text-sm text-white/80 transition-colors',
          'hover:bg-white/10 hover:text-white',
          'focus:bg-white/10 focus:text-white focus:outline-none',
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
        className={cn('-mx-1 my-1 h-px bg-white/10', className)}
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
          'px-3 py-2 text-xs font-semibold text-white/50 uppercase tracking-wider',
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
          'flex h-9 min-w-[140px] items-center justify-between gap-2 rounded-lg border border-white/10 bg-white/5 px-3 text-sm transition-colors',
          'hover:bg-white/10 hover:border-white/20',
          'focus:outline-none focus:ring-2 focus:ring-cyan-400/30',
          'disabled:opacity-50 disabled:cursor-not-allowed',
          isOpen && 'border-cyan-400/50 ring-2 ring-cyan-400/20'
        )}
      >
        <span className={cn('truncate', selectedOption ? 'text-gray-100' : 'text-gray-400')}>
          {selectedOption ? (
            <span className="flex items-center gap-2">
              {selectedOption.icon}
              {selectedOption.label}
            </span>
          ) : (
            placeholder
          )}
        </span>
        <ChevronDown className={cn('h-4 w-4 text-gray-400 transition-transform', isOpen && 'rotate-180')} />
      </button>

      {isOpen && (
        <>
          <div className="fixed inset-0 z-40" onClick={() => setIsOpen(false)} />
          <div className="absolute z-50 mt-1 min-w-full rounded-lg border border-white/10 bg-[rgba(20,28,45,0.95)] p-1 shadow-xl backdrop-blur-xl">
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
                  'hover:bg-white/10 hover:text-white',
                  'focus:bg-white/10 focus:text-white focus:outline-none',
                  option.value === value ? 'bg-white/10 text-white' : 'text-gray-300'
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
