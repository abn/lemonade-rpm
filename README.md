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
# Install only the command-line interface (CLI client)
sudo dnf install lemonade-cli

# Install only the system service server (headless multi-tenant background service)
# Note: This will automatically pull in lemonade-cli as a dependency
sudo dnf install lemonade-server

# Install only the embedded standalone server (portable, single-user, self-contained server)
# Note: Conflicts with lemonade-server; works with lemonade-web, tray, desktop, and cli
sudo dnf install lemonade-server-embedded

# Install only the system tray (lightweight GTK interface)
# Note: Requires lemonade-server or lemonade-server-embedded
sudo dnf install lemonade-tray

# Install only the desktop application
# Note: Requires lemonade-server or lemonade-server-embedded
sudo dnf install lemonade-desktop

# Install only the web interface launcher (opens the built-in web UI in a browser)
# Note: Requires lemonade-server or lemonade-server-embedded
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


> **Note:** Running both the system service and the user service at the same time will cause a port conflict. Use one or the other.

### Configuration

Lemonade server settings (port, host, model directory, routing options, etc.) are managed in `config.json` (located in the state directory) and CLI arguments. Environment variables and secrets (such as API keys and authentication tokens) can be configured via service environment files or systemd drop-ins:

* **System-wide service (`lemond.service`)**:
  - Environment file: `/etc/default/lemond` (loaded via `EnvironmentFile=-/etc/default/lemond`).
  - Drop-ins: `sudo systemctl edit lemond.service`.
  - State directory: `/var/lib/lemonade` (`StateDirectory=lemonade`).
  - Cache directory: `/var/cache/lemonade` (`CacheDirectory=lemonade`).
  - Hugging Face cache: `/var/cache/huggingface` (`Environment=HF_HOME=/var/cache/huggingface`).
* **Per-user service (`systemctl --user lemond.service`)**:
  - Environment file: `~/.config/lemonade/lemond.conf` (loaded via `EnvironmentFile=-%E/lemonade/lemond.conf`).
  - Drop-ins: `systemctl --user edit lemond.service`.
  - Standard XDG paths: `~/.local/share/lemonade`, `~/.cache/lemonade`, `~/.cache/huggingface`.

#### Common Environment Variables
Configure server secrets and upstream token variables in `/etc/default/lemond` (system) or `~/.config/lemonade/lemond.conf` (user):

| Variable | Description | Default (System) | Default (User) |
|---|---|---|---|
| `HF_TOKEN` | Hugging Face authentication token | *(None)* | *(None)* |
| `LEMONADE_API_KEY` | Require API key authentication on all routes | *(None)* | *(None)* |
| `LEMONADE_ADMIN_API_KEY` | API key specific to administrative routes | *(None)* | *(None)* |
| `LEMONADE_CACHE_DIR` | Base directory for backend caches | `/var/cache/lemonade` | `~/.cache/lemonade` |
| `HF_HOME` | Hugging Face model download cache | `/var/cache/huggingface` | `~/.cache/huggingface` |

#### Step-by-Step Example

To configure the system-wide service with an API key and Hugging Face token:

1. Edit `/etc/default/lemond`:
   ```bash
   sudo nano /etc/default/lemond
   ```
2. Add your settings:
   ```ini
   HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   LEMONADE_API_KEY=your_secure_api_key
   ```
3. Restart the service to apply changes:
   ```bash
   sudo systemctl restart lemond.service
   ```

*(Note: For the per-user service, edit `~/.config/lemonade/lemond.conf` and run `systemctl --user restart lemond.service` instead).*


### Command-Line Interface (CLI)

The `lemonade-cli` package installs the `lemonade` command-line client, which allows you to interact with a running Lemonade server (`lemond`):

```bash
sudo dnf install lemonade-cli
```

Use `lemonade --help` to list all available commands.

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

Desktop application settings are stored under the standard XDG path `~/.config/lemonade/app_settings.json` (with automatic forward migration from legacy `~/.cache/lemonade/app_settings.json`).

## Upstream Differences & Migrations

### Comparison with Upstream CPack RPMs

Our packaging differs from the official monolithic RPM generated by the upstream CPack workflow in several key ways:

