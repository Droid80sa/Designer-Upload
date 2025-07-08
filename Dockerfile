FROM python:3.10

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=app.py

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5055

CMD ["flask", "run", "--host=0.0.0.0", "--port=5055"]
