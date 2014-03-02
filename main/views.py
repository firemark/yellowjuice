from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from misc.mail import send_email
from .forms import SignupForm
from .models import UserConfirm
from time import time
import hashlib


User = get_user_model()


def signup(request):

    if request.user.is_authenticated():
        return HttpResponseForbidden()

    form = SignupForm(request.POST)

    if form.is_valid():
        data = form.cleaned_data
        email = data['email']
        user = User.objects.create_user(email=email,
                                        password=data['password'])

        #user.is_active = True
        user.save()

        # create hash
        m = hashlib.md5()
        m.update(str(time()).encode())
        m.update(email.encode())
        m.update(data['password'].encode())

        hash_key = m.hexdigest()
        UserConfirm.objects.create(user=user, key=hash_key)

        # send email
        send_email(
            'Register',
            'email/register.txt',
            {
            "hash": hash_key,
            "email": email,
            "full_path": request.build_absolute_uri("/confirm/2")
            },
            (email,)
        )

        return redirect('signup-done')

    return render(request, "signup.html", {"form": form})


def confirm(request, hash_key):

    userconfirm = get_object_or_404(UserConfirm, key=hash_key)
    userconfirm.user.is_active = True
    userconfirm.user.save()
    userconfirm.delete()

    return render(request, "confirm.html")
