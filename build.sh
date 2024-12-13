#!/usr/bin/env bash
# exit on error
set -o errexit
apt-get update
apt-get install -y software-properties-common
add-apt-repository -y ppa:ubuntu-toolchain-r/test
apt-get update
apt-get install -y zbar-tools libzbar0 libzbar-dev
# Install Python dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Run migrations
python manage.py migrate

# Create superuser
python manage.py create_superuser