import json
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from .forms import AccountRegistrationForm, AccountLoginForm, AccountProfileForm
from .models import Account


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = AccountRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, f'Account created for {user.email}! You can now sign in.')
            return redirect('login')
    else:
        form = AccountRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = AccountLoginForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name or user.email}!')
                next_url = request.GET.get('next') or 'dashboard'
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid email or password.')
        else:
            messages.error(request, 'Invalid email or password.')
    else:
        form = AccountLoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been successfully logged out.')
    return redirect('login')


@login_required(login_url='login')
def profile_view(request):
    if request.method == 'POST':
        form = AccountProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile details updated successfully.')
            return redirect('profile')
    else:
        form = AccountProfileForm(instance=request.user)

    return render(request, 'accounts/profile.html', {'form': form, 'user': request.user})


# --- JSON REST APIs for Accounts & Auth ---

@csrf_exempt
def api_login(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8')) if request.body else request.POST
    except Exception:
        data = request.POST

    email = data.get('email', '').strip()
    password = data.get('password', '').strip()

    if not email or not password:
        return JsonResponse({'error': 'Email and password are required.'}, status=400)

    user = authenticate(request, email=email, password=password)
    if user is not None:
        login(request, user)
        return JsonResponse({
            'success': True,
            'message': f'Logged in as {user.email}',
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role,
            }
        })
    return JsonResponse({'error': 'Invalid credentials.'}, status=401)


@csrf_exempt
def api_register(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8')) if request.body else request.POST
    except Exception:
        data = request.POST

    email = data.get('email', '').strip()
    username = data.get('username', '').strip()
    first_name = data.get('first_name', '').strip()
    last_name = data.get('last_name', '').strip()
    password = data.get('password', '').strip()
    role = data.get('role', Account.Role.STAKEHOLDER)

    if not email or not password or not username:
        return JsonResponse({'error': 'Email, username, and password are required.'}, status=400)

    if Account.objects.filter(email=email).exists():
        return JsonResponse({'error': 'An account with this email already exists.'}, status=400)

    if Account.objects.filter(username=username).exists():
        return JsonResponse({'error': 'An account with this username already exists.'}, status=400)

    user = Account.objects.create_user(
        email=email,
        username=username,
        first_name=first_name,
        last_name=last_name,
        password=password,
        role=role
    )

    return JsonResponse({
        'success': True,
        'message': 'Account registered successfully.',
        'user': {
            'id': user.id,
            'email': user.email,
            'username': user.username,
            'role': user.role,
        }
    }, status=201)


@csrf_exempt
def api_logout(request):
    logout(request)
    return JsonResponse({'success': True, 'message': 'Logged out.'})


def api_profile(request):
    if not request.user.is_authenticated:
        return JsonResponse({'authenticated': False, 'message': 'Anonymous user.'})

    user = request.user
    return JsonResponse({
        'authenticated': True,
        'user': {
            'id': user.id,
            'email': user.email,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user.role,
            'is_staff': user.is_staff,
            'created_date': user.created_date.isoformat(),
        }
    })


def api_users_list(request):
    users = [
        {
            'id': u.id,
            'email': u.email,
            'username': u.username,
            'name': f"{u.first_name} {u.last_name}".strip() or u.username,
            'role': u.role,
            'status': u.account_status,
        }
        for u in Account.objects.all().order_by('role', 'email')
    ]
    return JsonResponse({'users': users, 'count': len(users)})
