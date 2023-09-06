from ninja import NinjaAPI, Router
from django.http import HttpResponse
from django.shortcuts import render

api = NinjaAPI()
router = Router()

@api.get("/hello")
def hello(request):
    return "Hello world htmx"

@router.get("/index")
def index(request):
    return render(request, "index.html")

@api.get("/htmx-magic-happens")
def magic(request):
    return HttpResponse("Ta! Daaa!")
