#!/usr/bin/bash

# cwd=$(pwd)
# cd "$SRC/re2" && git checkout 4a8cee3dd3c3d81b6fe8b867811e193d5819df07 && cd "$cwd"

export CXXFLAGS=$(cat "$SRC/CXXFLAGS")
# RE2 commit 4a8cee3 does not build with Bazel 9 because C++ rules are no longer built-ins.
# Keep a Bazel 7 toolchain for compatibility in the generated benchmark image.
export USE_BAZEL_VERSION=7.4.1
bash "$SRC"/build.sh
