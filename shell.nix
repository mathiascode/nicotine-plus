  sources = import ./nix/sources.nix;
in
{ pkgs ? import sources.nixpkgs {} }:

  with pkgs;
  stdenv.mkDerivation {
    name = "macOS";

    buildInputs = [
      git
    ];
  }
