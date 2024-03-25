from enum import Enum
from pathlib import Path
from typing import Annotated, Dict, List, Optional

import typer

from git_ssh_profile_manager.gitconfigs_manager import (
    build_detail_configs,
    parse_gitconfig,
    serialize_config,
)
from git_ssh_profile_manager.ssh_manager import (
    generate_ssh_key,
    print_ssh_public_key,
)

app = typer.Typer()
BaseGitConfigFilePath = Path.home() / ".gitconfig"
GitConfigsDir = Path.home() / ".gitconfigs"
if not GitConfigsDir.exists():
    GitConfigsDir.mkdir(parents=True)

# FIXME: work around for creating dynamic enum
_, include_if_configs_global = parse_gitconfig(BaseGitConfigFilePath)
profiles_dict: Dict = {}
for profile in include_if_configs_global.keys():
    stem = Path(profile).stem[1:]
    profiles_dict[stem.capitalize()] = stem
Profiles = Enum("Profiles", profiles_dict)
del include_if_configs_global, profiles_dict


@app.command()
def create_profile(
    email: str,
    user_name: str,
    github_user_name: str,
    profile_name: str,
    gitdirs: Annotated[Optional[List[str]], typer.Option()] = None,
    onbranchs: Annotated[Optional[List[str]], typer.Option()] = None,
    remote_urls: Annotated[Optional[List[str]], typer.Option()] = None,
):
    if not (gitdirs or onbranchs or remote_urls):
        print(
            "At least one of the arguments (gitdirs, onbranchs, remote_urls) must be presented."
        )
        raise typer.Exit(255)
    git_config_for_profile = GitConfigsDir / f".{profile_name}"
    if git_config_for_profile.exists():
        print(f"ALready Exit, profile: {profile_name}")
        raise typer.Exit(255)
    generate_ssh_key(email=email, profile_name=profile_name)
    configs, include_if_configs = parse_gitconfig(BaseGitConfigFilePath)
    include_if_configs[str(git_config_for_profile)] = []
    if gitdirs:
        for gitdir in gitdirs:
            if not gitdir.endswith("/"):
                gitdir += "/"
            include_if_configs[str(git_config_for_profile)].append(("gitdir", gitdir))
    if onbranchs:
        for onbranch in onbranchs:
            include_if_configs[str(git_config_for_profile)].append(
                ("onbranch", onbranch)
            )
    if remote_urls:
        for remote_url in remote_urls:
            include_if_configs[str(git_config_for_profile)].append(
                ("hasconfig:remote.*.url", remote_url)
            )
    config_str = serialize_config(configs, include_if_configs)
    with open(BaseGitConfigFilePath, "w", encoding="utf-8") as bgcf:
        bgcf.write(config_str)

    detail_configs = build_detail_configs(
        user_name, email, github_user_name, profile_name
    )

    detail_config_str = serialize_config(detail_configs, {})

    with open(git_config_for_profile, "w", encoding="utf-8") as gcfp:
        gcfp.write(detail_config_str)

    print(
        "Please run this command to add your ssh key to agent.\n"
        f'eval "$(ssh-agent -s)" \nssh-add {Path.home()/".ssh"/profile_name}'
    )

    print(f"User profile {profile_name} is created successfully.")
    print("update this public key with your remote server")
    print_ssh_public_key(profile_name)


@app.command()
def add_new_includeif_rules(
    profile_name: Profiles,
    gitdirs: Annotated[Optional[List[str]], typer.Option()] = None,
    onbranchs: Annotated[Optional[List[str]], typer.Option()] = None,
    remote_urls: Annotated[Optional[List[str]], typer.Option()] = None,
):
    if not (gitdirs or onbranchs or remote_urls):
        print(
            "At least one of the arguments (gitdirs, onbranchs, remote_urls) must be presented."
        )
        raise typer.Exit(255)

    configs, include_if_configs = parse_gitconfig(BaseGitConfigFilePath)
    git_config_for_profile = GitConfigsDir / f".{profile_name.value}"

    if gitdirs:
        for gitdir in gitdirs:
            if not gitdir.endswith("/"):
                gitdir += "/"
            include_if_configs[str(git_config_for_profile)].append(("gitdir", gitdir))
    if onbranchs:
        for onbranch in onbranchs:
            include_if_configs[str(git_config_for_profile)].append(
                ("onbranch", onbranch)
            )
    if remote_urls:
        for remote_url in remote_urls:
            include_if_configs[str(git_config_for_profile)].append(
                ("hasconfig:remote.*.url", remote_url)
            )
    config_str = serialize_config(configs, include_if_configs)
    with open(BaseGitConfigFilePath, "w", encoding="utf-8") as bgcf:
        bgcf.write(config_str)


def cli_main():
    app()


if __name__ == "__main__":
    cli_main()
