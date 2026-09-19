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
# Bỏ script tự dò IPv6 của image gốc (chỉ có tác dụng với default.conf GỐC mà mình đã ghi đè
# ở trên) - script này gọi `apk manifest nginx` lúc container khởi động, có thể TREO VÔ THỜI
# HẠN trong môi trường mạng ra ngoài bị hạn chế/lọc (không phản hồi tới kho Alpine), khiến
# container không bao giờ start được dù build thành công. nginx.conf của mình đã tự khai báo
# `listen 80` rõ ràng nên không cần bước tự dò này.
RUN rm -f /docker-entrypoint.d/10-listen-on-ipv6-by-default.sh
EXPOSE 80
