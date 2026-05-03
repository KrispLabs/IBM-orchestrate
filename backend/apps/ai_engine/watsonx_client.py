from decouple import config
from typing import cast, Any

_API_KEY: str = cast(str, config('IBM_WATSONX_API_KEY', default=''))
_PROJECT_ID: str = cast(str, config('IBM_WATSONX_PROJECT_ID', default=''))
_URL: str = cast(str, config('IBM_WATSONX_URL', default='https://us-south.ml.cloud.ibm.com'))

# Use mock when explicitly requested OR when no real credentials are present
_USE_MOCK: bool = (
    config('WATSONX_STATUS', default='') == 'mocked'
    or not _API_KEY
    or _API_KEY == 'your-api-key-here'
)


def _mock_generate_tests(language: str) -> str:
    templates = {
        'python': '''\
import pytest


def test_basic_functionality():
    # TODO: replace with real call to function under test
    assert True


def test_returns_non_none():
    result = object()
    assert result is not None


def test_edge_case_empty_input():
    with pytest.raises((TypeError, ValueError)):
        pass  # TODO: call function under test with empty/None input


def test_expected_output_type():
    # TODO: assert isinstance(result, expected_type)
    assert True
''',
        'javascript': '''\
describe('Generated tests', () => {
  test('basic functionality', () => {
    // TODO: import and call function under test
    expect(true).toBe(true);
  });

  test('handles null input', () => {
    expect(() => {
      // TODO: call function with null
    }).not.toThrow();
  });
});
''',
        'typescript': '''\
import { describe, test, expect } from 'vitest';

describe('Generated tests', () => {
  test('basic functionality', () => {
    // TODO: import and call function under test
    expect(true).toBe(true);
  });

  test('handles undefined input', () => {
    expect(() => {
      // TODO: call function with undefined
    }).not.toThrow();
  });
});
''',
    }
    return templates.get(language, f'// Generated test stub for {language}\n// TODO: implement\n')


def _mock_update_tests(existing_tests: str) -> str:
    return existing_tests


def _get_model() -> Any:
    from ibm_watsonx_ai import Credentials
    from ibm_watsonx_ai.foundation_models import ModelInference

    credentials = Credentials(url=_URL, api_key=_API_KEY)
    return ModelInference(
        model_id="ibm/granite-13b-code-instruct-v2",
        credentials=credentials,
        project_id=_PROJECT_ID,
        params={
            "max_new_tokens": 1000,
            "temperature": 0.2,
            "repetition_penalty": 1.1,
        },
    )


def generate_tests(code_snippet: str, language: str = "python") -> str:
    if _USE_MOCK:
        return _mock_generate_tests(language)

    prompt = (
        f"You are an expert software engineer. Generate comprehensive unit tests for the following "
        f"{language} code.\nInclude edge cases, error handling, and normal flow tests.\n"
        f"Return only the test code with no explanation.\n\nCode to test:\n{code_snippet}\n\nGenerated tests:"
    )
    try:
        model = _get_model()
        response: Any = model.generate_text(prompt=prompt)
        return str(response)
    except Exception as exc:
        raise RuntimeError(f"WatsonX generate_tests failed: {exc}") from exc


def update_tests(original_code: str, updated_code: str, existing_tests: str) -> str:
    if _USE_MOCK:
        return _mock_update_tests(existing_tests)

    prompt = (
        f"You are an expert software engineer. Update the existing tests to match the updated code.\n"
        f"Only modify tests that are affected by the code changes.\n"
        f"Return only the updated test code with no explanation.\n\n"
        f"Original code:\n{original_code}\n\nUpdated code:\n{updated_code}\n\n"
        f"Existing tests:\n{existing_tests}\n\nUpdated tests:"
    )
    try:
        model = _get_model()
        response: Any = model.generate_text(prompt=prompt)
        return str(response)
    except Exception as exc:
        raise RuntimeError(f"WatsonX update_tests failed: {exc}") from exc
