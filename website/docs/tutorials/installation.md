# Installation Guide

Complete installation instructions for the All-in-One Crypto Trading MCP Server across different platforms and deployment scenarios.

## 📋 System Requirements

### Minimum Requirements
- **Operating System**: Windows 10+, macOS 10.15+, Linux (Ubuntu 18.04+)
- **Python**: 3.9 or higher
- **Memory**: 2GB RAM minimum (4GB recommended)
- **Storage**: 1GB available space
- **Network**: Stable internet connection

### Recommended Requirements
- **Memory**: 8GB RAM or higher
- **CPU**: 4+ cores for optimal performance
- **Storage**: 5GB+ for data caching and logs
- **Network**: High-speed internet for real-time data

### Dependencies
- **Git**: For repository cloning
- **Redis**: For caching (optional but recommended)
- **PostgreSQL**: For production database (SQLite default)
- **Node.js**: For web interface components (optional)

## 🐍 Python Installation

### Install Python

#### Windows
```bash
# Download from python.org or use chocolatey
choco install python39

# Verify installation
python --version
pip --version
```

#### macOS
```bash
# Using Homebrew
brew install python@3.9

# Or download from python.org
# Verify installation
python3 --version
pip3 --version
```

#### Linux (Ubuntu/Debian)
```bash
# Update package list
sudo apt update

# Install Python 3.9+
sudo apt install python3.9 python3.9-pip python3.9-venv

# Verify installation
python3.9 --version
pip3.9 --version
```

## 📦 Installation Methods

### Method 1: Quick Install (Recommended)

#### Automated Installation Script
```bash
# Download and run the installation script
curl -sSL https://install.cryptomcp.dev | bash

# Or with wget
wget -qO- https://install.cryptomcp.dev | bash

# The script will:
# 1. Check system requirements
# 2. Install dependencies
# 3. Clone the repository
# 4. Set up virtual environment
# 5. Install Python packages
# 6. Create configuration files
# 7. Set up database
```

### Method 2: Manual Installation

#### Step 1: Clone Repository
```bash
# Clone the repository
git clone https://github.com/cryptomcp/allinone-crypto-trading-mcp-server.git
cd allinone-crypto-trading-mcp-server

# Or download the latest release
wget https://github.com/cryptomcp/allinone-crypto-trading-mcp-server/archive/refs/tags/v2.1.0.tar.gz
tar -xzf v2.1.0.tar.gz
cd allinone-crypto-trading-mcp-server-2.0.0
```

#### Step 2: Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

#### Step 3: Install Dependencies
```bash
# Install the package in development mode
pip install -e .

# Or install from requirements
pip install -r requirements.txt

# Install optional dependencies
pip install -e ".[all]"  # All optional features
pip install -e ".[web]"  # Web interface
pip install -e ".[ai]"   # AI features
```

### Method 3: Docker Installation

#### Quick Docker Setup
```bash
# Pull and run the Docker image
docker run -d \
  --name allinone-crypto-mcp \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/.env:/app/.env \
  cryptomcp/allinone-crypto-mcp:latest

# Or use docker-compose
curl -O https://raw.githubusercontent.com/cryptomcp/allinone-crypto-trading-mcp-server/main/docker-compose.yml
docker-compose up -d
```

#### Custom Docker Build
```bash
# Build from source
git clone https://github.com/cryptomcp/allinone-crypto-trading-mcp-server.git
cd allinone-crypto-trading-mcp-server

# Build Docker image
docker build -t allinone-crypto-mcp .

# Run with custom configuration
docker run -d \
  --name allinone-crypto-mcp \
  -p 8000:8000 \
  -e LIVE=false \
  -e BINANCE_API_KEY=your_api_key \
  -v $(pwd)/data:/app/data \
  allinone-crypto-mcp
```

## ⚙️ Configuration Setup

### Environment Configuration

#### Create Configuration File
```bash
# Copy environment template
cp .env.example .env

# Edit configuration (use your preferred editor)
nano .env
# or
vim .env
# or
code .env
```

#### Essential Configuration
```env
# Security Settings (CRITICAL)
LIVE=false                          # Start in simulation mode
AM_I_SURE=false                     # Additional safety check
SECRET_KEY=your_secret_key_here     # Generate secure secret key

# Database Configuration
DATABASE_URL=sqlite:///./data/trading.db
# For PostgreSQL:
# DATABASE_URL=postgresql://user:pass@localhost:5432/trading

# Redis Configuration (Optional)
REDIS_URL=redis://localhost:6379/0

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=./logs/trading.log
```

