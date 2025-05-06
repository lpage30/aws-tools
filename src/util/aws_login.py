import subprocess
from util.logging import get_default_logger


def aws_sso_login(profile: str, region: str|None = None, timeout_s = 30) -> bool:
    command_line = ["aws", "sso", "login", "--profile", profile]
    if not region is None:
        command_line.append('--region')
        command_line.append(region)
    try:
        subprocess.run(command_line, timeout=timeout_s, check=True)
        return True
    except Exception:
        get_default_logger().exception(f"Failed {' '.join(command_line)}")
        return False    
