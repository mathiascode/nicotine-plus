let pkgs = import ./nix { };
in with pkgs;
mkShell {
  buildInputs = with pkgs; [
    gtk3-x11
    python3
    python3Packages.certifi
    python3Packages.flake8
    python3Packages.pep8-naming
    python3Packages.pygobject3
    python3Packages.pytest
  ];
}
