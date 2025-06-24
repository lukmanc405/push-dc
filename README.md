# Install Git
pkg install git -y

# Clone the repository
git clone https://github.com/lukmanc405/push-dc.git

# Install Python
pkg install python -y

# Update system
apt update && apt upgrade -y

# Install OpenSSL
pkg install openssl -y

# Install Python packages
pip install requests colorama aiohttp

# Change directory
cd push-dc

# Run the Python script
python main.py
