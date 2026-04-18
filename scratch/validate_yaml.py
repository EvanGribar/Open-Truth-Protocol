import sys

try:
    import yaml  # type: ignore[import-untyped]

    with open(".github/labeler.yml") as f:
        yaml.safe_load(f)
    print("YAML is valid")
except ImportError:
    print("PyYAML not installed")
except Exception as e:
    print(f"YAML error: {e}")
    sys.exit(1)
