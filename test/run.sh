#!/bin/bash

echocol() { echo -e "\033[32m*** $@...\033[0m " >&2; }

 if [ ! -d bats ]; then
     echocol "Installing bats..."
     git clone --depth 1 https://github.com/mapio/bats.git
fi

if [ ! -r ../release/sf ]; then
    echocol "Compiling sf..."
    ./bin/mkdist
fi
export PATH="$PATH:$(pwd)/../release/"

echocol "Running tests..."
./bats/bin/bats .
