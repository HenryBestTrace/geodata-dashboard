#!/bin/bash
# EC2 Deployment Setup Script for Dash Dashboard
# This script helps set up the required environment on an AWS EC2 instance

# Exit on error
set -e

echo "==================================================="
echo "    Dashboard EC2 Deployment Setup"
echo "==================================================="

# Update system packages
echo "Updating system packages..."
sudo apt-get update -y
sudo apt-get upgrade -y

# Install Python and dependencies
echo "Installing Python and required packages..."
sudo apt-get install -y python3 python3-pip python3-venv nginx certbot python3-certbot-nginx

# Create directory for application
APP_DIR=/opt/dashboard
sudo mkdir -p $APP_DIR
sudo chown -R ubuntu:ubuntu $APP_DIR

# Create Python virtual environment
echo "Setting up Python virtual environment..."
python3 -m venv $APP_DIR/venv
source $APP_DIR/venv/bin/activate

# Install required Python packages
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install dash dash-bootstrap-components pandas plotly shapely numpy pillow gunicorn

# Set up Nginx for reverse proxy
echo "Setting up Nginx as a reverse proxy..."
sudo tee /etc/nginx/sites-available/dashboard << EOF
server {
    listen 80;
    server_name YOUR_DOMAIN_NAME;  # Replace with your domain

    location / {
        proxy_pass http://localhost:8050;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/dashboard /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Create systemd service for the dashboard
echo "Creating systemd service for dashboard..."
sudo tee /etc/systemd/system/dashboard.service << EOF
[Unit]
Description=Geodata Visualization Dashboard
After=network.target

[Service]
User=ubuntu
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
Environment="EC2_MODE=1"
ExecStart=$APP_DIR/venv/bin/gunicorn --workers 3 --bind 0.0.0.0:8050 main_app_ec2:server

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable dashboard.service

echo "==================================================="
echo "Basic setup complete!"
echo "==================================================="
echo ""
echo "Next steps:"
echo "1. Replace 'YOUR_DOMAIN_NAME' in /etc/nginx/sites-available/dashboard with your actual domain"
echo "2. Upload your dashboard files to $APP_DIR directory"
echo "3. Run: sudo certbot --nginx -d YOUR_DOMAIN_NAME"
echo "4. Start the dashboard: sudo systemctl start dashboard.service"
echo "5. Check status: sudo systemctl status dashboard.service"
echo ""
echo "==================================================="
