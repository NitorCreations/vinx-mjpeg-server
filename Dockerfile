FROM python:3.13

WORKDIR /app

COPY pyproject.toml vinx_mjpeg_server.py /app
COPY vinx_mjpeg_server /app/vinx_mjpeg_server

RUN pip install --no-cache .

ENTRYPOINT ["python3", "/app/vinx_mjpeg_server.py"]

CMD ["-h"]
