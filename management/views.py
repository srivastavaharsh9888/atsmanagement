from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import CandidateProfile
from .serializers import CandidateSerializer
from lib.QueryBuilder import QueryBuilder


class CandidateViewSet(viewsets.ModelViewSet):
    queryset = CandidateProfile.objects.all()
    serializer_class = CandidateSerializer

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)


class CandidateSearchView(APIView):
    def post(self, request, format=None):
        handler = QueryBuilder(CandidateProfile, request.data)
        queryset = handler.get_query()
        serializer = CandidateSerializer(queryset, many=True)
        candidates = serializer.data

        if 'relevance_search' in request.data:
            query_field = list(dict(request.data['relevance_search']).keys())[0]
            query_words = request.data['relevance_search'][query_field]

            scored_candidates = []
            for candidate in candidates:
                relevance = sum(1 for word in query_words if word.lower() in candidate.get(query_field, '').lower())
                scored_candidates.append((candidate, relevance))

            scored_candidates.sort(key=lambda x: x[1], reverse=True)
            return Response(scored_candidates, status=status.HTTP_200_OK)

        return Response(candidates, status=status.HTTP_200_OK)
