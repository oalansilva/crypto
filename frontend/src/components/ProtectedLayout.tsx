import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from '@/stores/authStore'

export function ProtectedLayout() {
  const { user, isLoading } = useAuth()

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[#07111a]">
        <div className="h-8 w-8 animate-spin rounded-full border-b-2 border-sky-400" />
      </div>
    )
  }

  if (!user) {
    return <Navigate to="/login" replace />
  }

  return <Outlet />
}
