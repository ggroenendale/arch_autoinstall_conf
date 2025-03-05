"""Installation of Arch Linux using python to configure settings

Node js install:
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash

in lieu of restarting the shell
\. "$HOME/.nvm/nvm.sh"

nvm install 22

node -v # Should print "v22.14.0".

nvm current # Should print "v22.14.0".

npm -v # Should print "10.9.2".

apt install wezterm
apt install stow
curl https://raw.githubusercontent.com/jesseduffield/lazydocker/master/scripts/install_update_linux.sh | bash
Commandline: apt install gem
Commandline: apt install ruby-full
Commandline: apt install -y nodejs
Commandline: apt install stow
Commandline: apt install fd-find
Commandline: apt install pip
Commandline: apt install xclip xsel wl-clipboard
Commandline: apt-get install ripgrep
Commandline: apt install luarocks
Commandline: apt install libparted-dev

Commandline: apt install python3.12 python3.12-venv
Commandline: apt install python3.12-dev
geoff@geoff-ubuntu:~$ 

"""
import subprocess
import pathlib
import json

from archinstall.lib.installer import Installer
from archinstall.default_profiles.minimal import MinimalProfile
from archinstall.lib.args import ArchConfig, arch_config_handler
# from archinstall.lib.configuration import ConfigurationOutput
from archinstall.lib.models import User, Bootloader
from archinstall.lib.models.device_model import DiskLayoutConfiguration
from archinstall.lib.models.network_configuration import NetworkConfiguration
from archinstall.lib.models.profile_model import ProfileConfiguration
from archinstall.lib.interactions.disk_conf import select_disk_config
from archinstall.lib.disk.encryption_menu import DiskEncryptionMenu
from archinstall.lib.disk.filesystem import FilesystemHandler
from archinstall.lib.profile import profile_handler

# ArchConfig builder from json config
config: ArchConfig = arch_config_handler.config

# Not sure if the mountpoint here is necessary if its available in the config
MOUNTPOINT = "/mnt"
DISK_CONFIG: DiskLayoutConfiguration = select_disk_config()

data_store = {}
DISK_ENC = DiskEncryptionMenu(DISK_CONFIG.device_modifications, data_store).run()
KERNELS = ["linux"]

# initiate file handler with the disk config and the optional disk encryption config
fs_handler = FilesystemHandler(DISK_CONFIG, DISK_ENC)

# Perform all file operations
# WARNING: this will potentially format the filesystem and delete all data
fs_handler.perform_filesystem_operations()

# Define paths
GRUB_THEME_DIR = "/boot/grub/themes"
GRUB_CONFIG = "/etc/default/grub"
THEME_REPO = "https://github.com/vinceliuice/grub2-themes.git"
THEME_NAME = "tela"  # Change this if you want another theme

def run_command(command, check=True):
    """ Helper function to run shell commands """
    subprocess.run(command, shell=True, check=check)


def setup_dotfiles(username):
    """
    Clones my dotfiles from my git repository. Should include: 
    - neovim configs
    - wezterm configs

    """
    # Git repository containing dotfiles
    dotfiles_repo = "https://github.com/ggroenendale/dotfiles.git"

    user_home = f"/home/{username}"
    git_clone_cmd = f"git clone {dotfiles_repo} {user_home}/dotfiles"
    stow_cmd = f"cd {user_home}/dotfiles && stow -t {user_home} *"

    subprocess.run(["sudo", "-u", username, "bash", "-c", git_clone_cmd], check=True)
    subprocess.run(["sudo", "-u", username, "bash", "-c", stow_cmd], check=True)


def install_fonts(username):
    """ Moves fonts from dotfiles to ~/.local/share/fonts and updates font cache """
    user_home = f"/home/{username}"
    fonts_src = f"{user_home}/dotfiles/fonts"
    fonts_dest = f"{user_home}/.local/share/fonts"

    subprocess.run(["mkdir", "-p", fonts_dest], check=True)
    subprocess.run(["cp", "-r", fonts_src + "/*", fonts_dest], check=True)
    subprocess.run(["fc-cache", "-fv"], check=True)


