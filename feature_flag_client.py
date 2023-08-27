import json
import logging
from typing import Any, Union
import httpx


class FeatureFlagClient:
    """
    The provided code serves as a client interface for interacting with a feature flag service 
    through HTTP requests. Feature flags are used to control the behavior of software applications 
    without requiring code changes. This class encapsulates the logic for evaluating different 
    variations of feature flags, both boolean and string, based on the given flag key and optional 
    default values. It employs the httpx library for making HTTP requests.
    """

    def __init__(self, http_client: httpx.Client, curr_env: str):
        """
        Initialize a FeatureFlagClient instance.

        Args:
            http_client (httpx.Client): An instance of the HTTP client for making requests.
            curr_env (str): The current environment identifier.
        """
        self._client = http_client
        self._curr_env = curr_env

    def evaluate_boolean_variation(
        self,
        flag_key: str,
        default_value: Union[bool, None] = None,
        assignment_id: Any = None
    ) -> bool:
        """
        Evaluate a boolean variation of a feature flag.

        Args:
            flag_key (str): The key of the feature flag to evaluate.
            default_value (Union[bool, None], optional): The default boolean value. Defaults to None.
            assignment_id (Any, optional): An identifier for user assignment. Defaults to None.

        Returns:
            bool: The evaluated boolean variation.
        Raises:
            TypeError: If default_value is not a boolean or None.
        """
        if isinstance(default_value, bool) or default_value is None:
            return self._evaluate_feature_flag_variation(
                flag_key, default_value, assignment_id
            )
        raise TypeError("'default_value' must be None or a boolean")

    def evaluate_string_variation(
        self,
        flag_key: str,
        default_value: Union[str, None] = None,
        assignment_id: Any = None
    ) -> str:
        """
        Evaluate a string variation of a feature flag.

        Args:
            flag_key (str): The key of the feature flag to evaluate.
            default_value (Union[str, None], optional): The default string value. Defaults to None.
            assignment_id (Any, optional): An identifier for user assignment. Defaults to None.

        Returns:
            str: The evaluated string variation.
        Raises:
            TypeError: If default_value is not a string or None.
        """
        if isinstance(default_value, str) or default_value is None:
            return self._evaluate_feature_flag_variation(
                flag_key, default_value, assignment_id
            )
        raise TypeError("'default_value' must be a non-empty string")

    def _evaluate_feature_flag_variation(
        self,
        flag_key: str,
        default_value: Any = None,
        assignment_id: Any = None,
    ) -> Union[bool, str, object]:
        """
        Evaluate a feature flag variation and return the evaluated value.

        Args:
            flag_key (str): The key of the feature flag to evaluate.
            default_value (Any, optional): The default value. Defaults to None.
            assignment_id (Any, optional): An identifier for user assignment. Defaults to None.

        Returns:
            Union[bool, str, object]: The evaluated value of the feature flag.

        Private Method.
        """
        url = ("/api/flags/{}/env/{}/users/").format(
            flag_key,
            self._curr_env
        )
        basic_json_data = self._get_basic_json_data(assignment_id)
        headers = {"Content-Type": "application/json"}
        json_data = {
            **basic_json_data,
            "defaultValue": str(default_value)
        }
        response = self._client.post(url, json=json_data, headers=headers)
        variation_name = None
        if response.status_code == httpx.codes.OK:
            response_text = json.loads(response.text)
            variation_name = response["flagValue"]
            variation_value = response_text["payload"]
            # Check for flag not found
            if variation_name is None:
                message = (
                    f"flag_key={flag_key} not found "
                    f"or inactive in current env={self._curr_env}, "
                    f"falling back to default_value={default_value}."
                )
                logging.error(message)
                variation_value = default_value
            # Check for flag variation evaluates to None
            elif variation_value is None:
                message = (
                    f"flag_key={flag_key} evaluates to "
                    f"variation_value={variation_value}, "
                    f"falling back to default_value={default_value}."
                )
                logging.info(message)
                variation_value = default_value
            else:
                message = (
                    f"flag_key={flag_key} evaluates to a valid "
                    f"variation_value={variation_value}."
                )
                logging.info(message)
        else:
            message = (
                f"Failed to evaluate feature flag variation. "
                f"Using the default_value={default_value}. "
                f"Error message: {response.content}. "
            )
            logging.error(message)
            variation_value = default_value
        return variation_value

    def _get_basic_json_data(self, assignment_id: Any):
        """
        Generate and return basic JSON data for the request payload.

        Args:
            assignment_id (Any): An identifier for user assignment.

        Returns:
            dict: Basic JSON data for the request payload.

        Private Method.
        """
        return {
            # Some JSON data
        }
