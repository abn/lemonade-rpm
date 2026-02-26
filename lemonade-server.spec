Name:           lemonade-server
Version:        9.3.4
Release:        1
Summary:        Lightweight, high-performance local LLM server
License:        Apache-2.0
URL:            https://lemonade-server.ai/
Source0:        %{name}-%{version}.tar.gz

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

# For the app subpackage
BuildRequires:  nodejs
BuildRequires:  npm

%description
Lemonade is a lightweight, high-performance local LLM server with support for
multiple backends including llama.cpp, FastFlowLM, and RyzenAI.

%package app
Summary:        Desktop application for Lemonade
Requires:       %{name}%{?_isa} = %{version}-%{release}
# Fedora usually bundles Electron or uses a system-wide one;
# this spec assumes an Electron-based build.
Requires:       electron

%description app
A modern desktop interface for managing and interacting with the 
Lemonade LLM server.

%prep
%autosetup -n %{name}-%{version}
cd lemonade
# Fix httplib detection and linking on Fedora (where it is header-only and has no .pc file)
sed -i 's/set(USE_SYSTEM_HTTPLIB ${HTTPLIB_FOUND})/set(USE_SYSTEM_HTTPLIB ${HTTPLIB_INCLUDE_DIRS})/' CMakeLists.txt
sed -i 's/PRIVATE cpp-httplib/PRIVATE httplib::httplib/g' CMakeLists.txt src/cpp/tray/CMakeLists.txt
# Ensure httplib::httplib target is defined via find_package
sed -i '/include(GNUInstallDirs)/a find_package(httplib REQUIRED)' CMakeLists.txt

%build
cd lemonade
# Build the server components
%cmake -G Ninja \
    -DBUILD_WEB_APP=OFF \
    -DBUILD_ELECTRON_APP=OFF \
    -DUSE_SYSTEM_JSON=ON \
    -DUSE_SYSTEM_CLI11=ON \
    -DUSE_SYSTEM_HTTPLIB=ON
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

# Install the app wrapper and files
mkdir -p %{buildroot}%{_libdir}/lemonade-app
cp -r src/app/dist-app/linux-unpacked/* %{buildroot}%{_libdir}/lemonade-app/

# Install Desktop integration
mkdir -p %{buildroot}%{_datadir}/applications
desktop-file-install --dir=%{buildroot}%{_datadir}/applications data/lemonade-app.desktop

mkdir -p %{buildroot}%{_datadir}/metainfo
cat > %{buildroot}%{_datadir}/metainfo/ai.lemonade_server.Lemonade.appdata.xml <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<component type="desktop-application">
  <id>ai.lemonade_server.Lemonade</id>
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
  <launchable type="desktop-id">lemonade-app.desktop</launchable>
  <url type="homepage">https://lemonade-server.ai/</url>
  <provides>
    <binary>lemonade-server</binary>
  </provides>
</component>
EOF

mkdir -p %{buildroot}%{_datadir}/icons/hicolor/scalable/apps
install -pm 0644 src/app/assets/logo.svg %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/ai.lemonade_server.Lemonade.svg

%check
cd lemonade
appstream-util validate-relax --nonet %{buildroot}%{_datadir}/metainfo/*.appdata.xml
desktop-file-validate %{buildroot}%{_datadir}/applications/*.desktop

%files
%license lemonade/LICENSE
%doc lemonade/README.md
%{_bindir}/lemonade-router
%{_bindir}/lemonade-server
%{_datadir}/lemonade-server/
%dir %{_sysconfdir}/lemonade
%config(noreplace) %{_sysconfdir}/lemonade/lemonade.conf
%config(noreplace) %{_sysconfdir}/lemonade/secrets.conf
%{_unitdir}/lemonade-server.service

%files app
%{_libdir}/lemonade-app/
%{_datadir}/applications/*.desktop
%{_datadir}/metainfo/*.appdata.xml
%{_datadir}/icons/hicolor/scalable/apps/*.svg

%changelog
* Wed Feb 25 2026 Gemini CLI <arun.neelicattu@gmail.com> - 9.3.4-1
- Initial package for Fedora
