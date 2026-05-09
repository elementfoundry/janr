#!/usr/bin/env bash
set -euo pipefail

echo "[JANR] Syntax checking playbook..."

cd ansible

ansible-playbook \
  playbooks/janr.yml \
  --syntax-check