def install_grub_and_theme():
    """
    Installs Grub bootloader
    """
    print("Installing GRUB and required packages...")
    run_command("pacman -S --noconfirm grub efibootmgr os-prober git")

    print("Creating GRUB theme directory...")
    pathlib.Path(GRUB_THEME_DIR).mkdir(parents=True, exist_ok=True)

    print(f"Cloning GRUB theme repository: {THEME_REPO}")
    run_command(f"git clone {THEME_REPO} /tmp/grub2-themes")

    print(f"Installing {THEME_NAME} theme...")
    run_command(f"cd /tmp/grub2-themes && ./install.sh --theme {THEME_NAME} --boot")

    print("Finding installed theme path...")
    theme_files = list(pathlib.Path(GRUB_THEME_DIR).rglob("theme.txt"))
    if not theme_files:
        print("ERROR: Theme not found!")
        return

    theme_path = str(theme_files[0])
    print(f"Theme path: {theme_path}")

    print("Updating GRUB configuration...")
    with open(GRUB_CONFIG, "r", encoding="utf8") as file:
        grub_config = file.readlines()

    # Modify or add GRUB_THEME setting
    new_config = []
    theme_set = False
    for line in grub_config:
        if line.startswith("GRUB_THEME="):
            new_config.append(f'GRUB_THEME="{theme_path}"\n')
            theme_set = True
        else:
            new_config.append(line)

    if not theme_set:
        new_config.append(f'GRUB_THEME="{theme_path}"\n')

    # Write updated configuration
    with open(GRUB_CONFIG, "w", encoding="utf8") as file:
        file.writelines(new_config)

    print("Regenerating GRUB configuration...")
    run_command("grub-mkconfig -o /boot/grub/grub.cfg")

    print("GRUB theme installation complete!")


def setup_nvidia():
    """
    Installs Nvidia GPU drivers and settings
    """
    # Enable early KMS for NVIDIA
    with open("/etc/mkinitcpio.conf", "r", encoding="utf8") as f:
        mk_config = f.read()
    if "nvidia" not in mk_config:
        mk_config = mk_config.replace('MODULES=()', 'MODULES=(nvidia nvidia_modeset nvidia_uvm nvidia_drm)')
    with open("/etc/mkinitcpio.conf", "w", encoding="utf8") as f:
        f.write(mk_config)
    subprocess.run(["mkinitcpio", "-P"], check=True)

    # Enable NVIDIA DRM for Wayland
    with open("/etc/default/grub", "r", encoding="utf8") as f:
        grub_config = f.read()
    if "nvidia_drm.modeset=1" not in grub_config:
        grub_config = grub_config.replace('GRUB_CMDLINE_LINUX_DEFAULT="', 'GRUB_CMDLINE_LINUX_DEFAULT="nvidia_drm.modeset=1 ')
    with open("/etc/default/grub", "w", encoding="utf8") as f:
        f.write(grub_config)
    subprocess.run(["grub-mkconfig", "-o", "/boot/grub/grub.cfg"], check=True)


def install_paru(username):
    """ Installs Paru AUR helper """
    user_home = f"/home/{username}"
    paru_cmds = [
        f"git clone https://aur.archlinux.org/paru.git {user_home}/paru",
        f"cd {user_home}/paru && makepkg -si --noconfirm"
    ]
    for cmd in paru_cmds:
        subprocess.run(["sudo", "-u", username, "bash", "-c", cmd], check=True)


# Load users from creds.json
with open("archcreds.json", "r", encoding="utf8") as file:
    creds = json.load(file)


# Start the guided installation
with Installer(
    target=MOUNTPOINT,
    disk_config=DISK_CONFIG,
    disk_encryption=DISK_ENC,
    kernels=KERNELS) as installation:
    installation.mount_ordered_layout()

    if installation.minimal_installation():
        # Set the hostname for the machine from the config file
        installation.set_hostname(hostname=config.hostname)

        # Add grub as bootloader
        installation.add_bootloader(Bootloader.Grub)
        
        # Define the network setup which should pull from the config file
        network_config: NetworkConfiguration | None = config.network_config

        if network_config:
            network_config.install_network_config(
                installation,
                config.profile_config
            )

        profile_config = ProfileConfiguration(MinimalProfile())
        profile_handler.install_profile_config(installation, profile_config)

        user = User('geoff', 'geoff', False)

        installation.create_users(user)

        # Enable services
        # for service in install_options["services"]:
        #     installation.enable_service(service)

        # Run post installation functions
        setup_dotfiles(user.username)
        install_paru(user.username)
