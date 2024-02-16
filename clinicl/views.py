from django.shortcuts import render


def home(request):
    return render(request, 'html/index.html')


from django.contrib.auth.views import LoginView


class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
