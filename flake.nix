{
  description = "JANR provisioning - clean-room dev environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = { self, nixpkgs }:
  let
    system = "x86_64-linux";
    pkgs = import nixpkgs {
      inherit system;

      # 🔴 HARDEN: disable impure overlays / global config leakage
      config = {
        allowUnfree = false;
      };
    };

    janrTools = import ./nix/tooling.nix { inherit pkgs; };

  in {
    devShells.${system}.default = pkgs.mkShellNoCC {

      # 🔴 STRICT TOOLING: only Nix-provided binaries
      packages = janrTools;

      # 🔴 CLEAN ROOM ENVIRONMENT SETUP
      shellHook = ''
        export PATH="${pkgs.lib.makeBinPath janrTools}"

        # Remove common impurity vectors
        unset LD_LIBRARY_PATH
        unset PYTHONPATH
        unset ANSIBLE_CONFIG

        # Force predictable locale + behavior
        export LANG=C.UTF-8
        export LC_ALL=C.UTF-8
        export PYTHONUTF8=1
        export PYTHONIOENCODING=utf-8

        # 🔵 JANR DEV SHELL PROMPT
        export PS1="\n[JANR DEV SHELL]\n\w\$ "

        echo "================================================="
        echo " JANR CLEAN ROOM DEV SHELL ACTIVE"
        echo "================================================="
        echo ""

        echo "PROJECT EXECUTION MODEL:"
        echo "  All Ansible operations MUST be executed via repository scripts."
        echo "  These scripts are portable and do not require Nix to be present."
        echo ""

        echo "NOTE:"
        echo "  All scripts assume the repository root as the working directory."
        echo "  If needed, inspect the scripts directly to view underlying commands."
        echo ""

        echo "PRIMARY COMMANDS (RECOMMENDED):"
        echo ""
        echo "  Deploy configuration to router:"
        echo "    ./deploy"
        echo ""
        echo "  Safe dry-run (no changes applied):"
        echo "    ./dry-run"
        echo ""
        echo "  Syntax validation only:"
        echo "    ./check-syntax"
        echo ""

        echo "================================================="
        echo ""
      '';
    };
  };
}