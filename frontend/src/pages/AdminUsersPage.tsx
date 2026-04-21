import { useEffect, useMemo, useState, type FormEvent } from 'react'
import { AlertTriangle, Ban, RefreshCw, Save, Search, Timer, UserCog, UserPlus, Users, X } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { useToast } from '@/components/ui/use-toast'
import { API_BASE_URL } from '@/lib/apiBase'
import { authFetch } from '@/lib/authFetch'

type AdminUser = {
  id: string
  email: string
  name: string
  status: 'active' | 'suspended' | 'banned'
  isBanned: boolean
  suspendedUntil: string | null
  suspensionReason: string | null
  notes: string | null
  createdAt: string | null
  lastLogin: string | null
}

type AdminUsersResponse = {
  items: AdminUser[]
  total: number
  page: number
  pageSize: number
}

type AdminActionLog = {
  id: number
  actorUserId: string
  actorEmail: string | null
  targetUserId: string
  targetEmail: string | null
  action: string
  targetSubject: string | null
  reason: string
  metadata: Record<string, unknown> | null
  createdAt: string | null
}

type AdminActionLogResponse = {
  items: AdminActionLog[]
  total: number
  page: number
  pageSize: number
}

type FiltersState = {
  q: string
  status: string
  createdFrom: string
  createdTo: string
  lastLoginFrom: string
  lastLoginTo: string
}

type EditState = {
  id: string
  name: string
  status: 'active' | 'suspended' | 'banned'
  isBanned: boolean
  suspendedUntil: string
  suspensionReason: string
  notes: string
  reason: string
}

type CreateState = {
  email: string
  name: string
  password: string
  status: 'active' | 'suspended' | 'banned'
  isBanned: boolean
  suspendedUntil: string
  suspensionReason: string
  notes: string
  reason: string
}

const EMPTY_FILTERS: FiltersState = {
  q: '',
  status: '',
  createdFrom: '',
  createdTo: '',
  lastLoginFrom: '',
  lastLoginTo: '',
}

const EMPTY_EDIT: EditState = {
  id: '',
  name: '',
  status: 'active',
  isBanned: false,
  suspendedUntil: '',
  suspensionReason: '',
  notes: '',
  reason: '',
}

const EMPTY_CREATE: CreateState = {
  email: '',
  name: '',
  password: '',
  status: 'active',
  isBanned: false,
  suspendedUntil: '',
  suspensionReason: '',
  notes: '',
  reason: '',
}

function formatDate(value: string | null) {
  if (!value) return '—'
  const parsed = new Date(value)
  if (Number.isNaN(parsed.getTime())) return value
  return parsed.toLocaleString('pt-BR')
}

function toIsoOrNull(localValue: string) {
  if (!localValue.trim()) return null
  return new Date(localValue).toISOString()
}

function toLocalInputValue(isoValue: string | null) {
  if (!isoValue) return ''
  const value = new Date(isoValue)
  if (Number.isNaN(value.getTime())) return ''
  const offset = value.getTimezoneOffset() * 60000
  return new Date(value.getTime() - offset).toISOString().slice(0, 16)
}

function isActiveUserSuspended(user: AdminUser | null) {
  if (!user) return false
  if (user.status !== 'suspended') return false
  if (!user.suspendedUntil) return true
  return new Date(user.suspendedUntil).getTime() > Date.now()
}

async function readErrorMessage(response: Response, fallback: string) {
  const payload = await response.json().catch(() => null) as
    | { detail?: string | string[] }
    | null

  if (Array.isArray(payload?.detail)) {
    return payload.detail.join(', ')
  }

  if (typeof payload?.detail === 'string' && payload.detail.trim()) {
    return payload.detail
  }

  return fallback
}

