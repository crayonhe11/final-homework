FROM python:3.13-slim
WORKDIR /app
COPY main.py ./
COPY backend ./backend
COPY data ./data
COPY web/static ./web/static
RUN useradd --create-home learner && mkdir /data && chown learner:learner /data
USER learner
EXPOSE 8000
VOLUME ["/data"]
CMD ["python", "main.py", "--host", "0.0.0.0", "--db", "/data/learning.sqlite3"]
