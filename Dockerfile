FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements-dev.txt

COPY . .
RUN pip install --no-cache-dir -e .

EXPOSE 8000

ENTRYPOINT ["docker/entrypoint.sh"]
CMD ["runserver"]
