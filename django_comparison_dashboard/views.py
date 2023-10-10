from django.http.response import HttpResponse

from . import graphs, preprocessing


def plot_scalar_data(request):
    query = request.GET.dict()
    filters, groupby, units, plot_options = preprocessing.prepare_query(query)
    df = preprocessing.get_scalar_data(filters, groupby, units).to_dict(orient="records")
    return HttpResponse(graphs.bar_plot(df, plot_options).to_html())
