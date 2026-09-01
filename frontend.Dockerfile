# CP6.3: Multi-stage build - stage 1 build React bang Node, stage 2 chi serve file tinh
# bang Nginx (image cuoi cung khong co Node/npm, nhe hon nhieu).
FROM node:20-alpine AS build
WORKDIR /app
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
