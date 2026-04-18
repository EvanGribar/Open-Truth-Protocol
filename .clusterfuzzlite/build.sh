#!/bin/bash -eu
# Install uv for faster dependency resolution
python3 -m pip install uv

# Install the package and its dependencies using uv
python3 -m uv pip install --system .



# Build the fuzzer.
compile_python_fuzzer tests/fuzz/test_schemas_fuzz.py
