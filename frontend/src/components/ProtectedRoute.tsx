import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '@/stores/authStore'

interface ProtectedRouteProps {
  children: React.ReactNode
  requireAdmin?: boolean
}

/**
 * Protege rotas que requerem autenticação.
 * Redireciona para /login se o usuário não estiver autenticado.
 */
export function ProtectedRoute({ children, requireAdmin = false }: ProtectedRouteProps) {
  const { user, isLoading } = useAuth()
  const location = useLocation()

  // Enquanto valida token, mostra loading
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-sky-400" />
      </div>
    )
  }

  // Não autenticado → redireciona para login
  if (!user) {
    return <Navigate to="/login" replace state={{ returnTo: location.pathname }} />
  }

  if (requireAdmin && !user.isAdmin) {
    return <Navigate to="/monitor" replace />
  }

  return <>{children}</>
}
