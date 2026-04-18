import json
import sys
from typing import Any

import atheris  # type: ignore[import-untyped]

with atheris.instrument_imports():
    from pydantic import ValidationError

    from shared.schemas import ResultEnvelope


def TestOneInput(data: bytes) -> None:
    fdp = atheris.FuzzedDataProvider(data)
    try:
        # Try to parse fuzzed string as JSON and validate
        json_str = fdp.ConsumeUnicodeNoSurrogates(sys.maxsize)
        payload: dict[str, Any] = json.loads(json_str)
        ResultEnvelope.model_validate(payload)
    except (ValidationError, json.JSONDecodeError, UnicodeDecodeError):
        # Expected errors
        return
    except Exception as e:
        # Unexpected errors are what we're looking for
        print(f"Unexpected exception: {e}")
        raise e


def main() -> None:
    atheris.Setup(sys.argv, TestOneInput)
    atheris.Fuzz()


if __name__ == "__main__":
    main()
