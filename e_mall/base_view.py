from django.shortcuts import render


def error_404(request):
    """404错误页"""
    return render(request, '404.html')


