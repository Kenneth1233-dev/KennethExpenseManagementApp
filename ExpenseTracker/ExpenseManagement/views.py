from django.shortcuts import render, HttpResponse, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, logout
from django.contrib.auth import login as dj_login
from django.contrib.auth.models import User
from .models import Topup_info, UserProfile
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
        topup_info = Topup_info.objects.filter(user=user).order_by('Date')
        paginator = Paginator(topup_info, 4)
        page_umber = request.GET.get('page')
        page_obj = Paginator.get_page(paginator, page_umber)
        context = {
                    #'add_info':
                    topup_info, 'page_obj', page_obj
        }
        # if request.session.has_key('is_logged'):
        return render(request, 'home/index.html', context)
    return redirect('home')


def topup(request):
    return render(request, 'home/topup.html')


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
            return redirect('/index')
        else:
            messages.error(request, 'Invalid Credentials, Please try again')
            return redirect('/')
        return HttpResponse('404 - NOT FOUND')


def handleLogout(request):
    del request.session['is_logged']
    del request.session['user_id']
    logout(request)
    messages.success(request, 'Successfully logged out')
    return redirect('home')


def topup_submission(request):
    if request.session.has_key('is_logged'):
        if request.method == 'POST':
            user_id = request.session['user_id']
            user1 = User.objects.get(id=user_id)
            topup_info1 = Topup_info.objects.filter(user=user1).order_by('-Date')
            top_up = request.POST['top_up']
            quantity = request.POST['quantity']
            Date = request.POST['Date']
            Category = request.POST['Category']
            add = Topup_info(user=user1, top_up=top_up, quantity=quantity, Date=Date, Category=Category)

            add.save()
            paginator = Paginator(topup_info1, 4)
            page_number = request.GET.get('page')
            page_obj = Paginator.get_page(paginator, page_number)

            context = {
                'page_obj': page_obj
            }
            return render(request, 'home/index.html', context)
        return redirect('/index')


def topup_update(request, id):
    if request.session.has_key('is_logged'):
        if request.method == 'POST':
            add = Topup_info.objects.get(id=id)
            add.top_up = request.POST['top_up']
            add.quantity = request.POST['quantity']
            add.date = request.POST['Date']
            add.Category = request.POST['Category']
            add.save()
            return redirect('/index')
        return redirect('/home')


def expense_edit(request, id):
    if request.session.has_key('is_logged'):
        topup_info = Topup_info.objects.get(id=id)
        user_id = request.session('user_id')
        user1 = User.objects.get(id=user_id)
        return render(request, 'home/expense_edit.html', { 'topup_info':topup_info })
    return redirect('/home')


def expense_delete(request, id):
    if request.session.has_key('is_logged'):
        topup_info = Topup_info.session.objects.get(id=id)
        topup_info.delete()
        return redirect('/index')
    return redirect('/home')


def expense_month(request):
    today_date = datetime.date.today()
    one_month_ago = todays_date-datetime.timedelta(days=30)
    user_id = request.session['user_id']
    user1 = User.objects.get(id=user_id)
    topup = Topup_info.objects.filter(user=user1, Date_gte=one_month_ago, Date_lte=todays_date)
    finalrep ={}


def get_Category(topup_info):
    # if topup_info.top_up=='Expense':
    return topup_info.Category


Category_list = list(set(map(get_Category, topup)))


def get_expense_category_amount(Category, top_up):
    quantity = 0
    filtered_by_category = topup.filter(Category=Category, top_up='Expense')
    for i in filtered_by_category:
        quantity += i.quantity
    return qantity
    for x in topup:
        for y in Category_list:
            finalrep[y] = get_expense_category_amount(y, 'Expense')
    return JsonResponse({'expense_category_data': finalrep}, safe=False)


