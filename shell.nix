with import <nixpkgs> { };

(python3.withPackages (
  ps: with ps; [
    requests
    # standard libs
    #json
    #logging
  ]
)).env
