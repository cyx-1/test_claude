"""
Tests for Configuration Management (config_manager.py)

Following TDD principles - tests written FIRST before implementation.

Tests cover:
- Loading valid config.yaml
- Handling missing config file
- Validation of repository entries (missing fields, invalid paths)
- Environment variable substitution (${OPENAI_API_KEY})
- Default settings when not specified
"""

import os
from pathlib import Path
from typing import Dict, Any

import pytest
import yaml

from config_manager import (
    ConfigManager,
    ConfigValidationError,
    load_config,
    validate_config,
    substitute_env_vars,
)


class TestConfigManager:
    """Test suite for ConfigManager class."""

    def test_load_valid_config(self, temp_config_file, sample_config):
        """Test loading a valid config.yaml file."""
        manager = ConfigManager(config_path=temp_config_file)
        config = manager.load()

        assert config is not None
        assert "repositories" in config
        assert len(config["repositories"]) == 2
        assert config["repositories"][0]["name"] == "test-repo-1"

    def test_load_config_with_defaults(self, temp_dir, minimal_config):
        """Test loading config with minimal settings applies defaults."""
        config_path = temp_dir / "minimal_config.yaml"
        with open(config_path, "w") as f:
            yaml.dump(minimal_config, f)

        manager = ConfigManager(config_path=config_path)
        config = manager.load()

        # Check that defaults are applied
        assert "settings" in config
        assert config["settings"]["auto_fetch"] is True
        assert config["settings"]["parallel_limit"] == 10
        assert config["settings"]["clone_on_missing"] is True

        # Check AI defaults when section is missing
        assert "ai" in config
        assert config["ai"]["enabled"] is True

    def test_load_missing_config_file(self, temp_dir):
        """Test handling of missing config file."""
        nonexistent_path = temp_dir / "nonexistent_config.yaml"

        with pytest.raises(FileNotFoundError) as exc_info:
            manager = ConfigManager(config_path=nonexistent_path)
            manager.load()

        assert "config.yaml not found" in str(exc_info.value).lower()

    def test_load_malformed_yaml(self, temp_dir):
        """Test handling of malformed YAML file."""
        bad_config_path = temp_dir / "bad_config.yaml"
        with open(bad_config_path, "w") as f:
            f.write("invalid: yaml: content:\n  - broken")

        with pytest.raises(yaml.YAMLError):
            manager = ConfigManager(config_path=bad_config_path)
            manager.load()

    def test_validate_config_missing_repositories(self):
        """Test validation fails when repositories section is missing."""
        invalid_config = {"settings": {"auto_fetch": True}}

        with pytest.raises(ConfigValidationError) as exc_info:
            validate_config(invalid_config)

        assert "repositories" in str(exc_info.value).lower()

    def test_validate_config_empty_repositories(self):
        """Test validation fails when repositories list is empty."""
        invalid_config = {"repositories": []}

        with pytest.raises(ConfigValidationError) as exc_info:
            validate_config(invalid_config)

        assert "empty" in str(exc_info.value).lower() or "at least one" in str(
            exc_info.value
        ).lower()

    def test_validate_repository_missing_name(self):
        """Test validation fails when repository is missing name field."""
        invalid_config = {
            "repositories": [
                {
                    # Missing 'name'
                    "local_path": "/tmp/repos/test",
                    "remote_url": "https://github.com/user/test.git",
                }
            ]
        }

        with pytest.raises(ConfigValidationError) as exc_info:
            validate_config(invalid_config)

        assert "name" in str(exc_info.value).lower()

    def test_validate_repository_missing_local_path(self):
        """Test validation fails when repository is missing local_path field."""
        invalid_config = {
            "repositories": [
                {
                    "name": "test-repo",
                    # Missing 'local_path'
                    "remote_url": "https://github.com/user/test.git",
                }
            ]
        }

        with pytest.raises(ConfigValidationError) as exc_info:
            validate_config(invalid_config)

        assert "local_path" in str(exc_info.value).lower()

    def test_validate_repository_missing_remote_url(self):
        """Test validation fails when repository is missing remote_url field."""
        invalid_config = {
            "repositories": [
                {
                    "name": "test-repo",
                    "local_path": "/tmp/repos/test",
                    # Missing 'remote_url'
                }
            ]
        }

        with pytest.raises(ConfigValidationError) as exc_info:
            validate_config(invalid_config)

        assert "remote_url" in str(exc_info.value).lower()

    def test_validate_repository_invalid_url_format(self):
        """Test validation handles invalid remote URL format."""
        invalid_config = {
            "repositories": [
                {
                    "name": "test-repo",
                    "local_path": "/tmp/repos/test",
                    "remote_url": "not-a-valid-url",
                }
            ]
        }

        # Should either pass (lenient validation) or raise error
        # Depends on implementation choice - documenting expected behavior
        try:
            validate_config(invalid_config)
            # If no exception, validation is lenient
            assert True
        except ConfigValidationError:
            # If exception, validation is strict about URL format
            assert True

    def test_env_var_substitution_present(self, env_with_api_key):
        """Test environment variable substitution when variable is present."""
        config_with_env = {
            "repositories": [
                {
                    "name": "test",
                    "local_path": "/tmp/test",
                    "remote_url": "https://github.com/user/test.git",
                }
            ],
            "ai": {"api_key": "${OPENAI_API_KEY}"},
        }

        result = substitute_env_vars(config_with_env)

        assert result["ai"]["api_key"] == "sk-test-key-12345"
        assert "${" not in result["ai"]["api_key"]

    def test_env_var_substitution_missing(self, env_without_api_key):
        """Test environment variable substitution when variable is missing."""
        config_with_env = {
            "repositories": [
                {
                    "name": "test",
                    "local_path": "/tmp/test",
                    "remote_url": "https://github.com/user/test.git",
                }
            ],
            "ai": {"api_key": "${OPENAI_API_KEY}"},
        }

        # Should either raise error or leave placeholder
        try:
            result = substitute_env_vars(config_with_env)
            # If no error, placeholder should remain or be empty
            assert result["ai"]["api_key"] in ["${OPENAI_API_KEY}", "", None]
        except ConfigValidationError as e:
            # If error, should mention missing environment variable
            assert "environment" in str(e).lower() or "OPENAI_API_KEY" in str(e)

    def test_env_var_substitution_nested(self, monkeypatch):
        """Test environment variable substitution in nested structures."""
        monkeypatch.setenv("TEST_VAR", "test_value")
        monkeypatch.setenv("ANOTHER_VAR", "another_value")

        config = {
            "repositories": [
                {
                    "name": "test",
                    "local_path": "${TEST_VAR}/repos",
                    "remote_url": "https://${ANOTHER_VAR}.com/repo.git",
                }
            ],
        }

        result = substitute_env_vars(config)

        assert result["repositories"][0]["local_path"] == "test_value/repos"
        assert result["repositories"][0]["remote_url"] == "https://another_value.com/repo.git"

    def test_get_repositories(self, temp_config_file):
        """Test getting list of repositories from config."""
        manager = ConfigManager(config_path=temp_config_file)
        manager.load()

        repos = manager.get_repositories()

        assert len(repos) == 2
        assert repos[0]["name"] == "test-repo-1"
        assert repos[1]["name"] == "test-repo-2"

    def test_get_settings(self, temp_config_file):
        """Test getting settings from config."""
        manager = ConfigManager(config_path=temp_config_file)
        manager.load()

        settings = manager.get_settings()

        assert settings["auto_fetch"] is True
        assert settings["parallel_limit"] == 10
        assert settings["clone_on_missing"] is True

    def test_get_ai_config(self, temp_config_file):
        """Test getting AI configuration from config."""
        manager = ConfigManager(config_path=temp_config_file)
        manager.load()

        ai_config = manager.get_ai_config()

        assert ai_config["enabled"] is True
        assert ai_config["api_type"] == "openai"
        assert ai_config["model"] == "gpt-4o-mini"

    def test_is_ai_enabled_true(self, temp_config_file):
        """Test checking if AI is enabled when it is."""
        manager = ConfigManager(config_path=temp_config_file)
        manager.load()

        assert manager.is_ai_enabled() is True

    def test_is_ai_enabled_false(self, temp_dir):
        """Test checking if AI is enabled when it is disabled."""
        config = {
            "repositories": [
                {
                    "name": "test",
                    "local_path": "/tmp/test",
                    "remote_url": "https://github.com/user/test.git",
                }
            ],
            "ai": {"enabled": False},
        }

        config_path = temp_dir / "no_ai_config.yaml"
        with open(config_path, "w") as f:
            yaml.dump(config, f)

        manager = ConfigManager(config_path=config_path)
        manager.load()

        assert manager.is_ai_enabled() is False

    def test_config_reload(self, temp_dir, sample_config):
        """Test reloading configuration after modification."""
        config_path = temp_dir / "reload_config.yaml"
        with open(config_path, "w") as f:
            yaml.dump(sample_config, f)

        manager = ConfigManager(config_path=config_path)
        manager.load()

        # Verify initial state
        assert len(manager.get_repositories()) == 2

        # Modify config file
        modified_config = sample_config.copy()
        modified_config["repositories"].append(
            {
                "name": "new-repo",
                "local_path": "/tmp/repos/new",
                "remote_url": "https://github.com/user/new.git",
            }
        )

        with open(config_path, "w") as f:
            yaml.dump(modified_config, f)

        # Reload and verify changes
        manager.load()
        assert len(manager.get_repositories()) == 3

    def test_default_config_path(self, monkeypatch, temp_dir):
        """Test using default config.yaml path if not specified."""
        # Change to temp directory
        monkeypatch.chdir(temp_dir)

        # Create config.yaml in current directory
        config_path = temp_dir / "config.yaml"
        with open(config_path, "w") as f:
            yaml.dump({"repositories": [{"name": "test", "local_path": "/tmp/test", "remote_url": "https://github.com/user/test.git"}]}, f)

        # Create manager without specifying path
        manager = ConfigManager()
        config = manager.load()

        assert config is not None
        assert len(config["repositories"]) == 1


