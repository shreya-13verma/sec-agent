FROM node:20-alpine AS build

WORKDIR /app

COPY frontend/package.json ./
RUN npm install

COPY frontend ./
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
COPY frontend/package.json ./
RUN npm install -g vite
COPY --from=build /app/dist ./dist
COPY frontend/vite.config.js ./

EXPOSE 3000

CMD ["npx", "vite", "preview", "--port", "3000", "--host", "0.0.0.0"]
