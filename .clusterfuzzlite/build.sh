#!/bin/bash -eu
# Install the package and its dependencies.
python3 -m pip install .

# Build the fuzzer.
compile_python_fuzzer tests/fuzz/test_schemas_fuzz.py
