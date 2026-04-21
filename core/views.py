from django.shortcuts import render


def home(request):
    """
    Homepage view — the main entry point of the application.
    Renders the landing page with the project title.
    """
    return render(request, 'home.html')

