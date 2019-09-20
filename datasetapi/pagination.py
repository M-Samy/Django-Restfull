from rest_framework.pagination import (
    LimitOffsetPagination,
    PageNumberPagination
    )

class DataLimitOffsetPagination(LimitOffsetPagination):
    default_limit=10
    max_limit=100


class DataPageNumberPagination(PageNumberPagination):
    page_size = 10