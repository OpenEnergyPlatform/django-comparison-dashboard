from django.http.response import JsonResponse

from . import queries
from .utils import prepare_query


def get_scalar_data(request):
    filters, group_by = prepare_query(request.GET.dict())
    return JsonResponse(list(queries.get_scalar_data(filters, group_by)), safe=False)
