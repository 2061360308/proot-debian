from colorama import init, Fore, Style
from tools import banner, ask_confirmation, run_command, run_command_in_container
from tools import install_package, install_package_in_container, add_to_file
from tools import GREEN, RED, YELLOW, BLUE, BORDER
import commands
import os, shutil, sh

init()

banner()

question = GREEN("这个脚本用来自动完成利用Proot-distro\
在Termux配置Debian + LXQt的LInux桌面\n 是否继续")
ask_confirmation(question)
if not ask_confirmation(question):
    print("用户选择退出脚本")
    exit()

# 启用Termux x11和root软件源
run_command(commands.init_termux_source)
# 更新软件包
run_command(commands.update_termux_source)
# 获取存储权限
run_command(commands.get_storage_authority)
# 安装必备软件包
install_package(("termux-x11-nightly", 
                 "pulseaudio", 
                 "virglrenderer-android", 
                 "termux-am", 
                 "tmux", 
                 "proot-distro"), True)

# 安装debian容器
run_command(commands.install_debian)

# 询问用户名
quesiton = "将为您在Debian容器中创建一个新用户, 请输入用户名: "
username = input(GREEN(quesiton))

# 创建新用户
create_user_command = (commands.create_user[0], commands.create_user[1].replace("<username>", username))
run_command_in_container(create_user_command)

def add_sudoers_entry(username):
    print(GREEN(f"为用户 {username} 添加 sudoers 条目"))
    prefix = os.getenv("PREFIX")
    sudoers_file = os.path.join(prefix, "var/lib/proot-distro/installed-rootfs/debian/etc/sudoers")
    backup_file = sudoers_file + ".bak"
    
    # 备份 sudoers 文件
    shutil.copy2(sudoers_file, backup_file)
    
    try:
        # 读取 sudoers 文件内容
        with open(sudoers_file, 'r') as file:
            lines = file.readlines()
        
        # 查找 root 行并在其后添加新行
        new_line = f"{username}    ALL=(ALL:ALL) NOPASSWD:ALL\n"
        for i, line in enumerate(lines):
            if line.strip() == "root    ALL=(ALL:ALL) ALL":
                lines.insert(i + 1, new_line)
                break
        
        # 写回 sudoers 文件
        with open(sudoers_file, 'w') as file:
            file.writelines(lines)
        
        print(f"Added sudoers entry for {username}")
    except Exception as e:
        print(f"Error occurred: {e}")
        # 如果出错，恢复原来的文件
        shutil.copy2(backup_file, sudoers_file)
        print("Restored the original sudoers file.")
    finally:
        # 删除备份文件
        if os.path.exists(backup_file):
            os.remove(backup_file)
    
add_sudoers_entry(username)

# 更新Debian容器内apt软件源列表
def update_container_sources_list():
    banner()
    print(GREEN("更新Debian容器内apt软件源列表"))

    install_package_in_container(("apt-transport-https", "ca-certificates"))

    sources_list_content = """# /etc/apt/sources.list
# 默认注释了源码仓库，如有需要可自行取消注释
deb http://mirrors.ustc.edu.cn/debian bookworm main contrib non-free non-free-firmware
# deb-src http://mirrors.ustc.edu.cn/debian bookworm main contrib non-free non-free-firmware
deb http://mirrors.ustc.edu.cn/debian bookworm-updates main contrib non-free non-free-firmware
# deb-src http://mirrors.ustc.edu.cn/debian bookworm-updates main contrib non-free non-free-firmware

# backports 软件源，请按需启用
# deb http://mirrors.ustc.edu.cn/debian bookworm-backports main contrib non-free non-free-firmware
# deb-src http://mirrors.ustc.edu.cn/debian bookworm-backports main contrib non-free non-free-fian.html
"""

    prefix = os.getenv("PREFIX")
    sources_list = os.path.join(prefix, "var/lib/proot-distro/installed-rootfs/debian/etc/apt/sources.list")
    # 备份并删除 sources_list
    backup_sources_list = sources_list + ".bak"
    if os.path.exists(sources_list):
        shutil.copy2(sources_list, backup_sources_list)
        os.remove(sources_list)

    # 写入新的 sources_list
    add_to_file("sources_list", sources_list_content)
    run_command_in_container(commands.update_apt_source)
