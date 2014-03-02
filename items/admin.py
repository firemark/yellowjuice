from django.contrib import admin
from .models import (OptionItem, OptionGroup,
                     OptionCurrency, OptionTranslate, OptionGroupTranslate)


class OptionTranslateInline(admin.TabularInline):
    model = OptionTranslate
    extra = 1


class OptionCurrencyInline(admin.TabularInline):
    model = OptionCurrency
    extra = 1


class OptionGroupTranslateInline(admin.TabularInline):
    model = OptionGroupTranslate
    extra = 1


class OptionItemAdmin(admin.ModelAdmin):
    inlines = (OptionTranslateInline, OptionCurrencyInline)

    list_display = ('key', 'group')
    list_display_links = ('key',)


class OptionGroupAdmin(admin.ModelAdmin):
    inlines = (OptionGroupTranslateInline,)

    list_display = ('key',)
    list_display_links = ('key',)

admin.site.register(OptionItem, OptionItemAdmin)
admin.site.register(OptionGroup, OptionGroupAdmin)
