"""Module related to ssh"""
import subprocess
from enum import Enum
from pathlib import Path


class SSHKeyType(str, Enum):
    ED25519 = "ed25519"

def error_handler(response_status, err):
    match response_status:
        case 0:
            pass
        case _:
            raise ValueError(f"can't generate ssh key, {err.decode('utf-8')}")


def generate_ssh_key(
    email: str, profile_name: str, key_type: SSHKeyType = SSHKeyType.ED25519
):
    """function to generate ssh key"""
    save_loc = str(Path.home() / f".ssh/{profile_name}")
    with subprocess.Popen(
        ["ssh-keygen", "-t", key_type.value, "-C", email, "-f", save_loc],
        stderr=subprocess.PIPE,
    ) as proc:
        try:
            _, err = proc.communicate(timeout=60)
            response_status = proc.returncode
        except subprocess.TimeoutExpired as timeout_exception:
            proc.kill()
            raise ValueError("Process Hanging for too long") from timeout_exception

    error_handler(response_status, err)


def print_ssh_public_key(profile_name: str):
    """view ssh public key"""
    save_loc_pub = str(Path.home() / f".ssh/{profile_name}.pub")
    with open(save_loc_pub, "r", encoding="utf-8") as pubfile:
        print(pubfile.read())

