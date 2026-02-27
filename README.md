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

# Enable the Electron Copr repository (required for lemonade-app)
sudo dnf copr enable sergiomb/electrons

# Install everything
sudo dnf install lemonade
```

### Modular Installation

You can also install the components independently:

```bash
# Install only the server (headless)
sudo dnf install lemonade-server

# Install only the desktop application
# Note: This will automatically pull in lemonade-server as a dependency
sudo dnf copr enable sergiomb/electrons
sudo dnf install lemonade-app
```

## Post-Installation

### Core Server

The core server runs as a system-wide service:

```bash
# Start the server
sudo systemctl start lemonade-server

# Enable the server to start at boot
sudo systemctl enable lemonade-server
```

### System Tray (Desktop Users)

For a graphical interface in your system tray, you can enable the user-level tray service. **Note:** The core `lemonade-server` system service **must** be running for the tray to start successfully:

```bash
# Enable and start the tray for the current user
systemctl --user enable --now lemonade-tray
```

Once started, a Lemonade icon will appear in your system tray, providing quick access to logs, settings, and the web interface.

Configuration files are located in `/etc/lemonade/`.

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
