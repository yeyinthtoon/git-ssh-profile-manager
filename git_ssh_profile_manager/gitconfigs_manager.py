"""module related to gitconfigs"""

from pathlib import Path
from collections import defaultdict, OrderedDict
from typing import Dict, List, Tuple


def parse_gitconfig(
    gitconfig_file_path: Path,
) -> Tuple[Dict[str, Dict], Dict[str, List]]:
    """parse gitconfig file"""
    configs_dict: Dict[str, Dict] = defaultdict(dict)
    includeif_config_dict: Dict[str, List] = OrderedDict()
    if not gitconfig_file_path.exists():
        return configs_dict, includeif_config_dict
    with open(gitconfig_file_path, "r", encoding="utf-8") as gcf:
        gitconfigs = gcf.read()

    for paragraph in gitconfigs.split("["):
        if paragraph.startswith("includeIf"):
            keyword, value = None, None
            for line in paragraph.split("\n"):
                line = line.strip()
                if len(line) == 0:
                    continue
                if line.startswith("includeIf"):
                    splited_line = line.strip("]").split('"')
                    if len(splited_line) != 3:
                        raise NotImplementedError()
                    cond = splited_line[1].split(":")
                    if not (len(cond) == 2 or len(cond) == 4):
                        raise NotImplementedError()
                    if len(cond) == 2:
                        keyword, value = cond
                    else:
                        keyword = ":".join(cond[:2])
                        value = ":".join(cond[2:])
                elif not (keyword and value):
                    raise NotImplementedError()
                else:
                    splited_line = line.split("=")
                    if len(splited_line) != 2:
                        raise NotImplementedError()
                    key = str(Path(f"{splited_line[1].strip()}").expanduser())
                    if key not in includeif_config_dict:
                        includeif_config_dict[key] = []
                    includeif_config_dict[key].append((keyword, value))
                    keyword, value = None, None

        else:
            header = None
            for line in paragraph.split("\n"):
                line = line.strip()
                if len(line) == 0:
                    continue
                if line.endswith("]"):
                    header = line.strip("]")
                elif not header:
                    raise NotImplementedError()
                else:
                    splited_line = line.split("=")
                    if len(splited_line) != 2:
                        raise NotImplementedError()
                    configs_dict[header][splited_line[0].strip()] = splited_line[
                        1
                    ].strip()

    return configs_dict, includeif_config_dict


def serialize_config(configs: Dict[str, Dict], includeif_configs: Dict[str, List]):
    """serialize gitconfigs back to string"""
    strs = []
    for key, rules in includeif_configs.items():
        for rule in rules:
            rule = f'[includeIf "{":".join(rule)}"]'
            strs.append(rule)
            strs.append(f"    path = {key}")
    
    for key, config in configs.items():
        strs.append(f"[{key}]")
        for subkey, subval in config.items():
            strs.append(f"    {subkey} = {subval}")
    strs.append("")
    return "\n".join(strs)


def build_detail_configs(user_name, email, github_user_name, profile_name):
    return {
        "user": {"name": user_name, "email": email},
        "github": {"user": github_user_name},
        "core": {"sshCommand": f"ssh -i ~/.ssh/{profile_name}"},
    }


if __name__ == "__main__":
    # a, b = parse_gitconfig(Path("/mnt/c/Users/Htoon/Downloads/gits/.gitconfig"))
    # a, b = parse_gitconfig(Path("/mnt/c/Users/Htoon/Downloads/gits/.gitconfigs/.gitconfig-personal"))
    # print(a)
    # print(b)
    # print(serialize_config(a, b))

    a, b = parse_gitconfig(Path("/mnt/c/Users/Htoon/Downloads/gits/.gitconfig"))
    print(a, b)
    print(
        Path("~/.gitconfigs/.gitconfig-genie").expanduser()
        == (Path.home() / ".gitconfigs/.gitconfig-genie").expanduser()
    )
    print((Path.home() / ".gitconfigs/.gitconfig-genie").expanduser())
