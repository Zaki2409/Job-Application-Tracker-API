from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Count
from django.shortcuts import get_object_or_404
from .models import JobApplication
from .serializers import JobApplicationSerializer
import os
import openai
from dotenv import load_dotenv

# Load API key from .env
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

class JobApplicationViewSet(viewsets.ModelViewSet):
    queryset = JobApplication.objects.all().order_by('-applied_date')
    serializer_class = JobApplicationSerializer

    def get_queryset(self):
        """
        Allows filtering by status via query parameter: ?status=interviewing
        Example: GET /api/applications/?status=interviewing
        """
        queryset = super().get_queryset()
        status_param = self.request.query_params.get('status')
        if status_param:
            # Validate that the status is one of the allowed choices
            valid_statuses = dict(JobApplication.STATUS_CHOICES).keys()
            if status_param in valid_statuses:
                queryset = queryset.filter(status=status_param)
        return queryset

class SummaryAPIView(APIView):
    def get(self, request):
        # Get counts for each status that actually exist
        counts = (
            JobApplication.objects
            .values('status')
            .annotate(count=Count('id'))
        )
        # Convert to dictionary: {'applied': 5, 'interviewing': 2, ...}
        count_dict = {item['status']: item['count'] for item in counts}

        # Ensure all four statuses appear in response (with 0 if missing)
        result = {
            'applied': count_dict.get('applied', 0),
            'interviewing': count_dict.get('interviewing', 0),
            'rejected': count_dict.get('rejected', 0),
            'offered': count_dict.get('offered', 0),
        }
        return Response(result)

class AIFollowUpAPIView(APIView):
    def post(self, request, pk):
        """
        Expects URL: /api/applications/<id>/followup/
        Generates a follow-up email using OpenAI.
        """
        # Get the job application or return 404
        job = get_object_or_404(JobApplication, pk=pk)

        # Construct the prompt
        prompt = (
            f"Write a concise, professional follow-up email for a job application "
            f"to {job.company} for the {job.role} position. "
            f"Keep it polite, short, and express continued interest."
        )

        # Call OpenAI API
        try:
            if not openai.api_key:
                return Response(
                    {"error": "OpenAI API key not configured. Check your .env file."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  # or "gpt-4" if you have access
                messages=[
                    {"role": "system", "content": "You are a helpful career assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=300
            )

            email_text = response.choices[0].message.content.strip()
            return Response({"follow_up_email": email_text})

        except openai.error.AuthenticationError:
            return Response(
                {"error": "Invalid OpenAI API key. Please check your .env file."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        except openai.error.RateLimitError:
            return Response(
                {"error": "OpenAI rate limit exceeded. Try again later."},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        except openai.error.APIError as e:
            return Response(
                {"error": f"OpenAI API error: {str(e)}"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as e:
            return Response(
                {"error": f"Unexpected error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )