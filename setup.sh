#!/data/data/com.termux/files/usr/bin/bash

# 更新软件包
pkg update -y

# 安装 git 和 python3
pkg install -y ca-certificates git openssl python python-pip

# 安装 Python 软件包
pip install colorama sh requests

# 克隆 git 仓库到 $PREFIX/usr/local/src 下
GIT_REPO_URL="https://github.com/2061360308/proot-debian.git"  # 替换为实际的仓库 URL
CLONE_DIR="$PREFIX/local/src"
git clone $GIT_REPO_URL $CLONE_DIR

# 在 $PREFIX/usr/bin 目录下创建 setup-proot-debian 脚本
SETUP_SCRIPT="$PREFIX/bin/setup-proot-debian"
echo "#!/data/data/com.termux/files/usr/bin/bash" > $SETUP_SCRIPT
echo "python3 $CLONE_DIR/setup_termux.py" >> $SETUP_SCRIPT

# 赋予执行权限
chmod +x $SETUP_SCRIPT

clear

R="$(printf '\033[1;31m')"
G="$(printf '\033[1;32m')"
Y="$(printf '\033[1;33m')"
B="$(printf '\033[1;34m')"
C="$(printf '\033[1;36m')"
W="$(printf '\033[0m')"
BOLD="$(printf '\033[1m')"

echo "${G}脚本下载完成！请键入 setup-proot-debian 命令继续！${W}"