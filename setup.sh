#!/data/data/com.termux/files/usr/bin/bash

# 更新软件包
pkg update -y

# 安装 git 和 python3
pkg install -y git python python-pip

# 安装 Python 软件包
pip install colorama sh requests

# 克隆 git 仓库到 $PREFIX/usr/local/src 下
GIT_REPO_URL="https://github.com/2061360308/proot-debian.git"  # 替换为实际的仓库 URL
CLONE_DIR="$PREFIX/usr/local/src"
git clone $GIT_REPO_URL $CLONE_DIR

# 在 $PREFIX/usr/bin 目录下创建 setup-proot-debian 脚本
SETUP_SCRIPT="$PREFIX/usr/bin/setup-proot-debian"
echo "#!/data/data/com.termux/files/usr/bin/bash" > $SETUP_SCRIPT
echo "python3 $CLONE_DIR/setup_termux.py" >> $SETUP_SCRIPT

# 赋予执行权限
chmod +x $SETUP_SCRIPT

setup-proot-debian