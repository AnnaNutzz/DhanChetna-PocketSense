"""
PocketSense — Web Views (Server-Side Rendered)
All views that power the Django web frontend.
Uses session auth (not Firebase) for web users.
"""

import csv
import json
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.core.paginator import Paginator

from apps.accounts.models import User, UserProfile
from apps.transactions.models import Category, Transaction, IncomeSource
from apps.budgets.models import Budget, SavingsGoal


# ─────────────────────────── Auth ───────────────────────────

def login_view(request):
    if request.user.is_authenticated:
        return redirect('web:dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            return redirect('web:dashboard')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'web/login.html')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('web:dashboard')

    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
        elif len(password1) < 8:
            messages.error(request, 'Password must be at least 8 characters.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
        else:
            user = User.objects.create_user(
                username=username, email=email, password=password1,
                first_name=first_name,
            )
            UserProfile.objects.create(user=user)
            login(request, user)
            messages.success(request, f'Welcome to PocketSense, {first_name}! 🎉')
            return redirect('web:dashboard')

    return render(request, 'web/register.html')


def logout_view(request):
    logout(request)
    messages.success(request, 'Logged out. See you later!')
    return redirect('web:login')


# ─────────────────────────── Dashboard ───────────────────────────

def _get_time_of_day():
    hour = timezone.now().hour
    if hour < 12:
        return 'morning'
    elif hour < 17:
        return 'afternoon'
    else:
        return 'evening'


def _get_budget_status(user):
    """Calculate spending vs budget for all active budgets."""
    now = timezone.now()
    budgets = Budget.objects.filter(user=user, is_active=True).select_related('category')

    results = []
    for budget in budgets:
        if budget.period == 'monthly':
            start_date = now.date().replace(day=1)
        else:
            start_date = (now - timedelta(days=now.weekday())).date()

        txn_filter = {
            'user': user, 'type': 'expense', 'is_deleted': False,
            'transaction_date__gte': start_date,
        }
        if budget.category:
            txn_filter['category'] = budget.category

        spent = Transaction.objects.filter(**txn_filter).aggregate(
            total=Sum('amount'))['total'] or Decimal('0')

        limit = budget.limit_amount
        percentage = min(100, round(float(spent) / float(limit) * 100)) if limit else 0

        results.append({
            'category': budget.category.name if budget.category else 'Overall',
            'spent': float(spent),
            'limit': float(limit),
            'remaining': float(limit - spent),
            'percentage': percentage,
            'status': 'over' if percentage >= 100 else 'warning' if percentage >= 80 else 'ok',
        })
    return results


@login_required(login_url='/login/')
def dashboard_view(request):
    user = request.user
    today = timezone.now().date()
    month_start = today.replace(day=1)
    base_qs = Transaction.objects.filter(user=user, is_deleted=False)

    today_spent = base_qs.filter(type='expense', transaction_date=today).aggregate(
        total=Sum('amount'))['total'] or 0
    today_count = base_qs.filter(type='expense', transaction_date=today).count()

    month_expenses = base_qs.filter(type='expense', transaction_date__gte=month_start).aggregate(
        total=Sum('amount'))['total'] or 0
    month_income = base_qs.filter(type='income', transaction_date__gte=month_start).aggregate(
        total=Sum('amount'))['total'] or 0

    total_income = base_qs.filter(type='income').aggregate(total=Sum('amount'))['total'] or 0
    total_expenses = base_qs.filter(type='expense').aggregate(total=Sum('amount'))['total'] or 0
    wallet_balance = total_income - total_expenses

    recent = base_qs.select_related('category').order_by('-transaction_date', '-created_at')[:5]
    savings_jar = SavingsGoal.objects.filter(user=user, status='active').first()

    return render(request, 'web/dashboard.html', {
        'active_page': 'dashboard',
        'time_of_day': _get_time_of_day(),
        'today_spent': today_spent,
        'today_count': today_count,
        'month_expenses': month_expenses,
        'month_income': month_income,
        'month_net': month_income - month_expenses,
        'wallet_balance': wallet_balance,
        'recent_transactions': recent,
        'budget_status': _get_budget_status(user),
        'savings_jar': savings_jar,
    })


# ─────────────────────────── Transactions ───────────────────────────

@login_required(login_url='/login/')
def transactions_view(request):
    user = request.user
    qs = Transaction.objects.filter(user=user, is_deleted=False).select_related('category')

    # Filters
    filter_type = request.GET.get('type', '')
    filter_category = request.GET.get('category', '')
    filter_month = request.GET.get('month', '')

    if filter_type:
        qs = qs.filter(type=filter_type)
    if filter_category:
        qs = qs.filter(category_id=filter_category)
    if filter_month:
        try:
            year, month = filter_month.split('-')
            qs = qs.filter(transaction_date__year=int(year), transaction_date__month=int(month))
        except (ValueError, TypeError):
            pass

    qs = qs.order_by('-transaction_date', '-created_at')
    paginator = Paginator(qs, 25)
    page = paginator.get_page(request.GET.get('page', 1))

    categories = Category.objects.filter(Q(user=user) | Q(user__isnull=True))

    return render(request, 'web/transactions.html', {
        'active_page': 'transactions',
        'transactions': page,
        'categories': categories,
        'filter_type': filter_type,
        'filter_category': filter_category,
        'filter_month': filter_month,
    })


@login_required(login_url='/login/')
def add_expense_view(request):
    return _add_transaction(request, 'expense')


@login_required(login_url='/login/')
def add_income_view(request):
    return _add_transaction(request, 'income')


def _add_transaction(request, txn_type):
    user = request.user
    categories = Category.objects.filter(Q(user=user) | Q(user__isnull=True))

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        amount_str = request.POST.get('amount', '')
        category_id = request.POST.get('category', '')
        txn_date = request.POST.get('transaction_date', str(date.today()))
        description = request.POST.get('description', '').strip()

        try:
            amount = Decimal(amount_str)
            if amount <= 0:
                raise ValueError
        except (InvalidOperation, ValueError):
            messages.error(request, 'Please enter a valid positive amount.')
            return render(request, 'web/add_transaction.html', {
                'active_page': f'add_{txn_type}',
                'txn_type': txn_type,
                'categories': categories,
                'today': str(date.today()),
            })

        category = None
        if category_id:
            try:
                category = Category.objects.get(id=category_id)
            except Category.DoesNotExist:
                pass

        Transaction.objects.create(
            user=user,
            type=txn_type,
            title=title,
            amount=amount,
            category=category,
            transaction_date=txn_date,
            description=description,
        )

        emoji = '💸' if txn_type == 'expense' else '💰'
        messages.success(request, f'{emoji} {txn_type.title()} of ₹{amount} recorded!')

        # Budget warning check
        if txn_type == 'expense':
            for b in _get_budget_status(user):
                if b['status'] == 'over':
                    messages.warning(request, f'⚠️ You\'ve exceeded your {b["category"]} budget!')
                elif b['status'] == 'warning':
                    messages.warning(request, f'⚡ {b["category"]} budget is at {b["percentage"]}%!')

        return redirect('web:transactions')

    return render(request, 'web/add_transaction.html', {
        'active_page': f'add_{txn_type}',
        'txn_type': txn_type,
        'categories': categories,
        'today': str(date.today()),
    })


@login_required(login_url='/login/')
def delete_transaction_view(request, pk):
    if request.method == 'POST':
        txn = get_object_or_404(Transaction, id=pk, user=request.user)
        txn.is_deleted = True
        txn.save(update_fields=['is_deleted'])
        messages.success(request, 'Transaction deleted.')
    return redirect('web:transactions')


# ─────────────────────────── Wallet ───────────────────────────

@login_required(login_url='/login/')
def wallet_view(request):
    user = request.user
    base_qs = Transaction.objects.filter(user=user, is_deleted=False)

    total_income = base_qs.filter(type='income').aggregate(total=Sum('amount'))['total'] or 0
    total_expenses = base_qs.filter(type='expense').aggregate(total=Sum('amount'))['total'] or 0
    wallet_balance = total_income - total_expenses

    income_sources = IncomeSource.objects.filter(user=user, is_active=True)

    return render(request, 'web/wallet.html', {
        'active_page': 'wallet',
        'wallet_balance': wallet_balance,
        'total_income': total_income,
        'total_expenses': total_expenses,
        'income_sources': income_sources,
    })


# ─────────────────────────── Savings ───────────────────────────

@login_required(login_url='/login/')
def savings_view(request):
    goals = SavingsGoal.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'web/savings.html', {
        'active_page': 'savings',
        'goals': goals,
    })


@login_required(login_url='/login/')
def savings_create_view(request):
    if request.method == 'POST':
        name = request.POST.get('name', 'My Savings').strip()
        target = request.POST.get('target_amount', '0')
        target_date = request.POST.get('target_date', '') or None

        try:
            target_amount = Decimal(target)
            if target_amount <= 0:
                raise ValueError
        except (InvalidOperation, ValueError):
            messages.error(request, 'Please enter a valid target amount.')
            return redirect('web:savings')

        SavingsGoal.objects.create(
            user=request.user,
            name=name,
            target_amount=target_amount,
            target_date=target_date,
        )
        messages.success(request, f'🏺 Savings goal "{name}" created!')

    return redirect('web:savings')


@login_required(login_url='/login/')
def savings_deposit_view(request, pk):
    if request.method == 'POST':
        goal = get_object_or_404(SavingsGoal, id=pk, user=request.user, status='active')
        amount_str = request.POST.get('amount', '0')

        try:
            amount = Decimal(amount_str)
            if amount <= 0:
                raise ValueError
        except (InvalidOperation, ValueError):
            messages.error(request, 'Please enter a valid amount.')
            return redirect('web:savings')

        goal.current_amount += amount
        if goal.current_amount >= goal.target_amount:
            goal.status = 'completed'
            messages.success(request, f'🎉 Goal "{goal.name}" completed! Amazing!')
        else:
            messages.success(request, f'💰 ₹{amount} deposited into "{goal.name}"!')
        goal.save()

    return redirect('web:savings')


# ─────────────────────────── Budgets ───────────────────────────

@login_required(login_url='/login/')
def budgets_view(request):
    categories = Category.objects.filter(
        Q(user=request.user) | Q(user__isnull=True)
    )

    return render(request, 'web/budgets.html', {
        'active_page': 'budgets',
        'budget_status': _get_budget_status(request.user),
        'categories': categories,
    })


@login_required(login_url='/login/')
def budget_create_view(request):
    if request.method == 'POST':
        category_id = request.POST.get('category', '')
        limit = request.POST.get('limit_amount', '0')
        period = request.POST.get('period', 'monthly')

        try:
            limit_amount = Decimal(limit)
            if limit_amount <= 0:
                raise ValueError
        except (InvalidOperation, ValueError):
            messages.error(request, 'Please enter a valid limit amount.')
            return redirect('web:budgets')

        category = None
        if category_id:
            try:
                category = Category.objects.get(id=category_id)
            except Category.DoesNotExist:
                pass

        Budget.objects.create(
            user=request.user,
            category=category,
            limit_amount=limit_amount,
            period=period,
        )
        name = category.name if category else 'Overall'
        messages.success(request, f'🎯 {name} budget of ₹{limit_amount} created!')

    return redirect('web:budgets')


# ─────────────────────────── Analytics ───────────────────────────

@login_required(login_url='/login/')
def analytics_view(request):
    user = request.user
    now = timezone.now()
    month_start = now.date().replace(day=1)
    week_start = (now - timedelta(days=6)).date()

    base_qs = Transaction.objects.filter(user=user, is_deleted=False)

    month_expenses = base_qs.filter(type='expense', transaction_date__gte=month_start).aggregate(
        total=Sum('amount'))['total'] or 0
    month_income = base_qs.filter(type='income', transaction_date__gte=month_start).aggregate(
        total=Sum('amount'))['total'] or 0

    # Category split
    cat_data = base_qs.filter(
        type='expense', transaction_date__gte=month_start
    ).values(
        'category__name', 'category__color_hex'
    ).annotate(total=Sum('amount')).order_by('-total')

    category_data = [
        {
            'category': item['category__name'] or 'Uncategorized',
            'color': item['category__color_hex'] or '#6C5CE7',
            'total': float(item['total']),
        }
        for item in cat_data
    ]

    # Weekly trend
    daily = base_qs.filter(
        type='expense', transaction_date__gte=week_start
    ).values('transaction_date').annotate(
        total=Sum('amount')
    ).order_by('transaction_date')

    weekly_data = [
        {'date': str(d['transaction_date']), 'total': float(d['total'])}
        for d in daily
    ]

    return render(request, 'web/analytics.html', {
        'active_page': 'analytics',
        'month_expenses': month_expenses,
        'month_income': month_income,
        'month_net': month_income - month_expenses,
        'category_data': json.dumps(category_data),
        'weekly_data': json.dumps(weekly_data),
    })


# ─────────────────────────── Settings ───────────────────────────

@login_required(login_url='/login/')
def settings_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST' and request.POST.get('form_type') == 'profile':
        request.user.first_name = request.POST.get('first_name', '').strip()
        request.user.save(update_fields=['first_name'])

        profile.age_group = request.POST.get('age_group', 'student')
        profile.income_type = request.POST.get('income_type', 'pocket_money')
        profile.living_situation = request.POST.get('living_situation', 'hostel')
        profile.food_provided = 'food_provided' in request.POST
        profile.save()

        messages.success(request, 'Settings saved! ✅')
        return redirect('web:settings')

    return render(request, 'web/settings.html', {
        'active_page': 'settings',
        'profile': profile,
    })


# ─────────────────────────── CSV Export ───────────────────────────

@login_required(login_url='/login/')
def export_csv_view(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="pocketsense_transactions_{date.today()}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Date', 'Type', 'Title', 'Category', 'Amount', 'Description'])

    transactions = Transaction.objects.filter(
        user=request.user, is_deleted=False
    ).select_related('category').order_by('-transaction_date')

    for txn in transactions:
        writer.writerow([
            txn.transaction_date,
            txn.type,
            txn.title,
            txn.category.name if txn.category else '',
            txn.amount,
            txn.description,
        ])

    return response
