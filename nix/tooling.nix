{ pkgs }:

with pkgs; [
  # CORE UNIX TOOLING (THIS WAS MISSING)
  coreutils
  findutils
  gnugrep
  gnused
  gawk

  # shell support
  bashInteractive

  # Ansible tooling
  ansible
  ansible-lint
  sshpass
  openssh

  # Python runtime
  python3
  python3Packages.netaddr

  # Networking tools
  iproute2
  nftables
  bind

  # utilities
  jq
  yq
  git
  inetutils

  # system introspection
  systemd

  # python 
  python3
  python3.pkgs.pip
  python3.pkgs.virtualenv

]
