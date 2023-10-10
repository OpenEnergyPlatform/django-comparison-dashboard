from django.http.response import JsonResponse

from . import queries
from .utils import prepare_filters


def get_scalar_data(request):
    filters = prepare_filters(request.GET.dict())
    return JsonResponse(list(queries.get_scalar_data(filters).values()), safe=False)
