# Arch Linux install and Setup

I am making the move to Arch Linux and I will be handling a lot of the installation using the configurations and
scripts found in this repository.

## Overview of Whats Included

---

### Desktop Environment -> Custom

I may come to regret this decision but I have decided to essentially combine all of the things I would normally
get with a desktop environment and just put in place each one that I want. I think I have a problem with
installing a monolithic piece of software with a bunch of dependencies that may become hard to manage as time
goes on. I think this will also give me more flexibility as I go through the process of setting up Arch the way
I want it.

I especially like the idea of updating 1 part of my configuration and not having the entire component of software
fail. However, I can picture some issues arising if two components rely on one library and one of those components
needs a different version of that library. If for example Waybar and Hyprland each need a different version of
Python and installing the newer version and removing the older version somehow breaks one of those components.

But we will cross that bridge when or if we get to it.

#### Terminal -> Wezterm

Wezterm is my preferred terminal. I like that it is customizable in lua which is just a delightful easy language.

#### Window Manager -> Hyprland

Hyprland is the goat and I am excited to get into customizing it.

#### App Launcher -> Fuzzel or Walker

I decided to go with fuzzel. It's wayland native which should jive well with Hyprland which also depends on
Wayland. It can also be customized using a fuzzel.ini file in `.config/fuzzel`. I've also been looking at Walker
which seems to have more recent development and might be less resource intensive. I am not sure yet.

#### Authentication Agent -> hyprpolkitagent

The thing that pops up when you need to authenticate something.

#### File Manager -> Thunar

I'm not real sure on File Managers. I know that I'm not super satisfied with Nautilus and Dolphin seems like its
a bit too heavy for what I need. Thunar also seems pretty extensible so I think for now we will go with that.

#### Panels, System Tray, & Widgets -> Waybar & Eww

Waybar is also Wayland based and works with Hyprland and Fuzzel. I'm also including Eww as well for custom
widgets.

#### Notifications -> Mako

Seen this recommended a couple times for notifications.

#### Settings & System Configuration -> Several

I first want to note `xdg-desktop-portal-hyprland` and I will explain more about what it does another time

#### Wallpaper -> swww

It seems to have the most customization and I think it supports animated wallpapers. Also seems to make it easy
to switch wallpapers or write a script that changes them.

#### Clipboard -> clipman + wl-clip-persist

I am still unsure between clipman and cliphist which one is best, because cliphist is able to copy images to the
clipboard but with clipman I at least found a simple config to tie it with fuzzel. wl-clip-persist extends the
history for the clipboard to include stuff even if an application closes.

### Browser -> LibreWolf + Zen Browser

This decision was more in the realm of what is performant and privacy focused but also helps me as a web app
developer. So far I am looking at Librewolf for the privacy focus and I also like Thorium. I may also install Zen
browser depending on if I want something that is quiet and nice to use.

After some testing I found LibreWolf to be faster than Thorium on Ubuntu 22.04. I found Thorium to be a bit
buggy with some graphical errors. It may be some configuration issues or some miscommunication with Nvidia.
But for simplicity I am going to stick with LibreWolf.

I also tested Zen browser and I really like it. I could see using Zen browser as a replacement for installing
the Spotify Linux app or other desktop apps.

### Development tools

#### Neovim

#### k3s

#### kdash

### Other Packages

This will mostly serve as a space for me to remember all of the tools that I use and dump some things from my brain.

A list of packages I need to install that are particularly necessary as libraries or installers

- cargo
- nvm
- npm
- nodejs
- helm
- gem
- ruby-full
- stow
- fd-find
- ripgrep
- luarocks
- libparted-dev
- Spark
- Zot (OCI Container registry)
- Podman
- gawk (makes bash config editing scripts work)

## Installation

---

### Reasons for using Archinstall

