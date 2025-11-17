with import <nixpkgs> { };

(python3.withPackages (
  ps: with ps; [
    requests
    bech32
    pyside6
    urllib3
  ]
)).env
