#!/bin/bash
set -e
set -o pipefail

# ====== 1️⃣ CÀI DEPENDENCIES ======
sudo apt update
sudo apt install -y git redis-server libmariadb-dev mariadb-server mariadb-client pkg-config pipx xvfb libfontconfig expect wget curl
sudo mysql_secure_installation

# ====== 2️⃣ CÀI WKHTMLTOPDF ======
cd ~
WK_DEB="wkhtmltox_0.12.6.1-2.jammy_amd64.deb"
wget -O $WK_DEB https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-2/$WK_DEB
sudo dpkg -i $WK_DEB || sudo apt -f install -y

# ====== 3️⃣ CÀI NVM + NODE + YARN ======
export NVM_DIR="$HOME/.nvm"
if [ ! -d "$NVM_DIR" ]; then
  curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
fi

# Load nvm ngay trong script
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

nvm install 24
nvm use 24
npm install -g yarn

# ====== 4️⃣ CÀI UV + PYTHON ======
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"
if uv python list | grep -q 3.14; then
    uv python uninstall 3.14
fi
uv python install 3.12 --default

# ====== 5️⃣ PIPX ======
pipx ensurepath

# ====== 6️⃣ CÀI FRAPPE-BENCH ======
pipx install frappe-bench

# ====== 7️⃣ REDIS ======
sudo systemctl enable redis-server
sudo systemctl start redis-server

# ====== 8️⃣ INIT BENCH ======
cd ~
bench init --frappe-branch version-15 frappe-bench
cd frappe-bench

# ====== 9️⃣ TẠO SITE ======
bench new-site localhost --mariadb-root-password admin --admin-password admin

# ====== 🔧 CẬP NHẬT REDIS PORT ======
sed -i 's/:13000/:6379/g; s/:11000/:6379/g' sites/common_site_config.json

# ====== 🔟 CÀI APP PROTOTYPE ======
bench get-app https://github.com/HieuCaoTlu/prototype
cd apps/prototype
git remote add origin https://github.com/HieuCaoTlu/prototype
git remote remove upstream 2>/dev/null || true
git pull origin develop
cd ../../

bench --site localhost install-app prototype
bench --site localhost enable-scheduler
bench --site localhost add-to-hosts
bench --site localhost migrate
bench set-config -g developer_mode 1

# ====== 1️⃣1️⃣ CÀI HONCHO ======
pipx install honcho
pipx inject frappe-bench honcho

# ====== 1️⃣2️⃣ START BENCH ======
bench start
