FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Install gunicorn if not in requirements
RUN pip install gunicorn

COPY . .

# Initialize database
RUN python -c "from app_fixed import init_db, create_admin_user; init_db(); create_admin_user()"

EXPOSE $PORT

CMD gunicorn --bind 0.0.0.0:$PORT app_fixed:app
