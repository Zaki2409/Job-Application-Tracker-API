# applications/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import JobApplicationViewSet, SummaryAPIView, AIFollowUpAPIView

# Create a router and register the ViewSet
router = DefaultRouter()
router.register(r'applications', JobApplicationViewSet, basename='jobapplication')

# The router automatically generates:
# - GET /applications/           (list)
# - POST /applications/          (create)
# - GET /applications/{id}/      (retrieve)
# - PUT /applications/{id}/      (update)
# - PATCH /applications/{id}/    (partial update)
# - DELETE /applications/{id}/   (destroy)

urlpatterns = [
    # Include all CRUD routes from the router
    path('', include(router.urls)),
    
    # Custom endpoints (not covered by the router)
    path('summary/', SummaryAPIView.as_view(), name='summary'),
    path('applications/<int:pk>/generate-followup/', AIFollowUpAPIView.as_view(), name='followup'),
]