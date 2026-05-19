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

        export VENV_DIR=.venv
 
        if [ ! -d "$VENV_DIR" ]; then
          echo "Creating virtualenv..."
          python -m venv $VENV_DIR
        fi
 
        source $VENV_DIR/bin/activate

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

        echo "PRIMARY COMMANDS (RECOMMENDED):"
        echo ""
        echo "  Full deployment:"
        echo "    ./janr deploy <target>"
        echo ""
        echo "  Safe dry-run (no changes applied):"
        echo "    ./janr dry-run <target>"
        echo ""
        echo "  Syntax validation only:"
        echo "    ./janr check-syntax <target>"
        echo ""
        echo "  Targets:"
        echo "    router   -> router.yml"
        echo "    ui       -> ui.yml"
        echo "    all      -> site.yml"
        echo ""
        echo "  Examples:"
        echo "    ./janr deploy router"
        echo "    ./janr dry-run all"
        echo "    ./janr check-syntax ui"
        echo ""
        echo "================================================="
        echo ""
      '';
    };
  };
}
