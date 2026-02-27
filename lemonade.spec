Name:           lemonade
Version:        9.3.4
Release:        5
Summary:        Lightweight, high-performance local LLM server
License:        Apache-2.0
URL:            https://lemonade-server.ai/
Source0:        lemonade-%{version}.tar.gz
Patch0:         001-linux-tray.patch
Patch1:         002-rename-app.patch
Patch2:         003-fix-terminal-call.patch

%define debug_package %{nil}

BuildRequires:  cmake
BuildRequires:  ninja-build
BuildRequires:  gcc-c++
BuildRequires:  libcurl-devel
BuildRequires:  libzstd-devel
BuildRequires:  nlohmann-json-devel >= 3.11.3
BuildRequires:  cli11-devel >= 2.4.2
BuildRequires:  cpp-httplib-devel >= 0.26.0
BuildRequires:  desktop-file-utils
BuildRequires:  libappstream-glib
BuildRequires:  systemd-rpm-macros
BuildRequires:  systemd-devel
BuildRequires:  gtk3-devel
BuildRequires:  libappindicator-gtk3-devel
BuildRequires:  libnotify-devel

# For the app subpackage
BuildRequires:  nodejs
BuildRequires:  npm

Requires:       %{name}-server = %{version}-%{release}
Requires:       %{name}-app = %{version}-%{release}

%description
Lemonade is a lightweight, high-performance local LLM server with support for
multiple backends including llama.cpp, FastFlowLM, and RyzenAI.

This package is a meta-package that installs both the Lemonade server and the
desktop application.

%package server
Summary:        Server components for Lemonade
# Required to create the lemonade system user in %pre
Requires(pre):  shadow-utils
%{?systemd_requires}

%description server
The Lemonade server subpackage contains the core LLM server, the system tray
management application, and the web interface.

%package app
Summary:        Desktop application for Lemonade
Requires:       %{name}-server%{?_isa} = %{version}-%{release}
# Fedora usually bundles Electron or uses a system-wide one;
# this spec assumes an Electron-based build.
Requires:       electron

%description app
A modern desktop interface for managing and interacting with the
Lemonade LLM server.

%prep
%autosetup -N -n %{name}-%{version}
cd lemonade
%patch -P 0 -p1
%patch -P 1 -p1
%patch -P 2 -p1
# Fix httplib detection and linking on Fedora (where it is header-only and has no .pc file)
sed -i 's/set(USE_SYSTEM_HTTPLIB ${HTTPLIB_FOUND})/set(USE_SYSTEM_HTTPLIB ${HTTPLIB_INCLUDE_DIRS})/' CMakeLists.txt
sed -i 's/PRIVATE cpp-httplib/PRIVATE httplib::httplib/g' CMakeLists.txt src/cpp/tray/CMakeLists.txt
# Ensure httplib::httplib target is defined via find_package
sed -i '/include(GNUInstallDirs)/a find_package(httplib REQUIRED)' CMakeLists.txt
# System service runs headless; tray is for user sessions only
sed -i 's|lemonade-server serve$|lemonade-server serve --no-tray|' data/lemonade-server.service.in

%build
cd lemonade
# Build the server components
%cmake -G Ninja \
    -DBUILD_WEB_APP=OFF \
    -DBUILD_ELECTRON_APP=OFF \
    -DUSE_SYSTEM_JSON=ON \
    -DUSE_SYSTEM_CLI11=ON \
    -DUSE_SYSTEM_HTTPLIB=ON \
    -DENABLE_LINUX_TRAY=ON
%cmake_build

# Build the Electron app
cd src/app
# Note: Fedora builds are offline. In a production Koji/Mock build,
# you would provide a pre-bundled node_modules tarball.
npm install --offline || npm install
npm run build:linux

%install
cd lemonade
%cmake_install

# --- Icons ---
# Install the application icon into the hicolor theme.
# Named "lemonade" so it is referenced consistently by the desktop entries
# and resolved automatically by the system tray (AppIndicator3/SNI).
install -Dpm 0644 src/app/assets/logo.svg \
    %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/lemonade.svg

# --- Web app launcher ---
# Shell script that opens the built-in web interface in the user's browser.
install -Dpm 0755 data/launch-lemonade-web-app.sh \
    %{buildroot}%{_bindir}/lemonade-web

# --- Desktop entries ---
# lemonade.desktop: Electron desktop app (app subpackage)
desktop-file-install \
    --dir=%{buildroot}%{_datadir}/applications \
    --set-icon=lemonade \
    data/lemonade-app.desktop
mv %{buildroot}%{_datadir}/applications/lemonade-app.desktop \
   %{buildroot}%{_datadir}/applications/lemonade.desktop

# lemonade-web.desktop: web interface launcher (base package)
desktop-file-install \
    --dir=%{buildroot}%{_datadir}/applications \
    --set-key=Exec --set-value=lemonade-web \
    --set-icon=lemonade \
    data/lemonade-web-app.desktop
mv %{buildroot}%{_datadir}/applications/lemonade-web-app.desktop \
   %{buildroot}%{_datadir}/applications/lemonade-web.desktop

