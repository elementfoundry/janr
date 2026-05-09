#!/usr/bin/env bash
set -euo pipefail

echo "[JANR] Deploying router stack..."

cd ansible

ansible-playbook \
  playbooks/janr.yml \
  -vv