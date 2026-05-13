# lemonade-rpm

[![Copr Build Status](https://copr.fedorainfracloud.org/coprs/abn/lemonade/package/lemonade/status_image/last_build.png)](https://copr.fedorainfracloud.org/coprs/abn/lemonade/)

Fedora RPM packages for [Lemonade](https://github.com/lemonade-sdk/lemonade), a lightweight, high-performance local LLM server.

The source is integrated via git submodules from [lemonade-sdk/lemonade](https://github.com/lemonade-sdk/lemonade).

## Installation

This package is available via the [abn/lemonade](https://copr.fedorainfracloud.org/coprs/abn/lemonade/) Copr repository.

### Quick Start (Full Installation)

To install both the server and the desktop application:

```bash
# Enable the Copr repository
sudo dnf copr enable abn/lemonade

# Install everything
sudo dnf install lemonade
```

### Modular Installation

You can also install the components independently:

```bash
# Install only the server (headless)
sudo dnf install lemonade-server

# Install only the system tray (lightweight GTK interface)
# Note: This will automatically pull in lemonade-server as a dependency
sudo dnf install lemonade-tray

# Install only the desktop application
# Note: This will automatically pull in lemonade-server as a dependency
sudo dnf install lemonade-desktop

# Install only the web interface launcher (opens the built-in web UI in a browser)
# Note: This will automatically pull in lemonade-server as a dependency
sudo dnf install lemonade-web
```

## Post-Installation

### Core Server

The core server can run either as a system-wide service (started by root, available to all users) or as a per-user service (started by you, runs only during your session).

**System service** — suitable for servers or shared desktops:

```bash
# Start the server
sudo systemctl start lemond.service

# Enable the server to start at boot
sudo systemctl enable lemond.service
```

**User service** — suitable for personal desktops (no `sudo` required):

```bash
# Enable and start for the current user
systemctl --user enable --now lemond.service

# Stop and disable
systemctl --user disable --now lemond.service
```

The user service stores data under your home directory and reads optional environment variables (e.g. `HF_TOKEN`, `LEMONADE_API_KEY`) from `~/.config/lemonade/conf.d/*.conf`.

> **Note:** Running both the system service and the user service at the same time will cause a port conflict. Use one or the other.

### System Tray (Desktop Users)

For a graphical interface in your system tray, install the `lemonade-tray` package:

```bash
sudo dnf install lemonade-tray
```

Launch it from your application menu (search for "Lemonade Tray"), or run `lemonade-tray` directly. To have it start automatically at login, add it via your desktop environment's autostart settings (e.g. GNOME Tweaks → Startup Applications).

Once started, a Lemonade icon will appear in your system tray, providing quick access to logs, settings, and the web interface.

### Web Interface

The `lemonade-web` package installs a `lemonade-web` launcher and a desktop entry that open the server's built-in web UI in your browser. The web UI is served by `lemond` at `http://localhost:13305/lemonade` and requires the server to be running.

### Desktop Application

The `lemonade-desktop` package installs the `lemonade-app` Tauri desktop application, available from your application menu as "Lemonade Desktop". It connects to a running `lemond` instance.

System-wide configuration files are located in `/etc/lemonade/conf.d/`. For the user service, per-user overrides go in `~/.config/lemonade/conf.d/`.

## Development

This project uses [tito](https://github.com/rpm-software-management/tito) for versioning and release management.

### Building RPMs locally

To perform a test build of the RPMs:
```bash
tito build --rpm --test
```

### Releasing to COPR

To tag a new version and release to COPR:
```bash
# Tag a new release (updates spec and creates git tag)
tito tag

# Release to COPR (as configured in .tito/releasers.conf)
tito release copr
```
