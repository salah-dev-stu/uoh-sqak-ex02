"""CODE_VERSION starts at 1.00 (R6 versioning) + config version compat check."""
import pytest

from agent_debate.shared.version import CODE_VERSION, validate_config_version


def test_code_version_starts_at_1_00():
    assert CODE_VERSION == "1.00"


def test_validate_config_version_accepts_matching():
    validate_config_version("1.00", source="setup.json")  # should not raise


def test_validate_config_version_rejects_mismatch():
    with pytest.raises(ValueError, match="version mismatch"):
        validate_config_version("2.00", source="setup.json")
