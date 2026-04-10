{
  description = "pyet-mc development environment with Python, Rust, and uv";
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    rust-overlay.url = "github:oxalica/rust-overlay";
  };
  outputs =
    {
      self,
      nixpkgs,
      flake-utils,
      rust-overlay,
    }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        overlays = [ rust-overlay.overlays.default ];
        pkgs = import nixpkgs {
          inherit system;
          overlays = overlays;
        };

        isLinux = pkgs.lib.hasInfix "linux" system;

        rust-toolchain = pkgs.rust-bin.stable.latest.default.override {
          extensions = [
            "rust-src"
            "rust-analyzer"
          ];
        };

      in
      {
        devShells = {
          default = pkgs.mkShell {
            packages = [
              rust-toolchain
              pkgs.python313
              pkgs.uv
              pkgs.maturin
              pkgs.stdenv.cc.cc.lib
              pkgs.zlib
              pkgs.ty
            ]
            ++ pkgs.lib.optionals isLinux [
              pkgs.chromium
            ];

            shellHook = ''
              export LD_LIBRARY_PATH=${pkgs.zlib}/lib:${pkgs.stdenv.cc.cc.lib}/lib''${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}
              ${pkgs.lib.optionalString isLinux ''
                export PATH=${pkgs.chromium}/bin:$PATH
              ''}

              echo "Python version: $(python --version)"
              echo "uv version: $(uv --version)"
              echo "Rust version: $(rustc --version)"
              echo "maturin version: $(maturin --version)"
            '';
          };

          cross = pkgs.mkShell {
            packages =
              let
                rust-cross = pkgs.rust-bin.stable.latest.default.override {
                  extensions = [
                    "rust-src"
                    "rust-analyzer"
                  ];
                  targets = [
                    "x86_64-unknown-linux-gnu"
                    "aarch64-unknown-linux-gnu"
                    "x86_64-pc-windows-gnu"
                  ];
                };
              in
              [
                rust-cross
                pkgs.python313
                pkgs.uv
                pkgs.maturin
                pkgs.zig
                pkgs.cargo-zigbuild
                pkgs.pkgsCross.mingwW64.stdenv.cc
                pkgs.pkgsCross.mingwW64.windows.mingw_w64
              ];

            shellHook = ''
              echo "Cross-compilation shell ready"
              echo "  cargo zigbuild --release --target aarch64-unknown-linux-gnu"
              echo "  cargo zigbuild --release --target x86_64-pc-windows-gnu"
              echo "  maturin build --release --target aarch64-unknown-linux-gnu --zig"
            '';
          };
        };
      }
    );
}
