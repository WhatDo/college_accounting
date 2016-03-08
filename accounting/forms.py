from decimal import Decimal
from django import forms
from django.forms import BaseInlineFormSet, ModelForm

from accounting.models import Price


class AtLeastOneFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()

        if any(self.errors):
            return

        if not any(cleaned_data and not cleaned_data.get('DELETE', False) for cleaned_data in self.cleaned_data):
            raise forms.ValidationError('Need at least one {}'.format(self.model._meta.object_name.lower()))


class EditableOnCreateForm(ModelForm):
    readonly_fields = ()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            for field in self.readonly_fields:
                attrs = self.fields[field].widget.attrs
                attrs['readonly'] = True
                attrs['disabled'] = True


class ProductForm(ModelForm):
    price = forms.DecimalField(decimal_places=2, min_value=Decimal(0))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.current_price:
            self.fields['price'].initial = self.instance.current_price.amount

    def save(self, commit=True):
        product = super().save(commit)

        new_price = self.cleaned_data['price']

        if not product.current_price or new_price != product.current_price.amount:
            product.price_history.add(Price.objects.create(amount=new_price, product=product))

        return product


class AccountForm(ModelForm):
    balance = forms.DecimalField(decimal_places=2)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            balance = self.fields['balance']
            balance.initial = self.instance.balance
            balance.widget.attrs['readonly'] = True
            balance.widget.attrs['disabled'] = True
