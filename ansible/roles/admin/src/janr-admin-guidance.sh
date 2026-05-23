#!/usr/bin/env sh

# Only show hint for janr-admin users in interactive shells
if [ -n "$PS1" ] && id -nG "$USER" | grep -qw janr-admin; then
    if command -v janr-dashboard >/dev/null 2>&1; then
        echo ""
        printf "\033[1;33m[janr] Admin tools available: run 'janr-dashboard'\033[0m\n"
        echo ""
    fi
fi