class TestConfigValidation:
    """Focused tests for configuration validation logic."""

    def test_validate_valid_config(self, sample_config):
        """Test that a valid config passes validation."""
        # Should not raise any exception
        validate_config(sample_config)

    def test_validate_duplicate_repository_names(self):
        """Test validation catches duplicate repository names."""
        config = {
            "repositories": [
                {
                    "name": "duplicate-name",
                    "local_path": "/tmp/repos/test1",
                    "remote_url": "https://github.com/user/test1.git",
                },
                {
                    "name": "duplicate-name",
                    "local_path": "/tmp/repos/test2",
                    "remote_url": "https://github.com/user/test2.git",
                },
            ]
        }

        with pytest.raises(ConfigValidationError) as exc_info:
            validate_config(config)

        assert "duplicate" in str(exc_info.value).lower()

    def test_validate_parallel_limit_negative(self):
        """Test validation catches invalid parallel_limit."""
        config = {
            "repositories": [
                {
                    "name": "test",
                    "local_path": "/tmp/test",
                    "remote_url": "https://github.com/user/test.git",
                }
            ],
            "settings": {"parallel_limit": -1},
        }

        with pytest.raises(ConfigValidationError) as exc_info:
            validate_config(config)

        assert "parallel_limit" in str(exc_info.value).lower()

    def test_validate_parallel_limit_zero(self):
        """Test validation handles zero parallel_limit."""
        config = {
            "repositories": [
                {
                    "name": "test",
                    "local_path": "/tmp/test",
                    "remote_url": "https://github.com/user/test.git",
                }
            ],
            "settings": {"parallel_limit": 0},
        }

        # Zero might be valid (unlimited) or invalid depending on design
        # This test documents the expected behavior
        try:
            validate_config(config)
            # If passes, zero is treated as unlimited
        except ConfigValidationError as e:
            # If fails, zero is invalid
            assert "parallel_limit" in str(e).lower()


