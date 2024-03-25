# Installation
```
pip install git+https://github.com/yeyinthtoon/git-ssh-profile-manager.git
```
# Command
```
git-ssh-profile-manager --help
git-ssh-profile-manager add-new-includeif-rules --help
git-ssh-profile-manager create-profile --help
```
# Notes
* If there is an agent already running, this command is not necessary 'eval "$(ssh-agent -s)".
* If old profiles are not working, check with the below command to see whether ssh identity is registered in active agent.
    ```
    ssh-add -l
    ```
* If old profiles are not active, you can register to ssh agent by
    ```
    ssh-add ~/.ssh/profile_name
    ```
