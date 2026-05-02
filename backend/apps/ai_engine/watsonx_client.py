from ibm_watsonx_ai import APIClient, Credentials
from ibm_watsonx_ai.foundation_models import ModelInference
from decouple import config


def get_watsonx_client():
    credentials = Credentials(
        url=config('IBM_WATSONX_URL'),
        api_key=config('IBM_WATSONX_API_KEY'),
    )
    client = APIClient(credentials)
    return client


def get_model():
    credentials = Credentials(
        url=config('IBM_WATSONX_URL'),
        api_key=config('IBM_WATSONX_API_KEY'),
    )
    model = ModelInference(
        model_id="ibm/granite-13b-code-instruct-v2",
        credentials=credentials,
        project_id=config('IBM_WATSONX_PROJECT_ID'),
        params={
            "max_new_tokens": 1000,
            "temperature": 0.2,
            "repetition_penalty": 1.1,
        }
    )
    return model


def generate_tests(code_snippet: str, language: str = "python") -> str:
    model = get_model()
    prompt = f"""You are an expert software engineer. Generate comprehensive unit tests for the following {language} code.
Include edge cases, error handling, and normal flow tests.
Return only the test code with no explanation.

Code to test:
{code_snippet}

Generated tests:"""
    
    response = model.generate_text(prompt=prompt)
    return response


def update_tests(original_code: str, updated_code: str, existing_tests: str) -> str:
    model = get_model()
    prompt = f"""You are an expert software engineer. Update the existing tests to match the updated code.
Only modify tests that are affected by the code changes.
Return only the updated test code with no explanation.

Original code:
{original_code}

Updated code:
{updated_code}

Existing tests:
{existing_tests}

Updated tests:"""
    
    response = model.generate_text(prompt=prompt)
    return response

# Made with Bob