def stats(request):
    if request.session.has_key('is_logged'):
        todays_date = datetime.date.today()
        one_month_ago = todays_date-datetime.timedelta(days=30)
        user_id = request.session['user_id']
        user1 = User.objects.get(id=user_id)
        topup_info = Topup_info.objects.filter(user=user1, Date_get=one_month_ago, Date_lte=todays_date)
        sum = 0

        for i in topup_info:
            if i.top_up == 'Expense':
                sum += i.quantity

        topup_info.sum = sum
        sum1 = 0
        for i in topup_info:
            if i.top_up == 'Income':
                sum1 += i.quantity
        topup_info.sum1 = sum1

        x = user1.userprofile.Savings + topup_info.sum1 - topup_info.sum
        y = user1.userprofile.Savings + topup_info.sum1 - topup_info.sum

        if x<0:
            messages.warning(request, 'Your Expenses has Exceeded your saving!')
            x = 0
        if x>0:
             y = 0
        topup_info.x = abs(x)
        topup_info.y = abs(y)

        return render(request, 'home/stats.html', {'topup':topup_info})


def expense_week(request):
    todays_date = datetime.date.today()
    one_week_ago = todays_date-datetime.timedelta(days=7)
    user_id = request.session['user_id']
    user1 = User.objects.get(id=user_id)
    topup = Topup_info.objects.filter(user=user1, Date_gte=one_week_ago, Date_lte=todays_date)
    finalrep = {}


def get_Category(topup_info):
    return topup_info.Category


Category_list = list(set(map(get_Category, topup)))


def get_expense_category_amount(Category, top_up):
    quantity = 0
    filtered_by_category = topup.filter(Category=Category, top_up='Expense')

    for i in filtered_by_category:
        quantity += i.quantity
        return quantity
    for x in topup:
        for y in Category_list:
            finalrep[y] = get_expense_category_amount(y, 'Expense')
    return JsonResponse({'expense_category_data': finalrep}, safe=False)


def weekly(request):
    if request.session.has_key('is_logged'):
        todays_date = datetime.date.today()
        one_week_ago = todays_date-datetime.timedelta(days=7)
        user_id = request.session['user_id']
        user1 = User.objects.get(id=user_id)
        topup_info = Topup_info.objects.filter(user=user1, Date_gte=one_week_ago, date_lte=todays_date)

        sum = 0

        for i in topup_info:
            if i.top_up == 'Expense':
                sum += i.quantity

        topup_info.sum = sum
        sum1 = 0

        for i in topup_info:
            if i.top_up == 'Income':
                sum1 += i.quantity

        topup_info.sum1 = sum1

        x = user1.userprofile.Savings + topup_info.sum1 - topup_info.sum
        y = user1.userprofile.Savings + topup_info.sum1 - topup_info.sum

        if x < 0:
            messages.warning(request, 'Your Expenses Exceeded your Savings')

        x = 0
        if x > 0:
            y = 0
            topup_info.x = abs(x)
            topup_info.y = abs(y)
        return render(request, 'home/weekly.html', {'topup_info': topup_info})


def check(request):
    if request.method == 'POST':
        user_exists = User.objects.filter(email=request.POST['email'])
        messages.error(request, 'Email not registered, TRY AGAIN!!!')
        return redirect('/reset_password')


def info_year(request):
    todays_date = datetime.date.today()
    one_week_ago = todays_date-datetime.timedelta(days=30*12)
    user_id = request.session['user_id']

    user1 = User.objects.get(id=user_id)
    topup = Topup_info.objects.filter(user=user1, Date_gte=one_week_ago, Date_lte=todays_date)
    finalrep = {}


def get_Category(topup_info):
    return topup_info.Category

Category_list = list(set(map(get_Category, topup)))


def get_expense_category_amount(Category, top_up):
    quantity = 0
    filtered_by_category = topup.filter(Category=Category, top_up='Expense')
    for i in filtered_by_category:
        quantity += i.quantity
    return quantity

    for x in topup:
        for y in Category_list:
            finalrep[y]= get_expense_category_amount(y, 'Expense')
    return JsonResponse({'expense_category_data': finalrep}, safe=False)

def info(request):
    return render(request, 'home/info.html')