{
  description = "sse-websockets";

  inputs = {
    nixpkgs.url = github:NixOS/nixpkgs/nixos-21.11;
  };

  outputs = { self, nixpkgs }:
  let
    system = "x86_64-linux";
    pkgs = import nixpkgs { inherit system; };
  in rec {
    packages.${system} = rec {

      python = pkgs.python39;

      pythonEnv = python.withPackages (ps: [
        ps.uvicorn
        ps.starlette
      ]);
    };

    devShell.${system} = with pkgs; with packages.${system}; pkgs.mkShell {
      buildInputs = [
        nssTools
        caddy
        pythonEnv
        websocat
      ];
      
    };
  };
}
