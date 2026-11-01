from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.models import Group
from django.contrib.auth.views import LoginView, LogoutView
from django.db import transaction
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import IngresoForm, RegistroForm
from .roles import GRUPO_CLIENTES


class RegistroView(CreateView):
    form_class = RegistroForm
    template_name = 'usuarios/registro.html'
    success_url = reverse_lazy('inicio')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('inicio')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        with transaction.atomic():
            self.object = form.save()
            grupo, _ = Group.objects.get_or_create(name=GRUPO_CLIENTES)
            self.object.groups.add(grupo)
        login(self.request, self.object)
        messages.success(self.request, 'Tu cuenta está lista. ¡Bienvenido!')
        return redirect(self.success_url)


class IngresoView(LoginView):
    template_name = 'usuarios/login.html'
    authentication_form = IngresoForm
    redirect_authenticated_user = True


class SalidaView(LogoutView):
    # Django solo admite POST y exige CSRF para cerrar la sesión.
    next_page = reverse_lazy('inicio')