### Generate Secret Key
```python
# Generate a secure secret key
python -c "
import secrets
print('SECRET_KEY=' + secrets.token_urlsafe(32))
"
```

### Database Setup

#### SQLite (Default)
```bash
# SQLite is automatically created
# No additional setup required
mkdir -p data logs
```

#### PostgreSQL Setup
```bash
# Install PostgreSQL
# Ubuntu/Debian:
sudo apt install postgresql postgresql-contrib

# macOS:
brew install postgresql

# Create database and user
sudo -u postgres psql
CREATE DATABASE trading;
CREATE USER trading_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE trading TO trading_user;
\q

# Update .env file
echo "DATABASE_URL=postgresql://trading_user:secure_password@localhost:5432/trading" >> .env
```

#### Redis Setup (Optional)
```bash
# Install Redis
# Ubuntu/Debian:
sudo apt install redis-server

# macOS:
brew install redis

# Start Redis
sudo systemctl start redis-server
# or on macOS:
brew services start redis

# Test Redis connection
redis-cli ping
# Should return: PONG
```

## 🔐 Security Setup

### API Keys Configuration

#### Exchange API Keys
```env
# Binance
BINANCE_API_KEY=your_binance_api_key
BINANCE_SECRET_KEY=your_binance_secret_key
BINANCE_TESTNET=true                # Start with testnet

# Coinbase Pro
COINBASE_API_KEY=your_coinbase_api_key
COINBASE_SECRET_KEY=your_coinbase_secret_key
COINBASE_PASSPHRASE=your_coinbase_passphrase
COINBASE_SANDBOX=true               # Start with sandbox

# Add other exchanges as needed
```

#### Blockchain Configuration
```env
# Ethereum
ETH_RPC_URL=https://eth-mainnet.g.alchemy.com/v2/YOUR_API_KEY
ETH_PRIVATE_KEY=your_ethereum_private_key  # Store securely!

# Solana
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
SOLANA_PRIVATE_KEY=your_solana_private_key  # Store securely!
```

#### News and Data APIs
```env
# CryptoPanic
CRYPTOPANIC_API_KEY=your_cryptopanic_api_key

# Whale Alert
WHALE_ALERT_API_KEY=your_whale_alert_api_key

# DexPaprika
DEXPAPRIKA_API_KEY=your_dexpaprika_api_key
```

### File Permissions
```bash
# Set proper file permissions
chmod 600 .env                     # Only owner can read/write
chmod 755 src/                     # Directory permissions
chmod 644 src/*.py                 # File permissions

# Create secure directories
mkdir -p data logs backups
chmod 750 data logs backups
```

## 🧪 Verification & Testing

### Installation Verification

#### Test Basic Installation
```bash
# Activate virtual environment
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows

# Test basic import
python -c "
import sys
print('Python version:', sys.version)

try:
    from allinone_crypto_mcp import __version__
    print('Package version:', __version__)
    print('✅ Installation successful!')
except ImportError as e:
    print('❌ Installation failed:', e)
"
```

#### Test Database Connection
```bash
# Test database connectivity
python -c "
from src.core.database import get_database_connection
try:
    conn = get_database_connection()
    print('✅ Database connection successful!')
    conn.close()
except Exception as e:
    print('❌ Database connection failed:', e)
"
```

#### Test API Connections
```bash
# Run connection tests
python -c "
import asyncio
from src.cex.exchanges import test_exchange_connections

async def test():
    results = await test_exchange_connections()
    for exchange, status in results.items():
        status_icon = '✅' if status['connected'] else '❌'
        print(f'{status_icon} {exchange}: {status['message']}')

asyncio.run(test())
"
```

### Run Test Suite
```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run all tests
pytest tests/

# Run specific test categories
pytest tests/unit/                  # Unit tests
pytest tests/integration/           # Integration tests
pytest tests/e2e/                   # End-to-end tests

# Run with coverage
pip install pytest-cov
pytest --cov=src tests/
```

## 🚀 First Run

### Start the MCP Server

#### Development Mode
```bash
# Start in development mode
python -m src.main

# Or using the installed command
allinone-crypto-mcp --debug

# With specific configuration
allinone-crypto-mcp --config /path/to/config.env
```

#### Production Mode
```bash
# Start in production mode
allinone-crypto-mcp --production

# With logging
allinone-crypto-mcp --production --log-level INFO

# As a daemon
nohup allinone-crypto-mcp --production > logs/server.log 2>&1 &
```

### Start Additional Services

