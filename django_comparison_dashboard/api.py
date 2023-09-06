from ninja import NinjaAPI

api = NinjaAPI(urls_namespace="comparison_dashboard")


@api.get("/hello")
def hello(request):
    return "Hello world"
