from django.shortcuts import render
from django.http import HttpResponse

def index(request):
	#context dictionary to replace template variable names
	context_dict = {'boldmessage': "Crunchy, creamy, cookie, candy, cupcake!"}
	#return a rendered response to return to client
	#note second parameter is our template
	return render(request, 'rango/index.html', context=context_dict)

def about(request):
	return HttpResponse("Rango says this here is the about page. <br/> <a href='/rango/'>Index</a>")