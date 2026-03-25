#!/bin/sh
# install.sh — Raspi-Sump installer
#
# Usage:
#   curl -fsSL https://www.linuxnorth.org/raspisumpv2/install.sh | sudo sh
#
# What this script does:
#   1. Checks for an existing unstable (pre-release) repository entry and
#      removes it if found, so the system targets the stable channel.
#   2. Imports the Linuxnorth Archive GPG signing key.
#   3. Adds the stable (trixie) APT repository.
#   4. Installs raspisump via apt.

set -e

APT_KEY_URL="https://apt.linuxnorth.org/public_key.asc"
APT_KEY_PATH="/usr/share/keyrings/linuxnorth-archive-keyring.gpg"
SOURCES_FILE="/etc/apt/sources.list.d/linuxnorth.list"
APT_BASE="https://apt.linuxnorth.org"
STABLE_DIST="trixie"
STABLE_ENTRY="deb [signed-by=${APT_KEY_PATH}] ${APT_BASE} ${STABLE_DIST} main"

# ── helpers ──────────────────────────────────────────────────────────────────

info()  { printf '\033[1;32m[raspi-sump]\033[0m %s\n' "$*"; }
warn()  { printf '\033[1;33m[raspi-sump]\033[0m %s\n' "$*"; }
error() { printf '\033[1;31m[raspi-sump]\033[0m %s\n' "$*" >&2; }
die()   { error "$*"; exit 1; }

# ── pre-flight ────────────────────────────────────────────────────────────────

if [ "$(id -u)" -ne 0 ]; then
    die "This script must be run as root. Try: curl -fsSL <url> | sudo sh"
fi

# Require Debian/Raspberry Pi OS
if [ ! -f /etc/debian_version ]; then
    die "This installer requires Debian or Raspberry Pi OS."
fi

# Require curl or wget
if command -v curl >/dev/null 2>&1; then
    FETCH="curl -fsSL"
elif command -v wget >/dev/null 2>&1; then
    FETCH="wget -qO-"
else
    die "curl or wget is required but neither was found. Install it with: sudo apt install curl"
fi

# Require gpg
if ! command -v gpg >/dev/null 2>&1; then
    die "gpg is required but not found. Install it with: sudo apt install gnupg"
fi

# ── remove unstable (pre-release) channel if present ─────────────────────────

if [ -f "$SOURCES_FILE" ]; then
    if grep -q "unstable" "$SOURCES_FILE" 2>/dev/null; then
        warn "Pre-release (unstable) repository entry found — replacing with stable channel."
        rm -f "$SOURCES_FILE"
    elif grep -q "${APT_BASE}" "$SOURCES_FILE" 2>/dev/null; then
        if grep -q "${STABLE_DIST}" "$SOURCES_FILE" 2>/dev/null; then
            info "Stable repository is already configured."
        else
            warn "Existing linuxnorth sources entry found but does not target ${STABLE_DIST}. Replacing."
            rm -f "$SOURCES_FILE"
        fi
    fi
fi

# ── import signing key ────────────────────────────────────────────────────────

info "Importing Linuxnorth Archive signing key..."
$FETCH "$APT_KEY_URL" | gpg --dearmor -o "$APT_KEY_PATH"
chmod 644 "$APT_KEY_PATH"

# ── add stable repository ─────────────────────────────────────────────────────

if [ ! -f "$SOURCES_FILE" ]; then
    info "Adding stable APT repository (${STABLE_DIST})..."
    printf '%s\n' "$STABLE_ENTRY" > "$SOURCES_FILE"
    chmod 644 "$SOURCES_FILE"
fi

# ── install ───────────────────────────────────────────────────────────────────

info "Updating package index..."
apt-get update -qq

info "Installing raspisump..."
apt-get install -y raspisump

info "Installation complete. Follow the on-screen instructions above to finish setup."
info "Advanced users: sensor settings can be configured manually in /etc/raspi-sump/raspisump.conf"
