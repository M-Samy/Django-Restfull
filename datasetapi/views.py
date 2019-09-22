from django.shortcuts import Http404
from rest_framework.views import APIView
from . models import Dataset as DatasetModel
from .serializers import DataSerializer
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from datetime import datetime
import datetime as dt
from rest_framework.response import Response
from django.db.models import Sum


class Dataset(APIView):
    def get(self, request):
        try:
            paginator = PageNumberPagination()
            paginator.page_size = 100
            query_param = self.request.query_params.get('q', None)
            from_date = self.request.query_params.get('from_date', dt.date.today().strftime("%Y-%m-%d"))
            to_date = self.request.query_params.get('to_date', from_date)
            order_field = self.request.query_params.get('order', None)
            order_type = self.request.query_params.get('type', 'ASC')
            returned_fields = self.request.query_params.get('fields', None)
            group_fields = self.request.query_params.get('group_fields', None)
            cpi = self.request.query_params.get('cpi', 0)

            if query_param:
                dataset = DatasetModel.objects.filter(
                    Q(channel__icontains = query_param) |
                    Q(country__icontains = query_param) |
                    Q(os__icontains = query_param)
                    )
            else:
                dataset = DatasetModel.objects.all()

            data_serializer = DataSerializer()
            self.handle_returned_fields(returned_fields, dataset, data_serializer)
            dataset = self.get_data_within_a_daterange(from_date, to_date, dataset)
            dataset = self.get_data_ordered(order_field, order_type, dataset)
            cpi_value = self.handle_cpi_value(cpi, dataset)

            # Only aggregated by Impressions and Clicks as test case.
            aggs = self.get_aggregated_values(group_fields, dataset)

            result_page = paginator.paginate_queryset(dataset, request)

            serializer = DataSerializer(result_page, many=True)
            data = paginator.get_paginated_response(serializer.data)
            res = {'res': data.data, 'total_cpi': cpi_value, 'aggregations': aggs}
            return Response(res)
        except Exception as e:
            print(e)
            raise Http404('Requested is failed with error {}'.format(e.__doc__))

    def get_data_within_a_daterange(self, from_date, to_date, data):
        try:
            if from_date and to_date:
                from_date = datetime.strptime(from_date,"%Y-%m-%d")
                to_date = datetime.strptime(to_date,"%Y-%m-%d")
                data = data.filter(date__range=[from_date, to_date])
            return data
        except Exception as e:
            raise Http404('Failed filter data within a range of dates {}'.format(e.__doc__))

    def get_data_ordered(self, order_field, order_type, data):
        try:
            model_fields = DatasetModel._meta.ordering

            if (order_field) and (order_field in model_fields):
                if order_type.upper() == "DESC":
                    order_field = "-" + order_field
                data = data.order_by(order_field)

            return data
        except Exception as e:
            raise Http404('Failed ordering data by {} due to {}'.format(order_field, e.__doc__))

    def handle_returned_fields(self, returned_fields, data, serializer):
        try:
            model_fields = DatasetModel._meta.ordering
            if returned_fields:
                fields_list = [field.strip() for field in returned_fields.split(',')]
            else:
                fields_list = "__all__"
            # Check if all returned fields client send is a real fields in Dataset Model.
            if all(elem.strip() in model_fields for elem in fields_list):
                serializer.Meta.fields = fields_list
            else:
                pass
        except Exception as e:
            raise Http404('Failed to get fields client want to back in response due to {}'.format(e.__doc__))

    def handle_cpi_value(self, cpi, dataset):
        try:
            cpi_value=None
            if int(cpi):
                cpi = dataset.aggregate(num_installs=Sum('installs'), num_spend=Sum('spend'))
                cpi_value = cpi['num_spend'] / cpi['num_installs']
            return cpi_value
        except Exception as e:
            raise Http404('Failed to get cpi due to {}'.format(e.__doc__))

    def get_aggregated_values(self, group_fields, dataset):
        try:
            model_fields = DatasetModel._meta.ordering
            aggs = None
            if group_fields:
                fields_list = [field.strip() for field in group_fields.split(',')]
                # Check if all returned fields client send is a real fields in Dataset Model.
                if all(elem.strip() in model_fields for elem in fields_list):
                    aggs = dataset.aggregate(sum_impressions=Sum("impressions"), sum_clicks=Sum("clicks"))
            return aggs
        except Exception as e:
            raise Http404('Failed to get aggregated values due to {}'.format(e.__doc__))
