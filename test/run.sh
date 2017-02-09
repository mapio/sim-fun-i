#!/bin/bash

echocol() { echo -e "\033[32m*** $@...\033[0m " >&2; }

 if [ ! -d ./test/bats ]; then
     echocol "Installing bats..."
     (cd test && git clone --depth 1 https://github.com/mapio/bats.git)
fi

if [ ! -r ./release/sf ]; then
    echocol "Compiling sf..."
    ./bin/mkdist
fi

export PATH="$PATH:$(pwd)/release/"
export FIXTURES="$(pwd)/test/fixtures"

echocol "Running tests..."
./test/bats/bin/bats test