#### Telegram Bot
```bash
# In a separate terminal
python -m src.telegram.bot

# Or as background service
nohup python -m src.telegram.bot > logs/telegram.log 2>&1 &
```

#### Web Interface (Optional)
```bash
# Start web interface
python -m src.web.app

# Or using uvicorn
uvicorn src.web.app:app --host 0.0.0.0 --port 8000
```

## 🔧 Platform-Specific Notes

### Windows Installation

#### PowerShell Execution Policy
```powershell
# Allow script execution
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Install Python packages
pip install -e .
```

#### Windows Service Setup
```bash
# Install pywin32 for Windows service support
pip install pywin32

# Create Windows service
python scripts/install_windows_service.py
```

### macOS Installation

#### Xcode Command Line Tools
```bash
# Install Xcode command line tools (required for some packages)
xcode-select --install
```

#### macOS Service Setup
```bash
# Create launchd service
cp scripts/com.cryptomcp.allinone.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.cryptomcp.allinone.plist
```

### Linux Installation

#### System Dependencies
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y \
    python3-dev \
    python3-pip \
    python3-venv \
    build-essential \
    libffi-dev \
    libssl-dev \
    redis-server \
    postgresql \
    postgresql-contrib

# CentOS/RHEL
sudo yum update
sudo yum install -y \
    python3-devel \
    python3-pip \
    gcc \
    openssl-devel \
    libffi-devel \
    redis \
    postgresql \
    postgresql-server
```

#### Systemd Service Setup
```bash
# Copy service file
sudo cp scripts/allinone-crypto-mcp.service /etc/systemd/system/

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable allinone-crypto-mcp
sudo systemctl start allinone-crypto-mcp

# Check status
sudo systemctl status allinone-crypto-mcp
```

## 🐳 Docker Deployment

### Docker Compose Setup

#### Production Docker Compose
```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  app:
    image: cryptomcp/allinone-crypto-mcp:latest
    restart: unless-stopped
    environment:
      - LIVE=false
      - DATABASE_URL=postgresql://postgres:password@db:5432/trading
      - REDIS_URL=redis://redis:6379/0
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./.env:/app/.env
    depends_on:
      - db
      - redis
    ports:
      - "8000:8000"
  
  db:
    image: postgres:13
    restart: unless-stopped
    environment:
      - POSTGRES_DB=trading
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:6-alpine
    restart: unless-stopped
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

#### Run Production Setup
```bash
# Start production environment
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Scale services
docker-compose -f docker-compose.prod.yml up -d --scale app=3
```

## 🔍 Troubleshooting

### Common Issues

#### Import Errors
```bash
# If you get import errors, check:
which python
pip list | grep allinone

# Reinstall if necessary
pip uninstall allinone-crypto-mcp
pip install -e .
```

#### Permission Errors
```bash
# Fix file permissions
chmod -R 755 src/
chmod 600 .env
chown -R $USER:$USER data/ logs/
```

#### Database Connection Issues
```bash
# Test database URL
python -c "
from sqlalchemy import create_engine
engine = create_engine('your_database_url')
try:
    engine.connect()
    print('✅ Database connection successful')
except Exception as e:
    print('❌ Database error:', e)
"
```

#### API Connection Issues
```bash
# Test API connectivity
curl -I https://api.binance.com/api/v3/ping
curl -I https://api.pro.coinbase.com/products

# Check firewall/proxy settings
ping api.binance.com
```

### Getting Help

#### Log Analysis
```bash
# Check application logs
tail -f logs/trading.log

# Check system logs
# Linux:
sudo journalctl -u allinone-crypto-mcp -f

# Windows:
# Check Windows Event Viewer

# macOS:
tail -f /var/log/system.log
```

#### Debug Mode
```bash
# Run with debug logging
PYTHONPATH=. python -m src.main --debug --log-level DEBUG

# Verbose output
allinone-crypto-mcp --verbose --debug
```

## 📞 Support

For installation support:
- **Installation Help**: install@cryptomcp.dev
- **Technical Support**: support@cryptomcp.dev
- **Documentation**: docs@cryptomcp.dev
- **Community**: [Telegram](https://t.me/web3botsupport)

### Quick Support Check
```bash
# Generate system info for support
python scripts/system_info.py > system_info.txt

# This creates a report with:
# - Python version and packages
# - System information
# - Configuration status
# - Test results
```

---

**🎉 Congratulations!** You've successfully installed the All-in-One Crypto Trading MCP Server. Next, check out the [Configuration Guide](configuration.md) to set up your trading environment.