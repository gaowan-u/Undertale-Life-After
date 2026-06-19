import os
import subprocess
import shutil

def run_cmd(cmd, timeout=5):
    """执行 shell 命令，增加超时机制防止卡死"""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=timeout
        )
        return result.returncode == 0, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return False, "命令执行超时"
    except Exception as e:
        return False, str(e)

def fix_pulseaudio():
    prefix = os.environ.get('PREFIX')
    if not prefix:
        return False, "错误：未在 Termux 环境中运行。"
    home = os.path.expanduser('~')

    # 1. 检查安装 (安装过程可能较慢，超时设为60秒)
    if not shutil.which('pulseaudio'):
        success, msg = run_cmd("pkg install -y pulseaudio", timeout=60)
        if not success:
            return False, f"安装失败: {msg}"

    # 2. 尝试清理僵死进程 (防止后续 pactl info 卡死)
    run_cmd("pulseaudio -k", timeout=3)

    # 3. 检查运行状态 (带超时保护)
    success, msg = run_cmd("pactl info")
    if success and "Server Name: pulseaudio" in msg:
        return True, "状态正常：PulseAudio 已在运行。"

    # 4. 清理残留状态文件
    paths_to_clean = [
        os.path.join(home, '.config', 'pulse'),
        os.path.join(prefix, 'var', 'run', 'pulse')
    ]
    for path in paths_to_clean:
        if os.path.exists(path):
            shutil.rmtree(path, ignore_errors=True)

    # 5. 补全环境变量
    runtime_dir = os.path.join(prefix, 'var', 'run')
    os.makedirs(runtime_dir, exist_ok=True)
    os.environ['XDG_RUNTIME_DIR'] = runtime_dir

    # 6. 智能修复配置文件
    conf_dir = os.path.join(prefix, 'etc', 'pulse')
    os.makedirs(conf_dir, exist_ok=True)
    conf_file = os.path.join(conf_dir, 'default.pa')

    need_rewrite = True
    if os.path.exists(conf_file):
        with open(conf_file, 'r', encoding='utf-8') as f:
            if 'module-aaudio-sink' in f.read() or 'module-sles-sink' in f.read():
                need_rewrite = False

    if need_rewrite:
        minimal_config = (
            "load-module module-native-protocol-unix\n"
            "load-module module-device-restore\n"
            ".ifexists module-sles-sink.so\nload-module module-sles-sink\n.endif\n"
            ".ifexists module-aaudio-sink.so\nload-module module-aaudio-sink\n.endif\n"
        )
        with open(conf_file, 'w', encoding='utf-8') as f:
            f.write(minimal_config)

    # 7. 启动并验证
    run_cmd("pulseaudio --start --exit-idle-time=-1")
    success, msg = run_cmd("pactl info")

    if success and "Server Name: pulseaudio" in msg:
        return True, "修复成功：PulseAudio 已正常启动。"
    return False, f"修复失败，日志：\n{msg}"

if __name__ == "__main__":
    is_ok, info = fix_pulseaudio()
    print(info)
