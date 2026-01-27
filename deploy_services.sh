#!/bin/bash
#
# EMS-Core v2.0 - Service Deployment Script
# Installiert und startet Optimizer + WebUI als Systemd Services
#

set -e  # Exit on error

echo "================================================"
echo "EMS-Core v2.0 - Service Deployment"
echo "================================================"
echo ""

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo "❌ This script must be run as root (use sudo)"
   exit 1
fi

EMS_DIR="/opt/ems-core"
VENV_DIR="${EMS_DIR}/venv"

# Check if EMS directory exists
if [ ! -d "$EMS_DIR" ]; then
    echo "❌ Error: ${EMS_DIR} does not exist"
    exit 1
fi

echo "📁 EMS Directory: ${EMS_DIR}"
echo ""

# Step 1: Stop existing services (if running)
echo "🛑 Stopping existing services..."
systemctl stop ems-optimizer 2>/dev/null || true
systemctl stop ems-webui 2>/dev/null || true
echo "✅ Services stopped"
echo ""

# Step 2: Create/Update systemd service files
echo "📝 Creating systemd service files..."

# Optimizer Service
cat > /etc/systemd/system/ems-optimizer.service << 'EOF'
[Unit]
Description=EMS-Core v2.0 Optimizer - Energy Management System
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=root
Group=root
WorkingDirectory=/opt/ems-core
Environment="PATH=/opt/ems-core/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
ExecStart=/opt/ems-core/venv/bin/python3 -m core.main

# Restart on failure
Restart=always
RestartSec=10

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=ems-optimizer

# Resource limits
LimitNOFILE=65536

[Install]
WantedBy=multi-user.target
EOF

echo "✅ Created: /etc/systemd/system/ems-optimizer.service"

# WebUI Service
cat > /etc/systemd/system/ems-webui.service << 'EOF'
[Unit]
Description=EMS-Core v2.0 Web UI - Flask Application
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=root
Group=root
WorkingDirectory=/opt/ems-core/webui
Environment="PATH=/opt/ems-core/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
ExecStart=/opt/ems-core/venv/bin/python3 app.py

# Restart on failure
Restart=always
RestartSec=10

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=ems-webui

# Resource limits
LimitNOFILE=65536

[Install]
WantedBy=multi-user.target
EOF

echo "✅ Created: /etc/systemd/system/ems-webui.service"
echo ""

# Step 3: Reload systemd
echo "🔄 Reloading systemd daemon..."
systemctl daemon-reload
echo "✅ Systemd reloaded"
echo ""

# Step 4: Enable services (auto-start on boot)
echo "⚙️ Enabling services..."
systemctl enable ems-optimizer
systemctl enable ems-webui
echo "✅ Services enabled (will start on boot)"
echo ""

# Step 5: Start services
echo "🚀 Starting services..."
systemctl start ems-optimizer
systemctl start ems-webui
echo "✅ Services started"
echo ""

# Step 6: Check status
echo "📊 Service Status:"
echo ""
echo "--- EMS Optimizer ---"
systemctl status ems-optimizer --no-pager -l || true
echo ""
echo "--- EMS WebUI ---"
systemctl status ems-webui --no-pager -l || true
echo ""

# Step 7: Show useful commands
echo "================================================"
echo "✅ Deployment Complete!"
echo "================================================"
echo ""
echo "📋 Useful Commands:"
echo ""
echo "  Status:"
echo "    sudo systemctl status ems-optimizer"
echo "    sudo systemctl status ems-webui"
echo ""
echo "  Logs:"
echo "    sudo journalctl -u ems-optimizer -f"
echo "    sudo journalctl -u ems-webui -f"
echo ""
echo "  Control:"
echo "    sudo systemctl start|stop|restart ems-optimizer"
echo "    sudo systemctl start|stop|restart ems-webui"
echo ""
echo "  Disable auto-start:"
echo "    sudo systemctl disable ems-optimizer"
echo "    sudo systemctl disable ems-webui"
echo ""
echo "🌐 WebUI: http://$(hostname -I | awk '{print $1}'):8080"
echo ""
