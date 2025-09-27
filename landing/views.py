from django.shortcuts import render, redirect

def home(request):
    # If user is already authenticated, redirect to dashboard
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    return render(request, 'landing/home.html')