export default function AdminUsersPage() {
  const { toast } = useToast()
  const [filters, setFilters] = useState<FiltersState>(EMPTY_FILTERS)
  const [appliedFilters, setAppliedFilters] = useState<FiltersState>(EMPTY_FILTERS)
  const [users, setUsers] = useState<AdminUser[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [pageSize] = useState(20)
  const [isLoading, setIsLoading] = useState(false)
  const [selectedUser, setSelectedUser] = useState<AdminUser | null>(null)
  const [editForm, setEditForm] = useState<EditState>(EMPTY_EDIT)
  const [createForm, setCreateForm] = useState<CreateState>(EMPTY_CREATE)
  const [logItems, setLogItems] = useState<AdminActionLog[]>([])
  const [isLogOpen, setIsLogOpen] = useState(false)

  const [suspendUntil, setSuspendUntil] = useState('')
  const [suspendReason, setSuspendReason] = useState('')
  const [banReason, setBanReason] = useState('')
  const [reactivateReason, setReactivateReason] = useState('')

  const totalPages = useMemo(() => Math.ceil(total / pageSize), [total, pageSize])

  const loadUsers = async () => {
    setIsLoading(true)
    try {
      const params = new URLSearchParams()
      if (appliedFilters.q) params.set('q', appliedFilters.q)
      if (appliedFilters.status) params.set('status', appliedFilters.status)
      const createdFromIso = toIsoOrNull(appliedFilters.createdFrom)
      const createdToIso = toIsoOrNull(appliedFilters.createdTo)
      const lastLoginFromIso = toIsoOrNull(appliedFilters.lastLoginFrom)
      const lastLoginToIso = toIsoOrNull(appliedFilters.lastLoginTo)
      if (createdFromIso) params.set('createdFrom', createdFromIso)
      if (createdToIso) params.set('createdTo', createdToIso)
      if (lastLoginFromIso) params.set('lastLoginFrom', lastLoginFromIso)
      if (lastLoginToIso) params.set('lastLoginTo', lastLoginToIso)
      params.set('page', String(page))
      params.set('pageSize', String(pageSize))

      const response = await authFetch(`${API_BASE_URL}/admin/users?${params.toString()}`)
      if (!response.ok) {
        throw new Error(await readErrorMessage(response, `Falha ao carregar usuários (${response.status})`))
      }
      const payload = (await response.json()) as AdminUsersResponse
      setUsers(payload.items)
      setTotal(payload.total)
    } catch (error: unknown) {
      toast({
        variant: 'destructive',
        title: 'Falha ao carregar usuários',
        description: error instanceof Error ? error.message : 'Erro inesperado',
      })
    } finally {
      setIsLoading(false)
    }
  }

  const loadUserActions = async (userId: string) => {
    try {
      const response = await authFetch(`${API_BASE_URL}/admin/user-actions?targetUserId=${userId}&page=1&pageSize=20`)
      if (!response.ok) {
        throw new Error(await readErrorMessage(response, `Falha ao carregar logs (${response.status})`))
      }
      const payload = (await response.json()) as AdminActionLogResponse
      setLogItems(payload.items)
    } catch (error: unknown) {
      toast({
        variant: 'destructive',
        title: 'Falha ao carregar logs',
        description: error instanceof Error ? error.message : 'Erro inesperado',
      })
    }
  }

  useEffect(() => {
    loadUsers()
  }, [appliedFilters, page])

  const resetPanels = () => {
    setSelectedUser(null)
    setEditForm(EMPTY_EDIT)
    setLogItems([])
    setIsLogOpen(false)
    setSuspendUntil('')
    setSuspendReason('')
    setBanReason('')
    setReactivateReason('')
  }

  const handleApplyFilters = (event?: FormEvent) => {
    event?.preventDefault()
    setPage(1)
    setAppliedFilters(filters)
  }

  const handleClearFilters = () => {
    setFilters(EMPTY_FILTERS)
    setAppliedFilters(EMPTY_FILTERS)
    setPage(1)
    resetPanels()
  }

  const openEdit = (user: AdminUser) => {
    setSelectedUser(user)
    setIsLogOpen(true)
    setEditForm({
      id: user.id,
      name: user.name,
      status: user.status,
      isBanned: user.isBanned,
      suspendedUntil: toLocalInputValue(user.suspendedUntil),
      suspensionReason: user.suspensionReason || '',
      notes: user.notes || '',
      reason: '',
    })
    loadUserActions(user.id)
  }

  const clearSelection = () => {
    setSelectedUser(null)
    setEditForm(EMPTY_EDIT)
    setLogItems([])
    setIsLogOpen(false)
  }

  const submitCreate = async (event: FormEvent) => {
    event.preventDefault()
    const trimmedName = createForm.name.trim()
    const trimmedEmail = createForm.email.trim()
    const trimmedPassword = createForm.password

    if (!trimmedName) {
      throw new Error('Informe o nome do usuário.')
    }

    if (!trimmedEmail) {
      throw new Error('Informe o e-mail do usuário.')
    }

    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(trimmedEmail)) {
      throw new Error('Informe um e-mail válido.')
    }

    if (!trimmedPassword || trimmedPassword.length < 8) {
      throw new Error('A senha inicial deve ter pelo menos 8 caracteres.')
    }

    if (createForm.status === 'suspended' && !createForm.suspendedUntil) {
      throw new Error('Informe até quando a suspensão ficará ativa.')
    }

    const response = await authFetch(`${API_BASE_URL}/admin/users`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: trimmedEmail,
        name: trimmedName,
        password: trimmedPassword,
        status: createForm.status,
        isBanned: createForm.isBanned,
        suspendedUntil: createForm.suspendedUntil ? toIsoOrNull(createForm.suspendedUntil) : undefined,
        suspensionReason: createForm.suspensionReason || undefined,
        notes: createForm.notes || undefined,
        reason: createForm.reason || undefined,
      }),
    })
    if (!response.ok) {
      throw new Error(await readErrorMessage(response, `Falha ao criar usuário (${response.status})`))
    }
    setCreateForm(EMPTY_CREATE)
    toast({
      title: 'Usuário criado',
      description: 'Usuário inserido com sucesso para suporte.',
    })
    await loadUsers()
  }

  const submitCreateWrapped = async (event: FormEvent) => {
    try {
      await submitCreate(event)
    } catch (error: unknown) {
      toast({
        variant: 'destructive',
        title: 'Falha ao criar usuário',
        description: error instanceof Error ? error.message : 'Erro inesperado',
      })
    }
  }

  const submitUpdate = async (event: FormEvent) => {
    event.preventDefault()
    if (!editForm.id) return

    const reason = editForm.reason.trim()
    if (!reason) {
      toast({
        variant: 'destructive',
        title: 'Motivo obrigatório',
        description: 'Informe o motivo da alteração.',
      })
      return
    }

    const response = await authFetch(`${API_BASE_URL}/admin/users/${editForm.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: editForm.name.trim(),
        status: editForm.status,
        isBanned: editForm.isBanned,
        suspendedUntil: editForm.suspendedUntil ? toIsoOrNull(editForm.suspendedUntil) : undefined,
        suspensionReason: editForm.suspensionReason || undefined,
        notes: editForm.notes || undefined,
        reason,
      }),
    })
    if (!response.ok) {
      throw new Error(await readErrorMessage(response, `Falha ao atualizar usuário (${response.status})`))
    }
    const updated = (await response.json()) as AdminUser
    setUsers((rows) => rows.map((row) => (row.id === updated.id ? updated : row)))
    setSelectedUser(updated)
    toast({
      title: 'Usuário atualizado',
      description: 'Os dados do usuário foram alterados.',
    })
    await loadUserActions(updated.id)
    await loadUsers()
  }

  const submitUpdateWrapped = async (event: FormEvent) => {
    try {
      await submitUpdate(event)
    } catch (error: unknown) {
      toast({
        variant: 'destructive',
        title: 'Falha ao salvar',
        description: error instanceof Error ? error.message : 'Erro inesperado',
      })
    }
  }

  const submitSuspend = async () => {
    if (!selectedUser) return
    if (!suspendReason.trim() || !suspendUntil) {
      toast({
        variant: 'destructive',
        title: 'Campos obrigatórios',
        description: 'Informe motivo e até quando a suspensão vale.',
      })
      return
    }
    try {
      const response = await authFetch(`${API_BASE_URL}/admin/users/${selectedUser.id}/suspend`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          reason: suspendReason,
          suspendedUntil: toIsoOrNull(suspendUntil),
        }),
      })
      if (!response.ok) {
        throw new Error(await readErrorMessage(response, `Falha ao suspender usuário (${response.status})`))
      }
      const updated = (await response.json()) as AdminUser
      setUsers((rows) => rows.map((row) => (row.id === updated.id ? updated : row)))
      setSelectedUser(updated)
      setSuspendUntil('')
      setSuspendReason('')
      toast({
        title: 'Usuário suspenso',
        description: `${updated.name} foi suspenso até ${formatDate(updated.suspendedUntil)}`,
      })
      await loadUsers()
      await loadUserActions(updated.id)
    } catch (error: unknown) {
      toast({
        variant: 'destructive',
        title: 'Falha ao suspender',
        description: error instanceof Error ? error.message : 'Erro inesperado',
      })
    }
  }

  const submitBan = async () => {
    if (!selectedUser) return
    if (!banReason.trim()) {
      toast({
        variant: 'destructive',
        title: 'Motivo obrigatório',
        description: 'Informe o motivo do banimento.',
      })
      return
    }
    try {
      const response = await authFetch(`${API_BASE_URL}/admin/users/${selectedUser.id}/ban`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reason: banReason }),
      })
      if (!response.ok) {
        throw new Error(await readErrorMessage(response, `Falha ao banir usuário (${response.status})`))
      }
      const updated = (await response.json()) as AdminUser
      setUsers((rows) => rows.map((row) => (row.id === updated.id ? updated : row)))
      setSelectedUser(updated)
      setBanReason('')
      toast({
        title: 'Usuário banido',
        description: `${updated.email} foi bloqueado.`,
      })
      await loadUsers()
      await loadUserActions(updated.id)
    } catch (error: unknown) {
      toast({
        variant: 'destructive',
        title: 'Falha ao banir',
        description: error instanceof Error ? error.message : 'Erro inesperado',
      })
    }
  }

  const submitReactivate = async () => {
    if (!selectedUser) return
    if (!reactivateReason.trim()) {
      toast({
        variant: 'destructive',
        title: 'Motivo obrigatório',
        description: 'Informe o motivo da reativação.',
      })
      return
    }
    try {
      const response = await authFetch(`${API_BASE_URL}/admin/users/${selectedUser.id}/reactivate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reason: reactivateReason }),
      })
      if (!response.ok) {
        throw new Error(await readErrorMessage(response, `Falha ao reativar usuário (${response.status})`))
      }
      const updated = (await response.json()) as AdminUser
      setUsers((rows) => rows.map((row) => (row.id === updated.id ? updated : row)))
      setSelectedUser(updated)
      setReactivateReason('')
      toast({
        title: 'Usuário reativado',
        description: `${updated.name} voltou ao estado ativo.`,
      })
      await loadUsers()
      await loadUserActions(updated.id)
    } catch (error: unknown) {
      toast({
        variant: 'destructive',
        title: 'Falha ao reativar',
        description: error instanceof Error ? error.message : 'Erro inesperado',
      })
    }
  }

  return (
    <div className="app-page space-y-6 pb-20">
      <section className="page-card p-6 sm:p-7 lg:p-8">
        <div className="flex items-start gap-4">
          <div className="flex h-14 w-14 items-center justify-center rounded-3xl border border-emerald-300/20 bg-[linear-gradient(135deg,rgba(16,185,129,0.22),rgba(56,189,248,0.18))]">
            <Users className="h-6 w-6 text-emerald-100" />
          </div>
          <div>
            <div className="eyebrow">
              <span>Admin</span>
            </div>
            <h1 className="section-title mt-2">Painel de usuários</h1>
            <p className="section-copy mt-2">
              Gestão de contas para suporte: busca, filtros, ações administrativas e trilha de auditoria.
            </p>
          </div>
        </div>
      </section>

      <Card className="page-card border-white/8 bg-[linear-gradient(180deg,rgba(16,28,42,0.98),rgba(12,22,34,0.94))]">
        <CardContent className="p-6 space-y-4">
          <div className="text-sm font-semibold text-[var(--text-primary)]">Novo usuário</div>
          <form onSubmit={submitCreateWrapped} className="grid gap-4 md:grid-cols-2 xl:grid-cols-6">
            <Input
              label="Nome"
              value={createForm.name}
              placeholder="Nome"
              onChange={(event) => setCreateForm((prev) => ({ ...prev, name: event.target.value }))}
              required
            />
            <Input
              label="E-mail"
              type="email"
              value={createForm.email}
              placeholder="email@dominio.com"
              onChange={(event) => setCreateForm((prev) => ({ ...prev, email: event.target.value }))}
              required
            />
            <Input
              label="Senha inicial"
              type="password"
              value={createForm.password}
              placeholder="Mínimo 8 caracteres"
              onChange={(event) => setCreateForm((prev) => ({ ...prev, password: event.target.value }))}
              required
            />
            <div className="space-y-2">
              <label className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">Status</label>
              <select
                value={createForm.status}
                onChange={(event) =>
                  setCreateForm((prev) => ({ ...prev, status: event.target.value as CreateState['status'] }))
                }
                className="w-full rounded-xl border border-[var(--border-default)] bg-[var(--bg-input)] px-3 py-3 text-sm text-[var(--text-primary)]"
              >
                <option value="active">Ativo</option>
                <option value="suspended">Suspenso</option>
                <option value="banned">Banido</option>
              </select>
            </div>
            <div className="flex items-start gap-2 pt-6">
              <input
                id="create-is-banned"
                type="checkbox"
                checked={createForm.isBanned}
                onChange={(event) => setCreateForm((prev) => ({ ...prev, isBanned: event.target.checked }))}
                className="mt-1"
              />
              <label htmlFor="create-is-banned" className="text-sm text-[var(--text-secondary)]">
                Forçar banimento
              </label>
            </div>
            <div className="md:col-span-2">
              <Input
                label="Motivo (opcional)"
                value={createForm.reason}
                onChange={(event) => setCreateForm((prev) => ({ ...prev, reason: event.target.value }))}
                placeholder="Motivo interno"
              />
            </div>
            {createForm.status === 'suspended' ? (
              <>
                <Input
                  label="Suspender até"
                  type="datetime-local"
                  value={createForm.suspendedUntil}
                  onChange={(event) => setCreateForm((prev) => ({ ...prev, suspendedUntil: event.target.value }))}
                  required
                />
                <Input
                  label="Razão da suspensão"
                  value={createForm.suspensionReason}
                  onChange={(event) =>
                    setCreateForm((prev) => ({ ...prev, suspensionReason: event.target.value }))
                  }
                  placeholder="Motivo da suspensão"
                />
              </>
            ) : null}
            <div className="md:col-span-2">
              <label className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">
                Observações
              </label>
              <textarea
                value={createForm.notes}
                onChange={(event) => setCreateForm((prev) => ({ ...prev, notes: event.target.value }))}
                rows={3}
                className="mt-2 w-full rounded-xl border border-[var(--border-default)] bg-[var(--bg-input)] px-3 py-2 text-sm text-[var(--text-primary)]"
                placeholder="Observações internas"
              />
            </div>
            <div className="md:col-span-2 xl:col-span-2">
              <Button type="submit" icon={<UserPlus className="h-4 w-4" />}>
                Criar usuário
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      <Card className="page-card border-white/8 bg-[linear-gradient(180deg,rgba(16,28,42,0.98),rgba(12,22,34,0.94))]">
        <CardContent className="p-6 space-y-4">
          <div className="flex items-start justify-between gap-3">
            <div>
              <div className="text-sm font-semibold text-[var(--text-primary)]">Busca e filtros</div>
              <p className="mt-1 text-sm text-[var(--text-tertiary)]">Use palavras-chave e janelas de tempo para localizar usuários rapidamente.</p>
            </div>
          </div>
          <form onSubmit={handleApplyFilters} className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
            <Input
              label="Busca (nome ou e-mail)"
              value={filters.q}
              onChange={(event) => setFilters((prev) => ({ ...prev, q: event.target.value }))}
              icon={<Search className="h-4 w-4" />}
              placeholder="Digite parte do nome ou e-mail"
            />
            <div className="space-y-2">
              <label className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">Status</label>
              <select
                value={filters.status}
                onChange={(event) => setFilters((prev) => ({ ...prev, status: event.target.value }))}
                className="w-full rounded-xl border border-[var(--border-default)] bg-[var(--bg-input)] px-3 py-3 text-sm text-[var(--text-primary)]"
              >
                <option value="">Todos</option>
                <option value="active">Ativo</option>
                <option value="suspended">Suspenso</option>
                <option value="banned">Banido</option>
              </select>
            </div>
            <Input
              label="Criado em (de)"
              type="datetime-local"
              value={filters.createdFrom}
              onChange={(event) => setFilters((prev) => ({ ...prev, createdFrom: event.target.value }))}
            />
            <Input
              label="Criado em (até)"
              type="datetime-local"
              value={filters.createdTo}
              onChange={(event) => setFilters((prev) => ({ ...prev, createdTo: event.target.value }))}
            />
            <Input
              label="Último login (de)"
              type="datetime-local"
              value={filters.lastLoginFrom}
              onChange={(event) => setFilters((prev) => ({ ...prev, lastLoginFrom: event.target.value }))}
            />
            <Input
              label="Último login (até)"
              type="datetime-local"
              value={filters.lastLoginTo}
              onChange={(event) => setFilters((prev) => ({ ...prev, lastLoginTo: event.target.value }))}
            />
          </form>
          <div className="mt-2 flex flex-wrap items-center gap-2">
            <Button type="button" onClick={handleApplyFilters}>
              Aplicar filtros
            </Button>
            <Button type="button" variant="ghost" onClick={handleClearFilters}>
              Limpar filtros
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card className="page-card border-white/8 bg-[linear-gradient(180deg,rgba(16,28,42,0.98),rgba(12,22,34,0.94))]">
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm font-semibold text-[var(--text-primary)]">Usuários</div>
              <p className="mt-1 text-sm text-[var(--text-tertiary)]">
                {isLoading ? 'Carregando...' : `${total} resultado(s)`}
              </p>
            </div>
            <Button variant="ghost" size="sm" onClick={resetPanels}>
              Recarregar
            </Button>
          </div>

          <div className="mt-4 overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-white/10 text-left text-[var(--text-muted)]">
                  <th className="py-2 pr-3">E-mail</th>
                  <th className="py-2 pr-3">Nome</th>
                  <th className="py-2 pr-3">Status</th>
                  <th className="py-2 pr-3">Último login</th>
                  <th className="py-2 pr-3">Criado</th>
                  <th className="py-2 pr-3">Ações</th>
                </tr>
              </thead>
              <tbody>
                {users.map((user) => {
                  const suspended = isActiveUserSuspended(user)
                  const selected = selectedUser?.id === user.id
                  const statusClasses =
                    user.status === 'active'
                      ? 'text-emerald-300 bg-emerald-500/12 border-emerald-400/40'
                      : user.status === 'suspended'
                        ? 'text-amber-300 bg-amber-500/12 border-amber-400/40'
                        : 'text-rose-300 bg-rose-500/12 border-rose-400/40'

                  return (
                    <tr key={user.id} className={`border-b border-white/8 ${selected ? 'bg-white/[0.04]' : ''}`}>
                      <td className="py-3 pr-3">{user.email}</td>
                      <td className="py-3 pr-3">{user.name}</td>
                      <td className="py-3 pr-3">
                        <span className={`inline-flex items-center rounded-full border px-2 py-1 text-[11px] font-semibold ${statusClasses}`}>
                          {user.status}
                          {suspended ? ' (ativo no limite)' : ''}
                        </span>
                      </td>
                      <td className="py-3 pr-3">{formatDate(user.lastLogin)}</td>
                      <td className="py-3 pr-3">{formatDate(user.createdAt)}</td>
                      <td className="py-3">
                        <div className="flex flex-wrap gap-2">
                          <Button size="sm" onClick={() => openEdit(user)}>
                            <UserCog className="h-3.5 w-3.5" />
                          </Button>
                          {user.status !== 'banned' ? (
                            <Button size="sm" variant="ghost" onClick={() => {
                              openEdit(user)
                              setBanReason('')
                              setSuspendReason('')
                              setReactivateReason('')
                            }}>
                              <Ban className="h-3.5 w-3.5" />
                            </Button>
                          ) : null}
                        </div>
                      </td>
                    </tr>
                  )
                })}
                {users.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="py-8 text-[var(--text-tertiary)]">Nenhum usuário encontrado.</td>
                  </tr>
                ) : null}
              </tbody>
            </table>
          </div>

          <div className="mt-4 flex items-center justify-between text-sm text-[var(--text-tertiary)]">
            <div>
              Página {page} de {Math.max(totalPages, 1)}
            </div>
            <div className="flex gap-2">
              <Button size="sm" variant="ghost" disabled={page <= 1} onClick={() => setPage((value) => Math.max(1, value - 1))}>
                Anterior
              </Button>
              <Button
                size="sm"
                variant="ghost"
                disabled={page >= totalPages || total === 0}
                onClick={() => setPage((value) => value + 1)}
              >
                Próxima
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {selectedUser ? (
        <Card className="page-card border-white/8 bg-[linear-gradient(180deg,rgba(16,28,42,0.98),rgba(12,22,34,0.94))]">
          <CardContent className="p-6 space-y-6">
            <div className="flex items-start justify-between gap-3">
              <div>
                <div className="text-sm font-semibold text-[var(--text-primary)]">Editar usuário</div>
                <p className="mt-1 text-sm text-[var(--text-tertiary)]">{selectedUser.email}</p>
              </div>
              <button type="button" onClick={clearSelection} className="text-xs text-[var(--text-muted)] hover:text-white">
                <X className="h-4 w-4" />
              </button>
            </div>

            <form onSubmit={submitUpdateWrapped} className="grid gap-4 md:grid-cols-2">
              <Input
                label="Nome"
                value={editForm.name}
                onChange={(event) => setEditForm((prev) => ({ ...prev, name: event.target.value }))}
                required
              />
              <div className="space-y-2">
                <label className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">Status</label>
                <select
                  value={editForm.status}
                  onChange={(event) =>
                    setEditForm((prev) => ({ ...prev, status: event.target.value as EditState['status'] }))
                  }
                  className="w-full rounded-xl border border-[var(--border-default)] bg-[var(--bg-input)] px-3 py-3 text-sm text-[var(--text-primary)]"
                >
                  <option value="active">Ativo</option>
                  <option value="suspended">Suspenso</option>
                  <option value="banned">Banido</option>
                </select>
              </div>
              <div className="space-y-2">
                <label className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">Suspensão até</label>
                <input
                  type="datetime-local"
                  value={editForm.suspendedUntil}
                  onChange={(event) => setEditForm((prev) => ({ ...prev, suspendedUntil: event.target.value }))}
                  className="w-full rounded-xl border border-[var(--border-default)] bg-[var(--bg-input)] px-3 py-3 text-sm text-[var(--text-primary)]"
                />
              </div>
              <Input
                label="Razão da suspensão"
                value={editForm.suspensionReason}
                onChange={(event) => setEditForm((prev) => ({ ...prev, suspensionReason: event.target.value }))}
              />
              <div className="col-span-2 space-y-2">
                <label className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">Observações</label>
                <textarea
                  value={editForm.notes}
                  onChange={(event) => setEditForm((prev) => ({ ...prev, notes: event.target.value }))}
                  rows={3}
                  className="w-full rounded-xl border border-[var(--border-default)] bg-[var(--bg-input)] px-3 py-2 text-sm text-[var(--text-primary)]"
                />
              </div>
              <Input
                label="Motivo da alteração"
                value={editForm.reason}
                onChange={(event) => setEditForm((prev) => ({ ...prev, reason: event.target.value }))}
                required
              />
              <div className="col-span-2 flex flex-wrap items-center gap-2">
                <Button type="submit" icon={<Save className="h-4 w-4" />}>Salvar alterações</Button>
                {editForm.status === 'suspended' || isActiveUserSuspended(selectedUser) ? null : (
                  <>
                    <Button
                      type="button"
                      variant="ghost"
                      icon={<Timer className="h-4 w-4" />}
                      onClick={() => setIsLogOpen((value) => !value)}
                    >
                      Log de ações
                    </Button>
                  </>
                )}
                <Button type="button" variant="ghost" onClick={submitSuspend} icon={<AlertTriangle className="h-4 w-4" />}>
                  Suspender
                </Button>
                <Button type="button" variant="secondary" onClick={submitBan} icon={<Ban className="h-4 w-4" />}>
                  Banir
                </Button>
              </div>
            </form>

            <div className="grid gap-3 lg:grid-cols-3">
              <Input
                label="Suspender até"
                type="datetime-local"
                value={suspendUntil}
                onChange={(event) => setSuspendUntil(event.target.value)}
              />
              <Input
                label="Motivo da suspensão"
                value={suspendReason}
                onChange={(event) => setSuspendReason(event.target.value)}
              />
              <div className="self-end">
                <Button type="button" size="sm" onClick={submitSuspend}>
                  Aplicar suspensão
                </Button>
              </div>
            </div>

            <div className="grid gap-3 lg:grid-cols-3">
              <Input
                label="Motivo do banimento"
                value={banReason}
                onChange={(event) => setBanReason(event.target.value)}
              />
              <div className="self-end">
                <Button type="button" size="sm" variant="secondary" onClick={submitBan}>
                  Aplicar banimento
                </Button>
              </div>
              <div />
            </div>

            <div className="grid gap-3 lg:grid-cols-3">
              <Input
                label="Motivo da reativação"
                value={reactivateReason}
                onChange={(event) => setReactivateReason(event.target.value)}
              />
              <div className="self-end">
                <Button
                  type="button"
                  size="sm"
                  icon={<RefreshCw className="h-4 w-4" />}
                  onClick={submitReactivate}
                >
                  Reativar
                </Button>
              </div>
              <div />
            </div>

            {isLogOpen ? (
              <div className="space-y-3">
                <div className="text-sm font-semibold text-[var(--text-primary)]">Ações recentes</div>
                <div className="divide-y divide-white/10 rounded-xl border border-white/10 bg-[rgba(4,13,25,0.5)] p-3">
                  {logItems.length === 0 ? (
                    <div className="py-4 text-sm text-[var(--text-tertiary)]">Sem histórico recente.</div>
                  ) : (
                    logItems.map((entry) => (
                      <div key={entry.id} className="py-3 text-sm">
                        <div className="flex items-center justify-between gap-2">
                          <span className="font-semibold text-[var(--text-primary)]">{entry.action}</span>
                          <span className="text-[var(--text-muted)]">{formatDate(entry.createdAt)}</span>
                        </div>
                        <div className="mt-1 text-[var(--text-secondary)]">
                          Operador: {entry.actorEmail || entry.actorUserId}
                        </div>
                        <div className="text-[var(--text-tertiary)]">
                          Motivo: {entry.reason}
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            ) : null}
          </CardContent>
        </Card>
      ) : null}
    </div>
  )
}
