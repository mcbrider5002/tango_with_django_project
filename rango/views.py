from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from django.contrib.auth import authenticate, login, logout
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from datetime import datetime

def index(request):
	request.session.set_test_cookie()
	#query db for all categories currently stored
	#order by likes in descending order
	#retrieve top 5 (or all if less than five)
	#place list in context_dict to pass on to template engine
	
	category_list = Category.objects.order_by('-likes')[:5]
	page_views = Page.objects.order_by('-views')[:5]
	context_dict = {'categories': category_list, 
					'pages': page_views
					}
	
	visitor_cookie_handler(request)
	
	context_dict['visits'] = request.session['visits']

	#render response and return
	return render(request, 'rango/index.html', context_dict)

def about(request):
	if request.session.test_cookie_worked():
		print("TEST COOKIE WORKED!")
		request.session.delete_test_cookie()
		visitor_cookie_handler(request)
	return render(request, 'rango/about.html', {'visits': request.session['visits']})

def show_category(request, category_name_slug):
	context_dict = {}
	
	#returns a category with the given slug name
	#if it does not exist, raises DoesNotExist exception
	try:
		category = Category.objects.get(slug=category_name_slug)

		#finds all associated pages matching given category
		pages = Page.objects.filter(category=category)
	
		context_dict['pages'] = pages
	
		#adds category object for existence check
		context_dict['category'] = category
		
	except Category.DoesNotExist:
		#if the category can't be found
		#let the template display no category message
		context_dict['category'] = None
		context_dict['pages'] = None
		
	#render response and return
	return render(request, 'rango/category.html', context_dict)
	
@login_required
def add_category(request):
	form = CategoryForm()
	
	if request.method == 'POST':
		form = CategoryForm(request.POST)
		
		if form.is_valid():
			form.save(commit=True)
			return index(request)
		else:
			print(form.errors)
			
	return render(request, 'rango/add_category.html', {'form': form})
	
@login_required	
def add_page(request, category_name_slug):

	try:
		category = Category.objects.get(slug=category_name_slug)
	except Category.DoesNotExist:
		category = None

	form = PageForm()
	
	if request.method == 'POST':
		form = PageForm(request.POST)
		
		if form.is_valid():
			if category:
				page = form.save(commit=False)
				page.category = category
				page.views = 0
				page.save()
				return show_category(request, category_name_slug)
		else:
			print(form.errors)
			
	return render(request, 'rango/add_page.html', {'form': form, 'category': category})
	
def register(request):
	registered=False
	
	if request.method == 'POST':
		user_form = UserForm(data=request.POST)
		profile_form = UserProfileForm(data=request.POST)
		
		if user_form.is_valid() and profile_form.is_valid():
			user = user_form.save()
			user.set_password(user.password)
			user.save()
			
			profile = profile_form.save(commit=False)
			profile.user = user
			if 'picture' in request.FILES:
				profile.picture = request.FILES['picture']
			profile.save()
			
			registered = True
		else:
			print(user_form.errors, profile_form.errors)
	else:
		user_form = UserForm()
		profile_form = UserProfileForm()
		
	return render(request, 'rango/register.html',
					{'user_form': user_form,
					 'profile_form': profile_form,
					 'registered': registered})
					 
def user_login(request):
	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')
		
		user = authenticate(username=username, password=password)
	
		if user:
			if user.is_active:
				login(request, user)
				return HttpResponseRedirect(reverse('index'))
			else:
				return HttpResponse("Your Rango account is disabled")
		else:
			print("Invalid login details: {0}, {1}".format(username, password))
			return HttpResponse("Invalid login details supplied.")
		
	else:
		return render(request, 'rango/login.html', {})
		
@login_required
def user_logout(request):
	logout(request)
	return HttpResponseRedirect(reverse('index'))

@login_required		
def restricted(request):
	return render(request, 'rango/restricted.html', {})
	
def get_server_side_cookie(request, cookie, default_val=None):
	val = request.session.get(cookie)
	if not val:
		val = default_val
	return val
	
#helper function for index
def visitor_cookie_handler(request):
	visits = int(get_server_side_cookie(request, 'visits', '1'))
	
	last_visit_cookie = get_server_side_cookie(request, 
												'last_visit', 
												str(datetime.now()))
	last_visit_time = datetime.strptime(last_visit_cookie[:-7], 
										'%Y-%m-%d %H:%M:%S')
										
	#if it has been more than a day since the last visit, updates
	if(datetime.now() - last_visit_time).days > 0:
		visits += 1
		request.session['last_visit'] = str(datetime.now())
	else:
		visits = 1
		request.session['last_visit'] = last_visit_cookie
	
	request.session['visits'] = visits