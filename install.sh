cd ~
sudo apt update
sudo apt install git redis-server libmariadb-dev mariadb-server mariadb-client pkg-config pipx xvfb libfontconfig expect -y

cat << 'EOF' > mariadb_secure.expect
#!/usr/bin/expect -f
set timeout 10
spawn sudo mariadb-secure-installation

expect "Enter current password for root"
send "\r"

expect "Switch to unix_socket authentication"
send "Y\r"

expect "Change the root password?"
send "Y\r"

expect "New password:"
send "admin\r"

expect "Re-enter new password:"
send "admin\r"

expect "Remove anonymous users?"
send "Y\r"

expect "Disallow root login remotely?"
send "Y\r"

expect "Remove test database and access to it?"
send "Y\r"

expect "Reload privilege tables now?"
send "Y\r"

expect eof
EOF

chmod +x mariadb_secure.expect
./mariadb_secure.expect
rm mariadb_secure.expect

cd ~
wget https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-2/wkhtmltox_0.12.6.1-2.jammy_amd64.deb
sudo dpkg -i wkhtmltox_0.12.6.1-2.jammy_amd64.deb || sudo apt -f install -y

curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
source ~/.bashrc
nvm install 24
npm install -g yarn
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc
uv python install 3.14 --default
pipx ensurepath
cd ~
pipx install frappe-bench
sudo systemctl enable redis-server
sudo systemctl start redis-server
bench init --frappe-branch version-15 frappe-bench
cd frappe-bench
bench new-site localhost --mariadb-root-password admin --admin-password admin
bench get-app https://github.com/HieuCaoTlu/prototype
cd ~/frappe-bench/apps/prototype
git remote add origin https://github.com/HieuCaoTlu/prototype
git remote remove upstream 2>/dev/null || true
bench --site localhost install-app prototype
bench --site localhost enable-scheduler
bench --site localhost set-config server_script_enabled true
bench set-config -g developer_mode true
bench --site localhost add-to-hosts
bench --site localhost migrate
pipx install honcho
pipx inject frappe-bench honcho
git pull origin develop
bench start
