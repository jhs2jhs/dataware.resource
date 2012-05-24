from django.http import HttpResponse

def hello(request):
    return HttpResponse('hello, resource')

#####registeration with catalog#####
def catalog_register(request):
    txt = request.GET
    print txt
    return HttpResponse(txt)