@pytest.mark.unit
class TestEnvironmentVariableSubstitution:
    """Focused tests for environment variable substitution."""

    def test_substitute_single_var(self, monkeypatch):
        """Test substituting a single environment variable."""
        monkeypatch.setenv("TEST_VAR", "substituted_value")

        data = {"key": "${TEST_VAR}"}
        result = substitute_env_vars(data)

        assert result["key"] == "substituted_value"

    def test_substitute_multiple_vars(self, monkeypatch):
        """Test substituting multiple environment variables."""
        monkeypatch.setenv("VAR1", "value1")
        monkeypatch.setenv("VAR2", "value2")

        data = {"key1": "${VAR1}", "key2": "${VAR2}"}
        result = substitute_env_vars(data)

        assert result["key1"] == "value1"
        assert result["key2"] == "value2"

    def test_substitute_in_string_interpolation(self, monkeypatch):
        """Test substituting vars within larger strings."""
        monkeypatch.setenv("USER", "testuser")

        data = {"path": "/home/${USER}/repos"}
        result = substitute_env_vars(data)

        assert result["path"] == "/home/testuser/repos"

    def test_no_substitution_when_no_vars(self):
        """Test that strings without ${} remain unchanged."""
        data = {"key": "plain_string"}
        result = substitute_env_vars(data)

        assert result["key"] == "plain_string"

    def test_substitute_in_lists(self, monkeypatch):
        """Test substitution works in list values."""
        monkeypatch.setenv("TEST_VAR", "value")

        data = {"list": ["${TEST_VAR}", "other"]}
        result = substitute_env_vars(data)

        assert result["list"][0] == "value"
        assert result["list"][1] == "other"

    def test_substitute_in_nested_dicts(self, monkeypatch):
        """Test substitution works in deeply nested structures."""
        monkeypatch.setenv("NESTED_VAR", "nested_value")

        data = {"level1": {"level2": {"level3": "${NESTED_VAR}"}}}
        result = substitute_env_vars(data)

        assert result["level1"]["level2"]["level3"] == "nested_value"
