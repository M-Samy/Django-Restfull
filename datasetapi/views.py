from django.shortcuts import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from . models import Dataset as DatasetModel
from .serializers import DataSerializer
from rest_framework.pagination import PageNumberPagination
from rest_framework import filters
from django.db.models import Q


class Dataset(APIView):
    def get(self, request):
        try:
            paginator = PageNumberPagination()
            paginator.page_size = 100            
            dataset = DatasetModel.objects.all()
            query_param = self.request.query_params.get('q', None)
            if query_param:
                dataset = dataset.filter(
                    Q(channel__icontains = query_param) |
                    Q(country__icontains = query_param) |
                    Q(os__icontains = query_param)
                    )
            result_page = paginator.paginate_queryset(dataset, request)
            serializer = DataSerializer(result_page, many=True)
            return paginator.get_paginated_response(serializer.data)
        except Exception as e:
            raise Http404('Requested is failed with error {}'.format(e.__repr__))
