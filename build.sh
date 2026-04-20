#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --noinput
python manage.py migrate

# Create a default admin user if it doesn't exist (Free alternative to Shell)
python manage.py shell -c "from django.contrib.auth.models import User; User.objects.filter(username='7001701818').exists() or User.objects.create_superuser('7001701818', 'admin@example.com', 'admin123')"
