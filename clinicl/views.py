from django.views.generic import TemplateView
from clinicApp.models import Slide
class HomeView(TemplateView):
    slides = Slide.objects.all()
    template_name = 'html/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['slides'] = Slide.objects.all()
        context['user'] = user
        return context


