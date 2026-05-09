#!/usr/bin/env bash
set -euo pipefail

echo "[JANR] Running dry-run (check mode)..."

cd ansible

ansible-playbook \
  playbooks/janr.yml \
  -vv \
  --check \
  --diff