For starters I am moving away from Ubuntu to Arch Linux. I started to experiment with Neovim and found hyprland
also interesting and I have wanted to create a custom setup for a long while now. I think I will find comfort in
being able to install the packages piece by piece and understanding a bit more of the underlying pieces and
hopefully that will lead to a faster system. I have also found some things I didn't like with Ubuntu like the
move to Snap. I am sure there are a litany of other solutions I could go with including staying with Ubuntu and
using Neovim there and I could probably setup hyprland as well. Or I could move to one of the "almost Arch"
distros. But ultimately the amount of time spent researching and discovery into finding the right distro could
instead be spent going with Arch where I could research the individual packages I want and creating my forever
Operating System.

This move to Arch also coincides with moving my home network server from Ubuntu to Debian.

I chose to handle the installation this way rather than going the manual route and reading the wiki to make sure
this process is repeatable and editable as I learn how to use Arch and Install it. The whole idea of a "Forever
Operating System" being that I will continually modify my configuration and the applications I use, and get really
comfortable with wiping and reinstalling Arch.

I know that for myself in the event that the installation doesn't work or I don't like something I will give up
and move to a different Linux distro.

### Process

---

How this works is we begin with an Arch ISO that we will modify before running the scripts in this repository
and installing some of its requirements, namely `python 3.12` and the 3.0.2 version of `archinstall` from their git
repository.

However we first need to begin with `archiso` as that is what we will use to modify the ISO to begin with in order
to automate the rest of the process.

### Pre-Installation

---

To begin with, we will start with an Arch ISO and load it onto a Ventoy USB. Ventoy is a tool that can store
several ISO's onto a USB drive that you can then choose from when you boot from that USB. The idea being that
it will be easier in the future to add ISO's to your usb and you don't have to constantly reformat the USB.

Ventoy creates an exFAT or NTFS parition by default and we can save iso files and any other file onto this partition
which will become important as we create and add our other files to modify this ISO as well as other ISO's.
Downloading Ventoy from their [downloads page](https://www.ventoy.net/en/download.html) gives us a tar.gz file that we need to extract.

```bash
tar -xvzf ventoy-1.1.05-linux.tar.gz
```

Which creates a `ventoy-1.1.05-linux` folder in the working directory your terminal is in. I moved this to my home
directory.

```bash
mv ventoy-1.1.05-linux ~/ventoy
```

This also renamed the folder containing everything to just ventoy making the later scripts a bit easier.

Next we need our usb drive. I am using a 256GB drive for this. In order to make sure I have the right device name
I used the `lsblk` command and found my usb device at `/dev/sdc`. Another useful command is `sudo fdisk -l` to list
out all disks and partitions on your device.

Now we can install ventoy onto the `/dev/sdc` usb drive.

```bash
cd ~/ventoy
sudo sh Ventoy2Disk.sh -i /dev/sdc
```

From here, the Ventoy usb should be available to add files onto from your machine. I created a folder for my
ArchLinux iso and additional files.

```
Ventoy-USB/
├── ventoy/
│   └── ventoy.json
├── ArchLinux/
│   ├── InstallScripts/
│   │   └── setup.sh
│   ├── archlinux-version-x86_64.iso
│   └── archlinux-version-x86_64.iso.sig
└── Debian/
    ├── InstallScripts/
    │   └── setup.sh
    └── debian-version-amd64-DVD-1.iso
```

### Installation

---

#### Archiso install

To begin with we need to be working within the Arch iso.

```bash
sudo pacman -S archiso


```

#### Python 3.12

The Arch Linux ISO version that I am currently working with is `2025.03.01` and this comes with Python 3.13.2 so
this should work out of the box for our script.

However if we need to fix the installation, and we are inside the barebones iso we can install Python to the iso
and rebuild it.

```bash
pacman -Sy python
```

#### Archinstall

Now retrieve the 3.0.2 zip file from github.

```bash
curl https://github.com/archlinux/archinstall/archive/refs/tags/3.0.2.zip -o /tmp/archinstall.zip
unzip /tmp/archinstall.zip
```

This will download the 3.0.2 version into the `/tmp` directory and then unzip it into the working directory as the
folder `archinstall`

We then need to navigate into the new archinstall folder and pip install its contents

```bash
cd archinstall
pip install .
```