1. **Modular Subpackaging**: 
   * **Upstream**: Bundles everything (server, CLI, assets, desktop app) into a single monolithic `lemonade-server` package.
   * **Our RPM**: Splits components into modular subpackages (`lemonade-server`, `lemonade-server-embedded`, `lemonade-cli`, `lemonade-tray`, `lemonade-desktop`, and `lemonade-web`). This allows headless server systems to install only the server or CLI subpackage without pulling in heavy GUI dependencies like GTK3, WebKit2GTK, Node.js, or Rust.
2. **Native Fedora System Integration & Standard Paths**:
   * **Upstream CPack RPM**: Uses legacy scripts (such as `/opt/var/lib/lemonade` user home setup) without Fedora packaging macros or modular subpackages.
   * **Our RPM**: Follows standard Fedora packaging guidelines:
     * System user provisioning via native `systemd-sysusers` (`%{_sysusersdir}/lemonade.conf`).
     * State directory: `/var/lib/lemonade` (`StateDirectory=lemonade`).
     * Cache directory: `/var/cache/lemonade` (`CacheDirectory=lemonade`).
     * Model cache: `/var/cache/huggingface` (`Environment=HF_HOME=/var/cache/huggingface`).
     * System secrets: `/etc/default/lemond` (`EnvironmentFile=-/etc/default/lemond`).
     * Desktop app settings: `~/.config/lemonade/app_settings.json`.
3. **Declared Dependencies & System Hardening**:
   * Our spec file lists complete, verified build and runtime dependencies for each component (including `jq` for the web launcher, and hardware acceleration utilities).
   * Services include systemd sandboxing (`PrivateTmp`, `ProtectSystem`, `ProtectHome`, `RestrictNamespaces`, `AmbientCapabilities=CAP_SYS_RESOURCE`) and automatic membership in `render` and `video` groups.

---

### Key Changes & Migrations

The package performs **automatic, safe migrations** during installation and upgrades:

#### 1. Home Directory Migration (Upstream CPack to Local RPM)
* **What changed**: The `lemonade` user's home directory is standardized to `/var/lib/lemonade`.
* **Migration**: The package post-install script automatically detects if the `lemonade` user is configured with the non-standard `/opt/var/lib/lemonade` path, stops the system service if active, updates the home directory to `/var/lib/lemonade`, and moves existing files safely (`usermod -d -m`).

#### 2. Cache Directory Migration
* **What changed**: System service caches and models are moved out of hidden legacy paths (`/var/lib/lemonade/.cache/`).
* **Migration**: Upon upgrade, the package automatically migrates legacy `.cache/lemonade/` and `.cache/huggingface/` data to `/var/lib/lemonade/` and `/var/lib/lemonade/huggingface/`.

#### 3. GPU/NPU Hardware Acceleration Group Memberships
* **What changed**: To access direct rendering devices (like AMD GPUs, Ryzen NPUs, and Intel/NVIDIA cards) at `/dev/dri/renderD*`, the system service user must belong to the appropriate group.
* **Upgrade action**: The post-install script automatically adds the system `lemonade` user to the `render` and `video` groups (if they exist on the host) so that hardware acceleration works out of the box.

#### 4. Tauri Desktop App Configuration Path
* **What changed**: The Tauri desktop interface (`lemonade-desktop`) now stores settings under the standard XDG path `~/.config/lemonade/app_settings.json` instead of `~/.cache/lemonade/app_settings.json`. Settings are automatically migrated forward on first launch.

## Development

This project uses [tito](https://github.com/rpm-software-management/tito) for versioning and release management.

### Building RPMs locally

You can perform a test build of the RPMs either directly on your host (if all dependencies are installed) or inside a container.

**Option A: Container Build (Recommended)**
Always commit your changes to Git first (Tito only builds committed files), then run:
```bash
# 1. Start the rpmbuilder container in the background
podman run -d --rm -i --name rpmbuilder-lemonade -v ${PWD}:/sources:z quay.io/abn/rpmbuilder:fedora-44 sleep inf

# 2. Trigger the build inside the container
podman exec rpmbuilder-lemonade rpmbuilder
```
The built RPM packages will be located in `/output` inside the container.

**Option B: Host Build**
```bash
# Tito only builds committed changes
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
