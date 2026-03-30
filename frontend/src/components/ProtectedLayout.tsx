import { Navigate } from 'react-router-dom'
import { Layout } from './Layout'
import { useAuth } from '@/stores/authStore'

/**
 * Layout protegido por autenticação.
 * Redireciona para /login se o usuário não estiver autenticado.
 */
export function ProtectedLayout() {
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

  // Autenticado → renderiza o Layout normal
  return <Layout />
}
