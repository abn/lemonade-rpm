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


> **Note:** Running both the system service and the user service at the same time will cause a port conflict. Use one or the other.

### Configuration

Lemonade can be configured by setting environment variables in configuration drop-in files: 

* **System-wide service**: Read from `/etc/lemonade/conf.d/*.conf` (loaded in alphabetical order).
* **Per-user service**: Read from `~/.config/lemonade/conf.d/*.conf`.

#### Common Options
You can configure the server by adding options to a custom file (e.g., `50-custom.conf`):

| Variable | Description | Default (System) | Default (User) |
|---|---|---|---|
| `LEMONADE_PORT` | Port to listen on | `13305` | `13305` |
| `LEMONADE_HOST` | Host address to bind to | `127.0.0.1` | `127.0.0.1` |
| `LEMONADE_API_KEY` | Admin API key for auth | *(None)* | *(None)* |
| `LEMONADE_CACHE_DIR`| Root directory for state/cache | `/var/lib/lemonade` | `~/.cache/lemonade` |
| `HF_HOME` | Hugging Face download cache | `/var/lib/lemonade/huggingface` | `~/.cache/huggingface` |

#### Step-by-Step Example

To configure the system-wide service to use a custom port and require an API key:

1. Create a custom configuration file:
   ```bash
   sudo nano /etc/lemonade/conf.d/50-custom.conf
   ```
2. Add your settings:
   ```ini
   LEMONADE_PORT=15000
   LEMONADE_API_KEY=your_secure_admin_key
   ```
3. Restart the service to apply changes:
   ```bash
   sudo systemctl restart lemond.service
   ```

*(Note: For the per-user service, create `~/.config/lemonade/conf.d/50-custom.conf` and run `systemctl --user restart lemond.service` instead).*


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

## Upstream Differences & Migrations

### Comparison with Upstream CPack RPMs

Our packaging differs from the official monolithic RPM generated by the upstream CPack workflow in several key ways:

1. **Modular Subpackaging**: 
   * **Upstream**: Bundles everything (server, CLI, assets, desktop app) into a single monolithic `lemonade-server` package.
   * **Our RPM**: Splits components into modular subpackages (`lemonade-server`, `lemonade-tray`, `lemonade-desktop`, and `lemonade-web`). This allows headless server systems to install only the server subpackage without pulling in heavy GUI dependencies like GTK3, WebKit2GTK, Node.js, or Rust.
2. **Standard File Paths**:
   * **Upstream**: Configures the `lemonade` user with home directory `/opt/var/lib/lemonade`.
   * **Our RPM**: Follows standard Fedora guidelines, placing the user's home/state directory at `/var/lib/lemonade` (`%{_sharedstatedir}/lemonade`).
3. **Declared Dependencies**:
   * Our spec file lists complete, verified build and runtime dependencies for each component (including `jq` for the web launcher), whereas upstream's CPack package has limited hardcoded requirements.

---

### Key Changes & Migrations (Version >= 10.9.0-2)

If you are upgrading from `lemonade <= 10.9.0-1` (or migrating from the upstream CPack RPM), the package performs **automatic, safe migrations** during installation:

#### 1. Home Directory Migration (Upstream CPack to Local RPM)
* **What changed**: The `lemonade` user's home directory has been standardized to `/var/lib/lemonade`.
* **Migration**: The package post-install script automatically detects if the `lemonade` user is configured with the non-standard `/opt/var/lib/lemonade` path, stops the system service if active, updates the home directory to `/var/lib/lemonade`, and moves all existing files safely (`usermod -d -m`).

#### 2. Flattened Cache Directory (Un-nesting state files)
* **What changed**: The system service now runs with default environment variables (`LEMONADE_CACHE_DIR=/var/lib/lemonade` and `HF_HOME=/var/lib/lemonade/huggingface`) defined in `/etc/lemonade/conf.d/10-paths.conf`.
* **Migration**: Previously, config, binaries, and downloaded models were nested inside hidden directories:
  * `/var/lib/lemonade/.cache/lemonade/` (Config/Binaries)
  * `/var/lib/lemonade/.cache/huggingface/` (HuggingFace Models)
  
  Upon upgrade, the package automatically moves files from the nested `.cache/` directories to their new flat locations (`/var/lib/lemonade/` and `/var/lib/lemonade/huggingface/`) so that your configurations and downloaded models are preserved.
  
  *Note: This change does not affect the per-user service (`systemctl --user`), which continues to use standard isolated paths under user home directories.*

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
