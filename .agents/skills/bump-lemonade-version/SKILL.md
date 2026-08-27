---
name: bump-lemonade-version
description: "Methodical workflow to upgrade the Lemonade RPM packages for a new upstream version using Tito, podman, and rpmbuilder."
---

# Upgrading Lemonade RPM Version

Use this skill when you need to bump the packaged version of upstream Lemonade in the `lemonade-rpm` repository.

Always refer to [AGENTS.md](file:///home/abn/workspace/lemonade-sdk/lemonade-rpm/AGENTS.md) for repository architecture, rules, and invariants.

---

## 1. Upstream Analysis and Prep

### Step 1.1: Fetch and Checkout upstream release
Check out the target release tag in the `lemonade` submodule:
```bash
git -C lemonade fetch --tags
git -C lemonade checkout vX.Y.Z
```

### Step 1.2: Identify Breaking and Dependency Changes
Compare the changes between the previous version and the new version to evaluate packaging impact:
```bash
git -C lemonade diff --name-only vPREV..vNEW
```

1. **Check CMake / Link Changes:** Inspect the root `CMakeLists.txt` and `src/cpp/CMakeLists.txt` for any new build-time options, library additions, or link dependencies (e.g. `drm_amdgpu` added in v11.0.0).
2. **Check Assets / CLI / Files:** Verify if any new commands, desktop entries, or static resource directories are added or deleted in `data/` or upstream `install` rules.
3. **Verify FHS & Path Compliance:** Ensure upstream changes haven't regressed FHS separation for system services (`/var/lib/lemonade` for state, `/var/cache/lemonade` and `/var/cache/huggingface` for cache/models). If upstream drops standard paths in favor of `$HOME/.cache` workarounds, enforce FHS via `/etc/default/lemond` or systemd service configurations.
4. **Verify Existing Patches:** Run `git apply --check` for every patch in the `patches/` directory to make sure they still apply cleanly. For example:
   ```bash
   git -C lemonade apply --check ../patches/0001-fix-app-store-settings-under-user-config-dir.patch
   ```

---

## 2. Update Spec Version

1. Open [lemonade.spec](file:///home/abn/workspace/lemonade-sdk/lemonade-rpm/lemonade.spec).
2. Modify the `Version:` field at the top of the file:
   ```spec
   Version:        X.Y.Z
   ```
3. **CRITICAL RULE**: Do **NOT** manually edit or append entries to the `%changelog` section. Tito automatically generates changelog entries on tagging. Manual edits will cause duplicate entry errors.

---

## 3. Verify changes with a Test Build

Tito's containerized build only builds from git commits. You must commit your changes before executing a build.

### Step 3.1: Commit changes to Git
```bash
git add lemonade lemonade.spec
git commit -m "Bump version to X.Y.Z and update submodule"
```

### Step 3.2: Run the rpmbuilder Container
Start the `rpmbuilder` container in the background (using the version of Fedora matching your host's target release, e.g. `fedora-44` for `.fc44`):
```bash
podman run -d --rm -i --name rpmbuilder-lemonade -v ${PWD}:/sources:z quay.io/abn/rpmbuilder:fedora-44 sleep inf
```

### Step 3.3: Trigger the Build
```bash
podman exec rpmbuilder-lemonade rpmbuilder
```

### Step 3.4: Verify the Build Output
Inspect the logs and build outputs in the `/output` folder (or container log) to confirm:
- AppStream metadata is valid (no validation warnings).
- No "Installed (but unpackaged)" file errors.
- Every expected subpackage (`lemonade-cli`, `lemonade-server`, `lemonade-tray`, `lemonade-desktop`, `lemonade-web`) is successfully written as an `.rpm` file.

### Step 3.5: Clean up the Container
```bash
podman stop rpmbuilder-lemonade
```

---

## 4. Release and Tagging

### Step 4.1: Tag the Package
Run the tito tag command to auto-generate the spec changelog, update `.tito/packages/lemonade`, and create the git release tag:
```bash
tito tag --use-release '1%{?dist}' --accept-auto-changelog
```
*Note: Always quote and keep the `%{?dist}` suffix so COPR builds retain the correct OS release identifier.*

### Step 4.2: Push to Origin
```bash
git push --follow-tags origin main
```
*Note: Pushing the tag to the remote repository triggers the COPR builder automatically via GitHub webhooks.*

---

## 5. Troubleshooting & Error Handling

### Error: Patch does not apply cleanly
If a patch check fails (`git apply --check` returns errors):
1. Apply it with `--reject`:
   ```bash
   git -C lemonade apply --reject ../patches/YOUR_PATCH.patch
   ```
2. Inspect the generated `.rej` files to see what failed to merge.
3. Edit the target source files to resolve conflicts, and recreate the patch:
   ```bash
   git -C lemonade diff > patches/YOUR_PATCH.patch
   ```

### Error: Link or compilation error inside container (missing libraries)
If the build fails inside `rpmbuilder` because of a missing header or library (e.g. `fatal error: header.h: No such file or directory` or `cannot find -llibname`):
1. Do **NOT** manually install the package inside the container using `dnf`. This violates the reproducibility of packaging.
2. Determine which Fedora package provides the missing file using your package manager or web search.
3. Add the package to the `BuildRequires:` (or `Requires:`) section of [lemonade.spec](file:///home/abn/workspace/lemonade-sdk/lemonade-rpm/lemonade.spec).
4. Commit the spec file modification to Git and rerun the container build.

### Error: Tito "dirty repository" state during tagging
If `tito tag` aborts because of uncommitted or untracked files:
1. Check untracked files with `git status`.
2. Add any temporary files (e.g. `.mbx`, `.cover`, or debug files) to the project `.gitignore`.
3. Do not run `tito tag` with dirty working trees.

### Error: Forgotten commit before running build
If you modified the spec file or submodule tag but the build compiles the old code, you likely forgot to commit. Since Tito uses the git tree to bundle source archives, you **must commit** before running the build. If you have many speculative commits during debugging, squash them into a single clean commit using `git rebase -i` before running the final tagging command.
