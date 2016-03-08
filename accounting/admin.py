from django.contrib import admin

from accounting import forms
from .models import *


class PurchaseItemsInline(admin.TabularInline):
    model = PurchaseItem


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    inlines = [PurchaseItemsInline]
    list_display = ('date', 'account', 'total_price')

    def total_price(self, obj):
        return '{0:.2f} kr'.format(obj.total_price)


class AccountsInline(admin.TabularInline):
    model = Account
    form = forms.AccountForm
    fields = ('user', 'paid_deposit', 'balance')


class ProductsInline(admin.TabularInline):
    model = Product
    form = forms.ProductForm


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    inlines = [AccountsInline, ProductsInline]


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance')

    def balance(self, obj):
        return '{0:.2f} kr'.format(obj.balance)

admin.site.register(Deposit)
