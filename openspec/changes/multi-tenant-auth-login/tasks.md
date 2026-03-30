# Tasks — Card #69: [MT-1] Autenticação — Login, Registro e JWT

## Lista de Tarefas Técnicas

1. **User model + migração Prisma**
   - Criar modelo User com campos: id (uuid), email (unique), password (string), createdAt, updatedAt
   - Criar modelo RefreshToken com campos: id, userId (FK), tokenHash, expiresAt, revokedAt, createdAt
   - Executar migração

2. **Auth service (registro, login, logout, refresh)**
   - `register(email, password)`: valida email, verifica duplicado, hash bcrypt, salva user, retorna user
   - `login(email, password)`: busca user, compara bcrypt, gera access + refresh JWT, salva refresh token, retorna tokens
   - `logout(refreshToken)`: marca refresh token como revoked
   - `refresh(refreshToken)`: valida refresh token, verifica se não revoked, gera novos tokens

3. **JWT utilitários**
   - `generateAccessToken(user)`: jwt.sign com exp 15min
   - `generateRefreshToken(user)`: jwt.sign com exp 7d
   - `verifyToken(token, secret)`: jwt.verify com try/catch

4. **Middleware de autenticação**
   - Extrair Bearer token do header Authorization
   - Verificar token com verifyToken
   - Injetar `req.user = {userId, email}` no request
   - Responder 401 para token inválido/expirado

5. **Rotas /auth/*
   - POST /auth/register → authService.register
   - POST /auth/login → authService.login
   - POST /auth/logout → authService.logout (auth middleware)
   - POST /auth/refresh → authService.refresh

**Nota:** Tarefas 1-5 devem ser completadas antes de considerar o card Done.