# --- AppStream metadata ---
install -Dpm 0644 /dev/stdin \
    %{buildroot}%{_datadir}/metainfo/lemonade.appdata.xml << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<component type="desktop-application">
  <id>lemonade</id>
  <metadata_license>FSFAP</metadata_license>
  <project_license>Apache-2.0</project_license>
  <name>Lemonade</name>
  <summary>Lightweight, high-performance local LLM server</summary>
  <description>
    <p>
      Lemonade is a lightweight, high-performance local LLM server with support for
      multiple backends including llama.cpp, FastFlowLM, and RyzenAI.
    </p>
  </description>
  <launchable type="desktop-id">lemonade.desktop</launchable>
  <launchable type="desktop-id">lemonade-web.desktop</launchable>
  <url type="homepage">https://lemonade-server.ai/</url>
  <provides>
    <binary>lemonade-server</binary>
    <binary>lemonade-web</binary>
    <binary>lemonade-app</binary>
  </provides>
</component>
EOF

# --- Electron app ---
# electron-builder names the binary after productName (lowercased) = "lemonade"
mkdir -p %{buildroot}%{_libdir}/lemonade-app
cp -r src/app/dist-app/linux-unpacked/* %{buildroot}%{_libdir}/lemonade-app/

# Wrapper script so lemonade-app is findable in PATH (required by lemonade.desktop Exec=lemonade-app)
install -Dpm 0755 /dev/stdin \
    %{buildroot}%{_bindir}/lemonade-app << 'EOF'
#!/bin/sh
exec %{_libdir}/lemonade-app/lemonade "$@"
EOF

# --- User systemd unit (tray) ---
# Runs lemonade-server in tray mode for graphical user sessions.
# Users can enable it with: systemctl --user enable --now lemonade-tray.service
install -Dpm 0644 /dev/stdin \
    %{buildroot}%{_userunitdir}/lemonade-tray.service << 'EOF'
[Unit]
Description=Lemonade Server (System Tray)
Documentation=https://lemonade-server.ai/
After=graphical-session.target
PartOf=graphical-session.target

[Service]
Type=simple
ExecStart=%{_bindir}/lemonade-server tray
Restart=on-failure
RestartSec=5s
KillSignal=SIGINT

[Install]
WantedBy=graphical-session.target
EOF

# --- System user home directory ---
# /var/lib/lemonade is WorkingDirectory and ReadWritePaths for the service unit.
install -dm 0750 %{buildroot}%{_sharedstatedir}/lemonade

%pre server
# Create the lemonade system group and user if they do not already exist.
getent group lemonade >/dev/null || groupadd -r lemonade
getent passwd lemonade >/dev/null || \
    useradd -r -g lemonade -d %{_sharedstatedir}/lemonade \
            -s /sbin/nologin -c "Lemonade Server" lemonade

%post server
%systemd_post lemonade-server.service
# Set ownership of the working directory now that the lemonade user exists.
chown lemonade:lemonade %{_sharedstatedir}/lemonade
chmod 0750 %{_sharedstatedir}/lemonade

%preun server
%systemd_preun lemonade-server.service

%postun server
%systemd_postun_with_restart lemonade-server.service

%check
cd lemonade
appstream-util validate-relax --nonet %{buildroot}%{_datadir}/metainfo/lemonade.appdata.xml
desktop-file-validate %{buildroot}%{_datadir}/applications/lemonade.desktop
desktop-file-validate %{buildroot}%{_datadir}/applications/lemonade-web.desktop

%files

%files server
%license lemonade/LICENSE
%doc lemonade/README.md
%{_bindir}/lemonade-router
%{_bindir}/lemonade-server
%{_bindir}/lemonade-web
%{_datadir}/lemonade-server/
%{_datadir}/icons/hicolor/scalable/apps/lemonade.svg
%{_datadir}/applications/lemonade-web.desktop
%dir %{_sysconfdir}/lemonade
%config(noreplace) %{_sysconfdir}/lemonade/lemonade.conf
%config(noreplace) %{_sysconfdir}/lemonade/secrets.conf
%{_unitdir}/lemonade-server.service
%{_userunitdir}/lemonade-tray.service
%dir %{_sharedstatedir}/lemonade

%files app
%{_bindir}/lemonade-app
%{_libdir}/lemonade-app/
%{_datadir}/applications/lemonade.desktop
%{_datadir}/metainfo/lemonade.appdata.xml

%changelog
* Fri Feb 27 2026 Arun Babu Neelicattu <arun.neelicattu@gmail.com> 9.3.4-5
- spec: fix autosetup after rename (arun.neelicattu@gmail.com)

* Fri Feb 27 2026 Arun Babu Neelicattu <arun.neelicattu@gmail.com> 9.3.4-4
- spec: fix incorrect source after rename (arun.neelicattu@gmail.com)

* Fri Feb 27 2026 Arun Babu Neelicattu <arun.neelicattu@gmail.com> 9.3.4-3
- tito: update tagger (arun.neelicattu@gmail.com)

* Fri Feb 27 2026 Arun Babu Neelicattu <arun.neelicattu@gmail.com> 9.3.4-2
- new package built with tito

* Thu Feb 26 2026 Arun Neelicattu <arun.neelicattu@gmail.com> - 9.3.4-1
Initial package source
