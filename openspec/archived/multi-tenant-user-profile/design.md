# Design — Card #71: [MT-3] Perfil de Usuário — Perfil, Alteração de Senha e Auditoria

## UX / UI

### Pages

Duas páginas novas:
1. **Meu Perfil** (`/profile`) — visualização e edição do perfil
2. **Alterar Senha** (`/change-password`) — alteração de senha

### Meu Perfil (`/profile`)

#### Layout
- Container centralizado (max-width: 480px)
- Card com: título, campos do formulário, botão salvar

#### Campos
| Campo | Tipo | Editável | Observação |
|-------|------|----------|------------|
| Nome | text input | Sim | Requerido, min 1 char |
| Email | text input | Não | Readonly, disabled |
| Último Login | text/label | Não | Formatado como data/hora |
| Membro desde | text/label | Não | createdAt formatado |

#### Estados
- **Loading**: Spinner centralizado enquanto busca dados
- **Error**: Toast de erro com mensagem
- **Success**: Toast de sucesso "Perfil atualizado"

#### Interações
- GET /api/users/me ao montar página
- PUT /api/users/me ao clicar "Salvar"
- Validação client-side: nome não pode ser vazio

---

### Alterar Senha (`/change-password`)

#### Layout
- Container centralizado (max-width: 480px)
- Card com: título, campos do formulário, botão alterar

#### Campos
| Campo | Tipo | Observação |
|-------|------|------------|
| Senha Atual | password input | Requerido |
| Nova Senha | password input | Requerido, min 8 chars |
| Confirmar Nova Senha | password input | Requerido, deve ser igual a Nova Senha |

#### Estados
- **Loading**: Spinner no botão enquanto aguarda resposta
- **Error**: Toast de erro (senha atual incorreta / validação)
- **Success**: Toast de sucesso "Senha alterada com sucesso"

#### Interações
- PUT /api/users/password ao clicar "Alterar Senha"
- Validação client-side: senhas devem coincidir, min 8 chars
- Limpar campos após sucesso

---

### Menu de Navegação (Header)

Adicionar items ao menu do usuário (dropdown do avatar/nome):

```
[Avatar/Nome ▾]
├── Meu Perfil      → /profile
├── Alterar Senha   → /change-password
├── ─────────────
└── Sair            → logout
```

---

## Component Inventory

### ProfilePage
- **States**: loading, ready, error
- **Layout**: centered card with form
- **Fields**: name (editable), email (readonly), lastLogin (readonly), createdAt (readonly)

### ChangePasswordPage
- **States**: loading, ready, error, success
- **Layout**: centered card with form
- **Fields**: currentPassword, newPassword, confirmPassword
- **Validation**: passwords match, min 8 chars

### UserMenu (dropdown)
- Existing component that needs new items added

---

## Technical Approach

### Backend
- New route file: `backend/app/routes/user_profile.py`
- Uses existing `get_current_user` dependency from auth middleware
- Uses existing `get_db` dependency
- Password change uses same bcrypt hashing as registration

### Frontend
- New pages: `frontend/src/pages/ProfilePage.tsx`, `frontend/src/pages/ChangePasswordPage.tsx`
- Use existing `useAuth()` hook for access token
- Use existing API_BASE from `@/lib/apiBase`
- Follow existing page patterns from other pages (e.g., SystemPreferencesPage)

### Routes
```
GET  /api/users/me
PUT  /api/users/me
PUT  /api/users/password
```

### Data Model
```python
class User(Base):
    # existing fields...
    last_login = Column(DateTime, nullable=True, default=None)
```

---

## Visual Design

### Colors / Theme
- Follow existing app theme (dark-green palette)
- Consistent with other pages (SystemPreferencesPage, etc.)

### Typography
- Same as other pages

### Spacing
- Consistent padding/margins with other pages
