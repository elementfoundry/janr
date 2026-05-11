#!/usr/bin/env bash

set -euo pipefail

NEW_HOSTNAME="janr"

show_help() {
    cat <<EOF
Bootstrap script for JANR (Just Another Network Router)
Run on the target machine to set up initial environment

Usage:
    $(basename "$0") [OPTIONS]

Options:
    -h, --help      Show this help message and exit
EOF
}

case "${1:-}" in
    -h|--help)
        show_help
        exit 0
        ;;
esac

echo "========================================="
echo "JANR Bootstrap"
echo "========================================="

# Capture current hostname BEFORE changing it
OLD_HOSTNAME="$(hostname)"

echo
echo "[0/8] Current hostname detected: ${OLD_HOSTNAME}"
echo "[1/8] Updating package lists..."
sudo apt update

echo
echo "[2/8] Upgrading system..."
sudo apt upgrade -y

echo
echo "[3/8] Installing packages..."
sudo apt install -y python3-apt vim avahi-daemon

echo
echo "[4/8] Setting hostname to ${NEW_HOSTNAME}..."
sudo hostnamectl set-hostname "${NEW_HOSTNAME}"

echo
echo "[5/8] Updating /etc/hosts (replacing ${OLD_HOSTNAME} → ${NEW_HOSTNAME})..."

# Replace any occurrence of old hostname in /etc/hosts
if grep -q "${OLD_HOSTNAME}" /etc/hosts; then
    sudo sed -i "s/${OLD_HOSTNAME}/${NEW_HOSTNAME}/g" /etc/hosts
fi

# Ensure localhost lines exist and are sane
if ! grep -q "^127.0.0.1" /etc/hosts; then
    echo "127.0.0.1 localhost" | sudo tee -a /etc/hosts >/dev/null
fi

if ! grep -q "^127.0.1.1" /etc/hosts; then
    echo -e "127.0.1.1\t${NEW_HOSTNAME}" | sudo tee -a /etc/hosts >/dev/null
fi

echo
echo "[6/8] Enabling Avahi..."
sudo systemctl enable --now avahi-daemon

echo
echo "[7/8] Fixing Ping..."
sudo setcap cap_net_raw+ep /usr/bin/ping

echo
echo "[8/8] Done."

echo
echo "========================================="
echo "Bootstrap complete"
echo "Old hostname: ${OLD_HOSTNAME}"
echo "New hostname: ${NEW_HOSTNAME}"
echo "mDNS: ${NEW_HOSTNAME}.local"
echo "========================================="
echo
echo "Reboot recommended."