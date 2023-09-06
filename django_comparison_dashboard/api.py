from ninja import NinjaAPI
from django.http import HttpResponse

api = NinjaAPI()


@api.get("/hello")
def hello(request):
    return "Hello world htmx"

@api.get("/htmx-magic-happens")
def magic(request):
    return HttpResponse("Ta! Daaa!")
