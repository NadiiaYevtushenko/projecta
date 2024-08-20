from django.http import JsonResponse
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page


class RedirectToDashboardMixin:
    """Перенаправлення користувача на інформаційну панель, якщо він пройшов автентифікацію"""
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)


class StaffRequiredMixin:
    """Доступ лише персоналу."""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class SuperuserRequiredMixin:
    """лише суперкористувачам"""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class CachePageMixin:
    """Кешування в певний час"""
    cache_timeout = 60 * 15  # 15 minutes

    @method_decorator(cache_page(cache_timeout))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class FormValidMixin:
    """Переадрусування на URL  адресу якщо форма дійсна"""
    def form_valid(self, form):
        response = super().form_valid(form)
        # додаткові умови
        return response


class SuccessMessageMixin:
    """повідомлення при успішному надсиланні форми"""
    success_message = "Done"

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.success_message:
            messages.success(self.request, self.success_message)
        return response


class UserIsOwnerMixin:
    """власник певного об'єкта має доступ до дій, що виконується у відповідному класі-view (наприклад, перегляд деталей або редагування)"""
    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.owner != self.request.user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class JSONResponseMixin:
    """відповідь JSON"""
    def render_to_json_response(self, context, **response_kwargs):
        return JsonResponse(self.get_data(context), **response_kwargs)

    def get_data(self, context):
        return context


class AjaxOnlyMixin:
    """лише через запити AJAX"""
    def dispatch(self, request, *args, **kwargs):
        if not request.is_ajax():
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class PaginationMixin:
    """кількість продуктів/обєктів  на сторінці """
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_paginated'] = self.get_queryset().count() > self.paginate_by
        return context
