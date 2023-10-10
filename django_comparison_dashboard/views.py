from django.http.response import JsonResponse

from . import preprocessing


def get_scalar_data(request):
    query = request.GET.dict()
    return JsonResponse(preprocessing.get_scalar_data(query).to_dict(orient="records"), safe=False)
