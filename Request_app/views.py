from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Profile, MaintenanceRequest
from .forms import LoginForm, ResetPasswordForm, UserForm, MaintenanceRequestForm
from django.contrib.auth.decorators import login_required ,user_passes_test
from django.utils.timezone import now, timedelta,datetime
from django.db.models import Q


# Helper to get role
def user_role(user):
    return getattr(user.profile, 'role', None)

# ------------------------ Signup ------------------------
def signup(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            role = request.POST.get('role')
            Profile.objects.create(user=user, role=role)

            login(request, user)

            if role == 'employee':
                return redirect('employee_dashboard')
            elif role == 'technician':
                return redirect('technician_dashboard')

    else:
        form = UserForm()
    return render(request, 'signup.html', {'form': form})

# ------------------------ Login ------------------------
def login_View(request):
    admin_user = User.objects.filter(is_superuser=True).first()
    admin_username = admin_user.username if admin_user else "Not found"
    admin_password = "admin123"

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user:
                login(request, user)
                if user.is_superuser:
                    return redirect('admin_dashboard')
                role = user_role(user)
                if role == 'employee':
                    return redirect('employee_dashboard')
                elif role == 'technician':
                    return redirect('technician_dashboard')
                else:
                    messages.warning(request, "Unknown role.")
                    return redirect('login')
            else:
                messages.error(request, "Invalid credentials")
    else:
        form = LoginForm()
    return render(request, 'login.html', {
        'form': form,
        'admin_username': admin_username,
        'admin_password': admin_password
    })
    
    

# ------------------------ FORGOT PASSWORD ------------------------
def forgot_password(request):
    if request.method == 'POST':
        username = request.POST.get('username').strip()

        if not username:
            messages.error(request, "Please enter your username.")
            return redirect('login')

        try:
            user = User.objects.get(username=username)
            return redirect('reset_password', user_id=user.id)

        except User.DoesNotExist:
            messages.error(request, "User not found.")
            return redirect('login')

    return redirect('login')



# ------------------------ RESET PASSWORD ------------------------
def reset_password(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            user.set_password(new_password)
            user.save()

            # Log out the user to prevent session issues
            logout(request)

            messages.success(request, "Password reset successfully! Please login again.")
            return redirect('login')

    else:
        form = ResetPasswordForm()

    return render(request, 'reset_password.html', {
        'form': form,
        'user_obj': user
    })

# ------------------------ Logout ------------------------
@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

# ------------------------ Dashboards ------------------------
@login_required
def admin_dashboard(request):
    qs = MaintenanceRequest.objects.all()
    return render(request, 'requests/dashboard.html', {
        'active': 'dashboard',
        'total': qs.count(),
        'pending': qs.filter(status='PENDING').count(),
        'in_progress': qs.filter(status='IN_PROCESS').count(),
        'resolved': qs.filter(status='COMPLETED').count(),
        'recent': qs.order_by('-created_at')[:10],
    })



@login_required
def employee_dashboard(request):
    qs = MaintenanceRequest.objects.filter(created_by=request.user)
    return render(request, 'requests/dashboard_employee.html', {
        'total': qs.count(),
        'pending': qs.filter(status='PENDING').count(),
        'resolved': qs.filter(status='COMPLETED').count(),
        'requests': qs.order_by('-created_at'),
    })


@login_required
def technician_dashboard(request):
    qs = MaintenanceRequest.objects.filter(assigned_to=request.user)
    return render(request, 'requests/dashboard_technician.html', {
        'total': qs.count(),
        'in_progress': qs.filter(status='in_progress').count(),
        'resolved': qs.filter(status='resolved').count(),
        'requests': qs.order_by('-created_at'),
    })

# ------------------------ Maintenance Requests ------------------------
@login_required
def create_requests(request):
    if user_role(request.user) != 'employee' and not request.user.is_superuser:
        messages.error(request, "Only employees can create requests.")
        return redirect('employee_dashboard')
    if request.method == 'POST':
        form = MaintenanceRequestForm(request.POST)
        if form.is_valid():
            req = form.save(commit=False)
            req.created_by = request.user
            req.save()
            messages.success(request, f"Request {req.request_id} created successfully!")
            return redirect('my_requests')
    else:
        form = MaintenanceRequestForm()
    return render(request, 'requests/create_request.html', {'form': form})

@login_required
def my_requests(request):
    requests_list = MaintenanceRequest.objects.filter(created_by=request.user).order_by('-created_at')
    return render(request, 'requests/request_detail.html', {'requests': requests_list})

@login_required
def update_request(request, pk):
    req = get_object_or_404(
    MaintenanceRequest,
    pk=pk,
    created_by=request.user,
    status='PENDING'
)
    if request.method == 'POST':
        form = MaintenanceRequestForm(request.POST, instance=req)
        if form.is_valid():
            form.save()
            messages.success(request, "Request updated successfully.")
            return redirect('my_requests')
    else:
        form = MaintenanceRequestForm(instance=req)
    return render(request, 'requests/update_request.html', {'form': form, 'request_obj': req})

@login_required
def delete_request(request, pk):
    req = get_object_or_404(
    MaintenanceRequest,
    pk=pk,
    created_by=request.user,
    status='PENDING'
)
    req.delete()
    messages.success(request, "Request deleted successfully.")
    return redirect('my_requests')

@login_required
def request_history(request):
    completed_requests = MaintenanceRequest.objects.filter(
        created_by=request.user,
        status__in=['resolved']
    ).order_by('-updated_at')
    return render(request, 'requests/request_list.html', {'requests': completed_requests})

# ------------------------ Profile ------------------------
@login_required
def profile(request):
    return render(request, 'requests/profile.html', {'user': request.user})

# Only allow superusers
def admin_required(view_func):
    return user_passes_test(lambda u: u.is_superuser)(view_func)

@login_required
@admin_required
def view_users(request):
    users = User.objects.all().order_by('-date_joined')  # latest users first
    return render(request, 'requests/view_users.html', {
        'active': 'users',
        'users': users
    })
    
@login_required
@admin_required
def manage_requests(request):
    requests = MaintenanceRequest.objects.all().order_by('-created_at')
    technicians = User.objects.filter(profile__role='technician')

    if request.method == "POST":
        req_id = request.POST.get("req_id")
        tech_id = request.POST.get("technician")
        status = request.POST.get("status")

        req = MaintenanceRequest.objects.get(id=req_id)

        if tech_id:
            req.assigned_to_id = tech_id
        
        if status:
            req.status = status

        req.save()
        messages.success(request, "Request updated successfully.")
        return redirect("manage_requests")

    return render(request, "requests/manage_requests.html", {
        "requests": requests,
        "technicians": technicians,
        "active": "requests",
    })
    
    

@login_required
@admin_required
def reports(request):
    requests = MaintenanceRequest.objects.filter(status="Resolved").order_by('-updated_at')

    category = request.GET.get("category")
    filter_type = request.GET.get("filter")
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    # CATEGORY FILTER
    if category and category != "all":
        requests = requests.filter(category=category)

    # DATE FILTER OPTIONS
    today = datetime.today().date()

    if filter_type == "daily":
        requests = requests.filter(updated_at__date=today)

    elif filter_type == "weekly":
        last_week = today - timedelta(days=7)
        requests = requests.filter(updated_at__date__gte=last_week)

    elif filter_type == "monthly":
        requests = requests.filter(updated_at__month=today.month, updated_at__year=today.year)

    elif filter_type == "yearly":
        requests = requests.filter(updated_at__year=today.year)

    elif filter_type == "custom" and start_date and end_date:
        requests = requests.filter(updated_at__date__range=[start_date, end_date])

    context = {
        "requests": requests,
        "active": "reports",
    }

    return render(request, "requests/reports.html", context)

@login_required
def assigned_tasks(request):
    technician = request.user
    tasks = MaintenanceRequest.objects.filter(
        assigned_to=technician,
        status__in=["Pending", "In Progress"]
    )

    return render(request, "technician/assigned_tasks.html", {"tasks": tasks})

@login_required
def update_progress(request, pk):
    task = MaintenanceRequest.objects.get(id=pk)

    if request.method == "POST":
        new_status = request.POST.get("status")
        task.status = new_status
        task.save()
        return redirect("assigned_tasks")

    return render(request, "technician/update_progress.html", {"task": task})

@login_required
def completed_tasks(request):
    technician = request.user
    tasks = MaintenanceRequest.objects.filter(
        assigned_to=technician,
        status="Resolved"
    )

    return render(request, "technician/completed_tasks.html", {"tasks": tasks})

