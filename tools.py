import os
import shutil
import sh
from colorama import init, Fore, Style

init()

def GREEN(text):
    return Fore.GREEN + text + Style.RESET_ALL

def RED(text):
    return Fore.RED + text + Style.RESET_ALL

def YELLOW(text):
    return Fore.YELLOW + text + Style.RESET_ALL

def BLUE(text):
    return Fore.BLUE + text + Style.RESET_ALL

def BORDER(text):
    return Fore.CYAN + text + Style.RESET_ALL

def banner():
    # 清空终端的输出内容
    print("\033c", end="")
    banner_text = r"""
██████╗ ██████╗  ██████╗  ██████╗ ████████╗    ██████╗ ███████╗██████╗ ██╗ █████╗ ███╗   ██╗
██╔══██╗██╔══██╗██╔═══██╗██╔═══██╗╚══██╔══╝    ██╔══██╗██╔════╝██╔══██╗██║██╔══██╗████╗  ██║
██████╔╝██████╔╝██║   ██║██║   ██║   ██║       ██║  ██║█████╗  ██████╔╝██║███████║██╔██╗ ██║
██╔═══╝ ██╔══██╗██║   ██║██║   ██║   ██║       ██║  ██║██╔══╝  ██╔══██╗██║██╔══██║██║╚██╗██║
██║     ██║  ██║╚██████╔╝╚██████╔╝   ██║       ██████╔╝███████╗██████╔╝██║██║  ██║██║ ╚████║
╚═╝     ╚═╝  ╚═╝ ╚═════╝  ╚═════╝    ╚═╝       ╚═════╝ ╚══════╝╚═════╝ ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝
                                                                                            
"""
    print(GREEN(banner_text))
    print(GREEN("Welcome to the Proot-Debian script!"))
    print(GREEN("code by @LuTong"))

def run_command_in_container(command):
    task_name = command[0]
    command = command[1]
    print(GREEN(f"工作在PRoot-distro容器中"))
    print(GREEN(f"当前执行: {task_name}"))
    print(GREEN(f"shell: 【{command}】\n"))
    try:
        sh.proot_distro("login", "debian", "--", "/bin/sh", "-c", command)
    except sh.ErrorReturnCode as e:
        print(Fore.RED + f"Failed to run command: {e}" + Style.RESET_ALL)

def run_command(command):
    task_name = command[0]
    command = command[1]
    print(GREEN(f"当前执行: {task_name}"))
    print(GREEN(f"shell: 【{command}】\n"))
    try:
        sh.bash("-c", command)
    except sh.ErrorReturnCode as e:
        print(Fore.RED + f"Failed to run command: {e}" + Style.RESET_ALL)

def add_to_file(path, content):
    backup_path = path + ".bak"
    
    # 备份文件
    if os.path.exists(path):
        shutil.copy2(path, backup_path)
    
    try:
        # 追加内容到文件末尾，如果文件不存在则创建文件
        with open(path, "a") as f:
            f.write(content)
    except Exception as e:
        print(f"Error occurred: {e}")
        # 如果出错，将文件还原
        if os.path.exists(backup_path):
            shutil.copy2(backup_path, path)
        raise
    finally:
        # 删除备份文件
        if os.path.exists(backup_path):
            os.remove(backup_path)

def ask_confirmation(prompt, default="yes"):
    valid = {"yes": True, "y": True, "no": False, "n": False}
    if default is None:
        prompt = f"{prompt} [y/n] "
    elif default == "yes":
        prompt = f"{prompt} [Y/n] "
    elif default == "no":
        prompt = f"{prompt} [y/N] "
    else:
        raise ValueError(f"Invalid default answer: '{default}'")

    while True:
        choice = input(prompt).strip().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            print("请输入 'yes'、'no' (或者 'y'、'n')。")

def create_quick_command(**kwargs):
    src_files = ["btx11", "stx11"]
    dest_dir = os.path.join(os.getenv("PREFIX"), "bin")

    for file in src_files:
        src_path = os.path.join(os.getcwd(), file)
        dest_path = os.path.join(dest_dir, file)

        try:
            # 读取文件内容并进行替换
            with open(src_path, 'r') as f:
                content = f.read()
            if file == "btx11":
                content = content.replace("<USER-HOME>", kwargs.get("USER_HOME", ""))
                content = content.replace("<USER>", kwargs.get("USER", ""))

            # 将替换后的内容写入目标文件
            with open(dest_path, 'w') as f:
                f.write(content)

            # 赋予启动权限
            os.chmod(dest_path, 0o755)
            print(Fore.GREEN + f"Successfully copied {file} to {dest_dir} and set executable permissions." + Style.RESET_ALL)
        except Exception as e:
            print(Fore.RED + f"Failed to copy {file} to {dest_dir}: {e}" + Style.RESET_ALL)

    

def install_package(packages, pkg=False):
    banner()
    for package in packages:
        print(GREEN(f"Installing {package}..."))
        try:
            # 运行安装命令
            if pkg:
                sh.pkg("install", "-y", package)
            else:
                sh.sudo("apt-get", "install", "-y", package)
            # 检测包是否成功安装
            result = sh.which(package)
            if result:
                print(GREEN(f"{package} installed successfully."))
            else:
                print(RED(f"Failed to install {package}."))
        except sh.ErrorReturnCode as e:
            print(RED(f"Failed to install {package}: {e}"))

def install_package_in_container(packages, distro="debian"):
    banner()
    for package in packages:
        print(GREEN(f"Installing {package} in {distro} container..."))
        try:
            # 运行安装命令
            command = f"apt install -y {package}"
            sh.proot_distro("login", distro, "--", "/bin/sh", "-c", command)
            # 检测包是否成功安装
            check_command = f"which {package}"
            result = sh.proot_distro("login", distro, "--", "/bin/sh", "-c", check_command).strip()
            if result:
                print(GREEN(f"{package} installed successfully in {distro} container."))
            else:
                print(RED(f"Failed to install {package} in {distro} container."))
        except sh.ErrorReturnCode as e:
            print(RED(f"Failed to install {package} in {distro} container: {e}"))
