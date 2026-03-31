import { Navigate } from 'react-router-dom'
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
    return <Navigate to="/login" replace />
  }

  if (requireAdmin && !user.isAdmin) {
    return <Navigate to="/" replace />
  }

  return <>{children}</>
}
