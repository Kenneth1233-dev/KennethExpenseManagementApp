from django.shortcuts import render, HttpResponse, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, logout
from django.contrib.auth import login as dj_login
from django.contrib.auth.models import User
from .models import Addmoney_info, UserProfile
from django.contrib.sessions.models import Session
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Sum
from django.http import JsonResponse
import datetime
from django.utils import timezone

# Create your views here.


def home(request):
    if request.session.has_key('is_logged'):
        return redirect('/index')
    return render(request, 'home/login.html')
    # return HttpResponse('This is home')


def index(request):
    if request.session.has_key('is_logged'):
        user_id = request.session["user_id"]
        user = User.objects.get(id=user_id)
        addmoney_info = Addmoney_info.objects.filter(user=user).order_by('Date')
        paginator = Paginator(addmoney_info, 4)
        page_umber = request.GET.get('page')
        page_obj = Paginator.get_page(paginator, page_umber)
        context = {
                    #'add_info':
                    addmoney_info, 'page_obj', page_obj
        }
        # if request.session.has_key('is_logged'):
        return render(request, 'home/index.html', context)
    return redirect('home')


def addmoney(request):
    return render(request, 'home/addmoney.html')


def profile(request):
    if request.session.has_key('is_loged'):
        return render(request, 'home/profile.html')
    return redirect('/home')


def profile_edit(request, id):
    if request.session.has_key('is_logged'):
        add = User.objects.get(id=id)
        return render(request, 'home/profile_edit.html', {'add':add})
    return redirect("/home")


def profile_update(request, id):
    if request.session.has_key('is_logged'):
        if request.method == "POST":
            user = User.objects.get(id=id)
            user.first_name = request.POST['fname']
            user.first_name = request.POST['lname']
            user.email = request.POST['email']
            user.userprofile.savings = request.POST['savings']
            user.userprofile.income = request.POST['income']
            user.userprofile.profession = request.POST['profession']
            user.userprofile.save()
            user.save()
            return redirect('/profile')
        return redirect('/home')


def handleSignup(request):
    if request.method == 'POST':
        # get the post parameter
        uname = request.POST['uname']
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        profession = request.POST['profession']
        Savings = request.POST['Savings']
        income = request.POST['income']

        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']
        profile = UserProfile(Savings=Savings, profession=profession, income=income)

        # checking for errors in input
        if request.mrhtod == 'POST':
            try:
                user_exists = User.objects.get(username=request.POST['uname'])
                messages.error(request, 'Username already taken, Please try a different username!!!')
                return redirect('/register')
            except User.DoesNotExist:

                if len(uname) > 15:
                    messages.error(request, 'Username too long must be maximum 15 characters, Please try again')
                    return redirect('/register')

                if not uname.isalname():
                    messages.error(request, 'Username should only contain letters and numbers, Please try again')
                    return redirect('/register')

                if pass1 != pass2:
                    messages.error(request, 'Password do not match, Please try again')

            # create the user
            user = User.objects.create_user(uname, email, pass1)
            user.first_name = fname
            user.last_name = lname
            user.email = email

            # profile = Userprofile.objects.all()
            user.save()

            # p1=profile.save(commit=False)
            profile.user = user
            profile.save()
            messages.success(request, 'Your account has been successfully created')
            return redirect('/')
        else:
            return HttpResponse('404 - NOT FOUND')
        return redirect('/login')


def handlelogin(request):
    if request.method == 'POST':

        # get the post parameter
        loginuname = request.POST['loginuname']
        loginpassword1=request.POST['loginpassword1']
        user = authenticate(username=loginuname, password=loginpassword1)

        if user is not None:
            dj_login(request, user)
            request.session['is_logged'] = True
            user = request.user.id
            request.session['user_id'] = user
            messages.seccess(request, 'Successfully logged in')
            return  redirect('/index')
        else:
            messages.error(request, 'Invalid Credentials, Please try again')
