FROM node:20-alpine AS deps

WORKDIR /workspace/frontend

COPY frontend/package*.json ./

RUN npm ci

FROM deps AS dev

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]

FROM deps AS build

COPY frontend/ ./

RUN npm run build

FROM nginx:1.27-alpine AS production

COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /workspace/frontend/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

