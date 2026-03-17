import { useState, type ReactNode } from 'react'
import { ChevronLeft, ChevronRight } from 'lucide-react'
import { cn } from '@/lib/utils'

interface SidebarProps {
  children: ReactNode
  defaultCollapsed?: boolean
  collapsedWidth?: number
  expandedWidth?: number
  side?: 'left' | 'right'
}

export function Sidebar({
  children,
  defaultCollapsed = false,
  collapsedWidth = 64,
  expandedWidth = 240,
  side = 'left',
}: SidebarProps) {
  const [isCollapsed, setIsCollapsed] = useState(defaultCollapsed)

  const width = isCollapsed ? collapsedWidth : expandedWidth

  return (
    <aside
      className={cn(
        'relative flex flex-col border-white/10 bg-[rgba(10,15,30,0.5)] backdrop-blur-sm transition-all duration-300',
        side === 'left' ? 'border-r' : 'border-l'
      )}
      style={{ width, minWidth: width }}
    >
      {/* Toggle Button */}
      <button
        type="button"
        onClick={() => setIsCollapsed(!isCollapsed)}
        className={cn(
          'absolute top-4 z-10 flex h-6 w-6 items-center justify-center rounded-full border border-white/10 bg-[rgba(20,28,45,0.9)] text-white/70 transition-colors hover:bg-white/10 hover:text-white',
          side === 'left' ? '-right-3' : '-left-3'
        )}
        aria-label={isCollapsed ? 'Expandir sidebar' : 'Recolher sidebar'}
      >
        {isCollapsed ? (
          side === 'left' ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />
        ) : (
          side === 'left' ? <ChevronLeft className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />
        )}
      </button>

      {/* Content */}
      <div className={cn('flex-1 overflow-hidden transition-opacity duration-200', isCollapsed && 'opacity-0 pointer-events-none')}>
        {children}
      </div>

      {/* Collapsed state indicator */}
      {isCollapsed && (
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
          <div className="vertical-text text-xs text-white/30 font-medium">
            {side === 'left' ? '→' : '←'}
          </div>
        </div>
      )}
    </aside>
  )
}

// Sidebar Section
interface SidebarSectionProps {
  title?: string
  children: ReactNode
  className?: string
}

export function SidebarSection({ title, children, className }: SidebarSectionProps) {
  return (
    <div className={cn('p-3', className)}>
      {title && (
        <h3 className="mb-2 px-2 text-xs font-semibold uppercase tracking-wider text-white/40">
          {title}
        </h3>
      )}
      {children}
    </div>
  )
}

// Sidebar Item
interface SidebarItemProps {
  icon?: ReactNode
  label: string
  active?: boolean
  collapsed?: boolean
  onClick?: () => void
  badge?: string | number
}

export function SidebarItem({ icon, label, active, collapsed, onClick, badge }: SidebarItemProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        'flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all duration-200',
        'hover:bg-white/5',
        active
          ? 'bg-[rgba(138,166,255,0.15)] text-white border border-[rgba(138,166,255,0.3)]'
          : 'text-white/60 hover:text-white'
      )}
    >
      {icon && <span className="flex-shrink-0">{icon}</span>}
      {!collapsed && <span className="flex-1 truncate text-left">{label}</span>}
      {!collapsed && badge !== undefined && (
        <span className="flex-shrink-0 rounded-full bg-white/10 px-2 py-0.5 text-xs">
          {badge}
        </span>
      )}
    </button>
  )
}

// Sidebar Group (collapsible)
interface SidebarGroupProps {
  label: string
  icon?: ReactNode
  children: ReactNode
  defaultOpen?: boolean
}

export function SidebarGroup({ label, icon, children, defaultOpen = true }: SidebarGroupProps) {
  const [isOpen, setIsOpen] = useState(defaultOpen)

  return (
    <div className="mb-2">
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="flex w-full items-center gap-2 px-3 py-2 text-xs font-semibold uppercase tracking-wider text-white/40 hover:text-white/60 transition-colors"
      >
        {icon}
        <span className="flex-1 text-left">{label}</span>
        <ChevronRight className={cn('h-3 w-3 transition-transform', isOpen && 'rotate-90')} />
      </button>
      {isOpen && <div className="mt-1 space-y-0.5">{children}</div>}
    </div>
  )
}
