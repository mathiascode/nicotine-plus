{ unstable ? import <unstable> {} }:

unstable.stdenv.mkDerivation rec {
	name = "test";
	version = "1.0.0";

	buildInputs = with unstable; [
		gnome3.gspell
		gnome3.glib
		gnome3.gtk
	];

	nativeBuildInputs = with unstable; [
		pkgconfig
		go
		wrapGAppsHook
	];
}
