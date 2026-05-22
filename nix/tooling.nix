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

  # python virtual env
  python3.pkgs.pip
  python3.pkgs.virtualenv

  # rust tool replacements
  moor
  exa
  bat
]