update_container_sources_list()

# debian 容器内安装语言环境以及文泉驿字体（中文字体）
install_package_in_container(("locales", "fonts-wqy-zenhei"))

# 配置debian容器内系统语言
def configure_locales_in_container(distro="debian"):
    banner()
    print(GREEN("配置 Debian 容器内的语言环境"))

    # 取消注释 /etc/locale.gen 中的 en_US.UTF-8 UTF-8
    prefix = os.getenv("PREFIX")
    locale_gen_file = os.path.join(prefix, f"var/lib/proot-distro/installed-rootfs/{distro}/etc/locale.gen")
    backup_locale_gen_file = locale_gen_file + ".bak"
    
    # 备份 locale.gen 文件
    shutil.copy2(locale_gen_file, backup_locale_gen_file)
    
    try:
        with open(locale_gen_file, 'r') as file:
            lines = file.readlines()
        
        for i, line in enumerate(lines):
            if line.strip() == "# en_US.UTF-8 UTF-8":
                lines[i] = "en_US.UTF-8 UTF-8\n"
                break
        
        # 写回 locale.gen 文件
        with open(locale_gen_file, 'w') as file:
            file.writelines(lines)
        
        print(GREEN("Updated /etc/locale.gen"))

        # 运行 locale-gen 命令
        run_command_in_container(("生成语言环境", "locale-gen"), distro)

        # 设置默认语言环境
        locale_conf_file = os.path.join(prefix, f"var/lib/proot-distro/installed-rootfs/{distro}/etc/default/locale")
        with open(locale_conf_file, 'w') as file:
            file.write("LANG=en_US.UTF-8\n")
        
        print(GREEN("Set default locale to en_US.UTF-8"))
    except Exception as e:
        print(RED(f"Error occurred: {e}"))
        # 如果出错，恢复原来的文件
        shutil.copy2(backup_locale_gen_file, locale_gen_file)
        print(RED("Restored the original /etc/locale.gen file."))
    finally:
        # 删除备份文件
        if os.path.exists(backup_locale_gen_file):
            os.remove(backup_locale_gen_file)
configure_locales_in_container()


# 安装并配置中文输入法
def setup_chinese_input():
    banner()
    print(GREEN("安装并配置中文输入法"))

    install_package_in_container(("fcitx5", "fcitx5-chinese-addons", 
                                  "fcitx5-frontend-gtk4", "fcitx5-frontend-gtk3", 
                                  "fcitx5-frontend-gtk2", "fcitx5-frontend-qt5"))

    prefix = os.getenv("PREFIX")
    profile = os.path.join(prefix, "var/lib/proot-distro/installed-rootfs/debian/etc/profile")
    profile_content = """# 设置 fcitx 输入法
export XMODIFIERS=@im=fcitx
export GTK_IM_MODULE=fcitx 
export QT_IM_MODULE=fcitx
"""
    add_to_file(profile, profile_content)
setup_chinese_input()

# 安装lxqt桌面环境
def setup_lxqt():
    install_package_in_container(("debconf-utils"))
    prefix = os.getenv("PREFIX")
    debconf_file = os.path.join(prefix, "local/src/proot-debian/debconf.txt")
    run_command_in_container(("设置 debconf", f"debconf-set-selections < {debconf_file}"))
    banner()
    print(GREEN("安装 LXQt 桌面环境"))
    print(YELLOW(">>> 这可能需要一段时间，请耐心等待..."))
    print(YELLOW(">>> 执行 Unpacking papirus-icon-theme 的时间额外的长，但不要担心，并不是卡死了。"))
    install_package_in_container(("lxqt"))
setup_lxqt()

banner()
print(GREEN("配置完成！"))
print(YELLOW("您可以通过运行以下命令启动和退出LXQt桌面环境："))
print(YELLOW("btx11"))
print(YELLOW("stx11"))
print("其他详细信息请查看项目主页：")