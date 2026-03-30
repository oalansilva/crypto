# Design — Card #69: [MT-1] Autenticação — Login, Registro e JWT

## UX / UI

### Endpoints REST

| Método | Path | Descrição | Auth |
|--------|------|-----------|------|
| POST | /auth/register | Criar conta | Não |
| POST | /auth/login | Login | Não |
| POST | /auth/logout | Logout | Não |
| POST | /auth/refresh | Renovar access token | Não (refresh token) |

### Fluxos

#### Registro
```
Usuário → POST /auth/register {email, password}
        ← 201 {id, email} (senha não retornada)
        [Erro 400 se email inválido ou já existe]
```

#### Login
```
Usuário → POST /auth/login {email, password}
        ← 200 {accessToken, refreshToken, expiresIn}
        [Erro 401 se credenciais inválidas]
```

#### Refresh Token
```
Usuário → POST /auth/refresh {refreshToken}
        ← 200 {accessToken, refreshToken, expiresIn}
```

#### Logout
```
Usuário → POST /auth/logout (Header: Authorization: Bearer <token>)
        ← 200 {message: "logout successful"}
```

#### Rota Protegida
```
Usuário → GET /protected (Header: Authorization: Bearer <token>)
        ← 200 {data}
        [Erro 401 sem token ou token inválido/expirado]
```

## Entidades

### User
```
id          uuid
email       string (único, indexado)
password    string (hash bcrypt, nunca exposto)
createdAt   timestamp
updatedAt   timestamp
```

### RefreshToken (para blocklist/invalidação)
```
id           uuid
userId       uuid (FK)
token        string (hash do refresh token)
expiresAt    timestamp
revokedAt    timestamp (null se ativo)
createdAt    timestamp
```

## Segurança

- Senha: hash bcrypt com salt rounds = 12
- Access token JWT: payload {sub: userId, email, type: "access"}, exp 15min
- Refresh token JWT: payload {sub: userId, type: "refresh"}, exp 7d
- Refresh tokens armazenados em tabela (não apenas JWT signed — permitem revoke)
- Rotas exceto /auth/* exigem Authorization: Bearer <accessToken>
- Rate limiting em /auth/* (sugestão: 10 req/min por IP)

## stack

- bcrypt → hash de senhas
- jsonwebtoken → criação/verificação de JWT
- Armazenamento: SQLite/Prisma (same stack do projeto)
