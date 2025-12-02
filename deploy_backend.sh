#!/bin/bash
# RoboKen Backend Deployment Script
# Usage: ./deploy_backend.sh [staging|production]

set -e

ENVIRONMENT=$1

if [ -z "$ENVIRONMENT" ]; then
    echo "Usage: ./deploy_backend.sh [staging|production]"
    exit 1
fi

echo "========================================="
echo "RoboKen Backend Deployment"
echo "Environment: $ENVIRONMENT"
echo "========================================="

# Set environment-specific variables
if [ "$ENVIRONMENT" = "staging" ]; then
    APP_PORT=8000
    CONFIG_ENV="staging"
elif [ "$ENVIRONMENT" = "production" ]; then
    APP_PORT=8000
    CONFIG_ENV="production"
else
    echo "Invalid environment. Use 'staging' or 'production'"
    exit 1
fi

# Update system
echo "Updating system packages..."
sudo dnf update -y

# Install Python 3.11 if not installed
echo "Installing Python 3.11..."
sudo dnf install -y python3.11 python3.11-pip

# Install git if not installed
echo "Installing git..."
sudo dnf install -y git

# Create application directory
echo "Creating application directory..."
sudo mkdir -p /opt/roboken
sudo chown $USER:$USER /opt/roboken
cd /opt/roboken

# Clone or update repository
if [ -d ".git" ]; then
    echo "Updating repository..."
    git pull origin main
else
    echo "Cloning repository..."
    # Replace with your actual GitHub repository URL
    git clone https://github.com/YOUR_USERNAME/roboken-simulator.git .
fi

# Install dependencies
echo "Installing Python dependencies..."
python3.11 -m pip install --upgrade pip
python3.11 -m pip install -r requirements.txt

# Install AWS CLI if not installed
if ! command -v aws &> /dev/null; then
    echo "Installing AWS CLI..."
    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
    unzip awscliv2.zip
    sudo ./aws/install
    rm -rf aws awscliv2.zip
fi

# Create environment configuration file
echo "Creating environment configuration..."
cat > /opt/roboken/.env << EOF
ENVIRONMENT=$CONFIG_ENV
AWS_REGION=ap-northeast-1
APP_PORT=$APP_PORT
EOF

# Create systemd service file
echo "Creating systemd service..."
sudo tee /etc/systemd/system/roboken.service > /dev/null << EOF
[Unit]
Description=RoboKen AI Automation Platform
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/opt/roboken
Environment="PATH=/usr/local/bin:/usr/bin:/bin"
EnvironmentFile=/opt/roboken/.env
ExecStart=/usr/local/bin/python3.11 -m uvicorn roboken_complete_platform:app --host 0.0.0.0 --port $APP_PORT
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
echo "Reloading systemd..."
sudo systemctl daemon-reload

# Enable and start service
echo "Starting RoboKen service..."
sudo systemctl enable roboken
sudo systemctl restart roboken

# Wait for service to start
echo "Waiting for service to start..."
sleep 5

# Check service status
echo "Checking service status..."
sudo systemctl status roboken --no-pager

# Test the API
echo "Testing API endpoint..."
sleep 2
curl -f http://localhost:$APP_PORT/health || echo "Warning: Health check failed"

echo "========================================="
echo "Deployment complete!"
echo "Environment: $ENVIRONMENT"
echo "Service status: $(sudo systemctl is-active roboken)"
echo "========================================="
echo ""
echo "Useful commands:"
echo "  View logs: sudo journalctl -u roboken -f"
echo "  Restart service: sudo systemctl restart roboken"
echo "  Stop service: sudo systemctl stop roboken"
echo "  Check status: sudo systemctl status roboken"
