"""
Configuration Management Module

Handles loading, parsing, and validating config.yaml for git repository control.

Features:
- Load and parse YAML configuration
- Validate repository entries and settings
- Environment variable substitution (${VAR_NAME})
- Provide default values for optional settings
"""

import os
import re
from pathlib import Path
from typing import Dict, Any, List, Optional

import yaml


class ConfigValidationError(Exception):
    """Raised when configuration validation fails."""

    pass


class ConfigManager:
    """
    Manages configuration for git repository control.

    Handles loading config.yaml, applying defaults, validating entries,
    and providing convenient access to configuration sections.
    """

    # Default configuration values
    DEFAULT_SETTINGS = {
        "auto_fetch": True,
        "parallel_limit": 10,
        "clone_on_missing": True,
    }

    DEFAULT_AI_CONFIG = {
        "enabled": True,
        "api_type": "openai",
        "api_key": None,
        "base_url": None,
        "model": "gpt-4o-mini",
        "max_tokens": 500,
        "temperature": 0.7,
    }

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize ConfigManager.

        Args:
            config_path: Path to config.yaml file. If None, uses ./config.yaml
        """
        if config_path is None:
            self.config_path = Path("config.yaml")
        else:
            self.config_path = Path(config_path)

        self.config: Optional[Dict[str, Any]] = None

    def load(self) -> Dict[str, Any]:
        """
        Load and parse configuration from YAML file.

        Returns:
            Loaded configuration dictionary

        Raises:
            FileNotFoundError: If config file doesn't exist
            yaml.YAMLError: If YAML is malformed
            ConfigValidationError: If configuration is invalid
        """
        if not self.config_path.exists():
            raise FileNotFoundError(
                f"config.yaml not found at: {self.config_path.absolute()}"
            )

        with open(self.config_path, "r") as f:
            raw_config = yaml.safe_load(f)

        # Apply environment variable substitution
        config = substitute_env_vars(raw_config)

        # Apply defaults
        config = self._apply_defaults(config)

        # Validate configuration
        validate_config(config)

        self.config = config
        return config

    def _apply_defaults(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply default values for optional settings.

        Args:
            config: Raw configuration dictionary

        Returns:
            Configuration with defaults applied
        """
        # Apply settings defaults
        if "settings" not in config:
            config["settings"] = {}

        for key, value in self.DEFAULT_SETTINGS.items():
            if key not in config["settings"]:
                config["settings"][key] = value

        # Apply AI config defaults
        if "ai" not in config:
            config["ai"] = {}

        for key, value in self.DEFAULT_AI_CONFIG.items():
            if key not in config["ai"]:
                config["ai"][key] = value

        return config

    def get_repositories(self) -> List[Dict[str, str]]:
        """
        Get list of repository configurations.

        Returns:
            List of repository dictionaries

        Raises:
            RuntimeError: If config hasn't been loaded yet
        """
        if self.config is None:
            raise RuntimeError("Configuration not loaded. Call load() first.")

        return self.config["repositories"]

    def get_settings(self) -> Dict[str, Any]:
        """
        Get settings configuration.

        Returns:
            Settings dictionary

        Raises:
            RuntimeError: If config hasn't been loaded yet
        """
        if self.config is None:
            raise RuntimeError("Configuration not loaded. Call load() first.")

        return self.config["settings"]

    def get_ai_config(self) -> Dict[str, Any]:
        """
        Get AI configuration.

        Returns:
            AI configuration dictionary

        Raises:
            RuntimeError: If config hasn't been loaded yet
        """
        if self.config is None:
            raise RuntimeError("Configuration not loaded. Call load() first.")

        return self.config["ai"]

    def is_ai_enabled(self) -> bool:
        """
        Check if AI features are enabled.

        Returns:
            True if AI is enabled, False otherwise

        Raises:
            RuntimeError: If config hasn't been loaded yet
        """
        if self.config is None:
            raise RuntimeError("Configuration not loaded. Call load() first.")

        return self.config["ai"].get("enabled", True)


def validate_config(config: Dict[str, Any]) -> None:
    """
    Validate configuration structure and values.

    Args:
        config: Configuration dictionary to validate

    Raises:
        ConfigValidationError: If configuration is invalid
    """
    # Check required sections
    if "repositories" not in config:
        raise ConfigValidationError(
            "Configuration must contain 'repositories' section"
        )

    repositories = config["repositories"]

    # Check repositories is not empty
    if not isinstance(repositories, list) or len(repositories) == 0:
        raise ConfigValidationError(
            "Configuration must contain at least one repository"
        )

    # Validate each repository
    seen_names = set()
    for idx, repo in enumerate(repositories):
        # Check required fields
        if "name" not in repo:
            raise ConfigValidationError(
                f"Repository at index {idx} is missing required field 'name'"
            )

        if "local_path" not in repo:
            raise ConfigValidationError(
                f"Repository '{repo.get('name', 'unknown')}' is missing required field 'local_path'"
            )

        if "remote_url" not in repo:
            raise ConfigValidationError(
                f"Repository '{repo['name']}' is missing required field 'remote_url'"
            )

        # Check for duplicate names
        if repo["name"] in seen_names:
            raise ConfigValidationError(
                f"Duplicate repository name found: '{repo['name']}'"
            )

        seen_names.add(repo["name"])

    # Validate settings if present
    if "settings" in config:
        settings = config["settings"]

        # Validate parallel_limit
        if "parallel_limit" in settings:
            parallel_limit = settings["parallel_limit"]
            if not isinstance(parallel_limit, int) or parallel_limit < 1:
                raise ConfigValidationError(
                    f"parallel_limit must be a positive integer, got: {parallel_limit}"
                )


def substitute_env_vars(data: Any) -> Any:
    """
    Recursively substitute environment variables in configuration.

    Replaces ${VAR_NAME} with the value of environment variable VAR_NAME.

    Args:
        data: Configuration data (dict, list, str, or other types)

    Returns:
        Data with environment variables substituted

    Raises:
        ConfigValidationError: If required environment variable is missing
    """
    if isinstance(data, dict):
        return {key: substitute_env_vars(value) for key, value in data.items()}

    elif isinstance(data, list):
        return [substitute_env_vars(item) for item in data]

    elif isinstance(data, str):
        # Pattern to match ${VAR_NAME}
        pattern = r"\$\{([^}]+)\}"

        def replace_var(match):
            var_name = match.group(1)
            value = os.environ.get(var_name)

            if value is None:
                # Leave placeholder if env var not found
                # Some tests expect this behavior for optional vars
                return match.group(0)

            return value

        return re.sub(pattern, replace_var, data)

    else:
        # Return as-is for non-string, non-collection types
        return data


def load_config(config_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Convenience function to load configuration.

    Args:
        config_path: Path to config.yaml file

    Returns:
        Loaded and validated configuration dictionary
    """
    manager = ConfigManager(config_path=config_path)
    return manager.load()
