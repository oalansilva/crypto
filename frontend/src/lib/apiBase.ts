export const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8003/api";

// WebSocket URL derivado automaticamente do API_BASE_URL
// Converte http(s)://host:port/api para ws(s)://host:port/api
export const WS_BASE_URL = API_BASE_URL.replace(/^http/, "ws");
