from django.contrib import messages
from django.views.generic.base import View
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.http.response import HttpResponseForbidden


class BaseView(View):

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def generate_successful_msg(self, request, obj, *args, **kwargs):
        """Generate msg when object had successful action and return string"""
        return ""

    def get_obj(self, request, pk, *args, **kwargs):
        raise ObjectDoesNotExist

    def get_obj_or_403(self, request, pk, *args, **kwargs):
        try:
            return self.get_obj(request, pk, *args, **kwargs)
        except ObjectDoesNotExist:
            raise HttpResponseForbidden
        except MultipleObjectsReturned:
            raise HttpResponseForbidden


class AbstractEditView(BaseView):

    """Abstract View to create edit views very fast
    Args:
        form_class (class): class to form.
        model_class (class): class to model class. Beware - manager must have
        can_edit_with_req(request) method.
        template_name (string): path to template.
        redirect_url (string): url to redirect when object is saved.
        initial (dict): initial vars to form
    """

    initial = {}

    def get_form(self, request, obj, data, *args, **kwargs):
        return self.form_class(data, instance=obj, initial=self.initial)

    def get_obj(self, request, pk, *args, **kwargs):
        """Return object to edit or return None"""
        return self.model_class.objects.can_edit_with_req(request)\
            .get(pk=pk) if pk else None

    def save(self, request, form, *args, **kwargs):
        """Create or update edited object"""
        form.save()

    def get(self, request, pk=None, *args, **kwargs):
        obj = self.get_obj_or_403(request, pk, *args, **kwargs)

        return render(request, self.template_name, {
            'form': self.get_form(request, obj, data=None)
        })

    def is_valid(self, request, form, *args, **kwargs):
        return form.is_valid()

    def post(self, request, pk=None, *args, **kwargs):

        obj = self.get_obj_or_403(request, pk, *args, **kwargs)
        form = self.get_form(request, obj, data=request.POST)

        if self.is_valid(request, form, args, kwargs):
            msg = self.generate_successful_msg(request, form.instance,
                                               *args, **kwargs)
            self.save(request, form, *args, **kwargs)
            if msg:
                messages.success(request, msg)

            return redirect(self.redirect_url)
        else:
            return render(request, self.template_name, {
                'form': form
            })


class AbstractDeleteView(BaseView):

    """Similiar to AbstractEditView but this class is to delete instances
    Args:
        model_class (class): class to model class. Beware - manager must have
        can_delete_with_req(request) method.
        template_name (string): path to template.
        redirect_url (string): url to redirect when object is saved.
    """

    def get_obj(self, request, pk, *args, **kwargs):
        """Return object to edit or return None"""
        return self.model_class.objects.can_delete_with_req(request)\
            .get(pk=pk)

    def delete(self, request, obj, *args, **kwargs):
        """Method do delete obj"""
        obj.delete()

    def get(self, request, pk, *args, **kwargs):
        obj = self.get_obj_or_403(request, pk, *args, **kwargs)

        return render(request, self.template_name,
                      {"obj": obj, "pk": pk})

    def post(self, request, pk, *args, **kwargs):
        obj = self.get_obj_or_403(request, pk, *args, **kwargs)
        msg = self.generate_successful_msg(request, obj, *args, **kwargs)
        self.delete(request, obj)
        if msg:
            messages.success(request, msg)

        return redirect(self.redirect_url)
