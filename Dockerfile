FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Matches the host user by default (see .env / docker-compose.yml) so that
# files written into the bind-mounted repo (db.sqlite3, media uploads, ...)
# aren't owned by root on the host.
ARG UID=1000
ARG GID=1000

RUN groupadd -g "${GID}" appuser \
    && useradd -m -u "${UID}" -g "${GID}" -s /bin/bash appuser

WORKDIR /app

COPY . .
RUN pip install --no-cache-dir -e ".[test,dev]" \
    && chown -R "${UID}:${GID}" /app

USER appuser

EXPOSE 8000

ENTRYPOINT ["docker/entrypoint.sh"]
CMD ["runserver"]
