from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from participation.models import Participation
from main.models import Currency
from django.contrib import messages
from django.db import transaction
from .models import *
import re


def lang_prefetch(cls, code):
    return Prefetch(
        'translates', to_attr="r_translates",
        queryset=cls.objects.filter(lang__code=code)
    )


@login_required
def show_items(request):
    participantions = Participation.objects\
        .present_with_req(request)\
        .prefetch_related(
            Prefetch("options", to_attr="r_options",
                     queryset=Option.objects.only("option_item__id")
                     .select_related("option"))
        )

    for p in participantions:
        p.pk_options = [o.option_item.pk for o in p.r_options]

    lang_code = request.LANGUAGE_CODE

    groups = OptionGroup.objects\
        .filter(visible=True)\
        .prefetch_related(
            lang_prefetch(OptionGroupTranslate, lang_code),
            Prefetch(
                'options', to_attr="r_options",
                queryset=OptionItem.objects.filter(visible=True)
                .prefetch_related(lang_prefetch(OptionTranslate, lang_code))
            )
        )

    currencies = Currency.objects\
        .prefetch_related(
            Prefetch('option_currencies', to_attr="r_prices",
                     queryset=OptionCurrency.objects
                     .filter(option__visible=True)
                     .only("price", "option_id"))
        ).only("code")

    return render(request, "panel/items/show.html", {
        "participantions": participantions,
        "groups": groups,
        "currencies": currencies
    })

re_item_post = re.compile(r"(\d+)/(\d+)")


def ids_to_object_dicts(ids, queryset):
    objs = queryset.filter(pk__in=ids).all()
    return {str(obj.pk): obj for obj in objs}


@login_required
def update_items(request):

    sid = transaction.savepoint()

    # save currency
    request.user.currency = Currency(pk=request.POST["currency"])
    request.user.save()

    # set to dict - secure for participation/group
    items = {}
    for key, value in request.POST.items():
        match = re_item_post.match(key)
        if match and value != "_":
            items[(match.group(1), match.group(2))] = value

    # security - checking ids
    parts = ids_to_object_dicts(
        ids={item[0] for item in items.keys()},
        queryset=Participation.objects.present_with_req(request)
        .select_related().only("pk")
    )
    options = ids_to_object_dicts(
        ids=items.values(),
        queryset=OptionItem.objects.filter(group__visible=True)
        .only("pk", "group_id")
    )

    # delete old
    Option.objects.filter(
        participation__participant__user=request.user,
        participation__conference=request.conference
    ).delete()

    # create new options
    try:
        for (participation_pk, group_pk), option_pk in items.items():
            #import pdb; pdb.set_trace()
            participation = parts[participation_pk]
            option_item = options[option_pk]

            if str(option_item.group_id) != group_pk:
                raise KeyError("option_item.group__id != group_pk")

            Option.objects.create(
                participation=participation,
                option_item=option_item
            )

    except KeyError:
        transaction.savepoint_rollback(sid)
        messages.error(request, "Hacker ! :(")
        return redirect("item:show")

    transaction.savepoint_commit(sid)
    messages.success(request, "done.")
    return redirect("item:show")
