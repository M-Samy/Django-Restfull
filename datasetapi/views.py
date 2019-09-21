from django.shortcuts import Http404
from rest_framework.views import APIView
from . models import Dataset as DatasetModel
from .serializers import DataSerializer
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from datetime import datetime


class Dataset(APIView):
    def get(self, request):
        try:
            paginator = PageNumberPagination()
            paginator.page_size = 100            
            dataset = DatasetModel.objects.all()
            query_param = self.request.query_params.get('q', None)
            from_date = self.request.query_params.get('from_date', None)
            to_date = self.request.query_params.get('to_date', None)
            order_field = self.request.query_params.get('order', None)
            order_type = self.request.query_params.get('type', 'ASC')

            if query_param:
                dataset = dataset.filter(
                    Q(channel__icontains = query_param) |
                    Q(country__icontains = query_param) |
                    Q(os__icontains = query_param)
                    )

            dataset = self.get_data_within_a_daterange(from_date, to_date, dataset)
            dataset = self.get_data_ordered(order_field, order_type, dataset)

            result_page = paginator.paginate_queryset(dataset, request)
            serializer = DataSerializer(result_page, many=True)
            return paginator.get_paginated_response(serializer.data)
        except Exception as e:
            raise Http404('Requested is failed with error {}'.format(e.__repr__))

    def get_data_within_a_daterange(self, from_date, to_date, data):
        try:
            if from_date and to_date:
                from_date = datetime.strptime(from_date,"%Y-%m-%d")
                to_date = datetime.strptime(to_date,"%Y-%m-%d")
                data = data.filter(date__range=[from_date, to_date])
            return data
        except Exception as e:
            raise Http404('Failed filter data within a range of dates {}'.format(e.__repr__))

    def get_data_ordered(self, order_field, order_type, data):
        try:
            model_fields = DatasetModel._meta.ordering
            if order_field and order_field in model_fields:
                data = data.order_by(order_field)

            if order_type.upper() == "DESC":
                order_field = "-" + order_field

            return data
        except Exception as e:
            raise Http404('Failed ordering data by {} due to {}'.format(order_field, e.__repr__))
