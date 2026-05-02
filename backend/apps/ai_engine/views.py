from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .watsonx_client import generate_tests, update_tests


@api_view(['POST'])
@permission_classes([AllowAny])
def generate_tests_view(request):
    code_snippet = request.data.get('code', '')
    language = request.data.get('language', 'python')

    if not code_snippet:
        return Response(
            {'error': 'No code provided'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        tests = generate_tests(code_snippet, language)
        return Response({
            'status': 'success',
            'tests': tests,
            'language': language
        })
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def update_tests_view(request):
    original_code = request.data.get('original_code', '')
    updated_code = request.data.get('updated_code', '')
    existing_tests = request.data.get('existing_tests', '')

    if not all([original_code, updated_code, existing_tests]):
        return Response(
            {'error': 'original_code, updated_code and existing_tests are all required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        updated = update_tests(original_code, updated_code, existing_tests)
        return Response({
            'status': 'success',
            'updated_tests': updated
        })
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# Made with Bob
