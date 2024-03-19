from django.urls import path
from .views import CandidateViewSet, CandidateSearchView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'candidates', CandidateViewSet)

urlpatterns = [
    path('candidates/search/', CandidateSearchView.as_view(), name='candidate_search'),
]

urlpatterns += router.urls
