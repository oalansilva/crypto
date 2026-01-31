import { Outlet } from 'react-router-dom'
import { AppNav } from './AppNav'

export function Layout() {
  return (
    <div className="min-h-screen relative overflow-hidden bg-black text-white font-sans selection:bg-blue-500/30">
      <div className="fixed inset-0 -z-10 pointer-events-none">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl animate-float" />
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl animate-float" style={{ animationDelay: '2s' }} />
      </div>
      <AppNav />
      <Outlet />
    </div>
  )
}
