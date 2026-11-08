# Frontend image, used for local runs with Docker Compose.
# In Azure the same files are served from Blob Storage (static website), not from this container.
FROM nginxinc/nginx-unprivileged:1.27-alpine
COPY --chown=nginx:nginx index.html app.js styles.css config.js /usr/share/nginx/html/
EXPOSE 8080
