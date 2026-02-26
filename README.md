# lemonade-server-rpm

[![Copr Build Status](https://copr.fedorainfracloud.org/coprs/abn/lemonade/package/lemonade-server/status_image/last_build.png)](https://copr.fedorainfracloud.org/coprs/abn/lemonade/)

Fedora RPM packages for [Lemonade](https://github.com/lemonade-sdk/lemonade), a lightweight, high-performance local LLM server.

The source is integrated via git submodules from [lemonade-sdk/lemonade](https://github.com/lemonade-sdk/lemonade).

## Installation

This package is available via the [abn/lemonade](https://copr.fedorainfracloud.org/coprs/abn/lemonade/) Copr repository.

```bash
# Enable the Copr repository
sudo dnf copr enable abn/lemonade

# Install the server
sudo dnf install lemonade-server

# Optional: Install the desktop application
sudo dnf install lemonade-server-app
```

## Post-Installation

The server can be managed via systemd:

```bash
# Start the server
sudo systemctl start lemonade-server

# Enable the server to start at boot
sudo systemctl enable lemonade-server
```

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
