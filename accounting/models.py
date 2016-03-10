from django.conf import settings
from django.db import models, connection
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.utils import timezone


class Book(models.Model):
    name = models.CharField(max_length=255)
    deposit = models.DecimalField(max_digits=7, decimal_places=2)

    def __str__(self):
        return self.name


class PricedItem(models.Model):
    id = models.BigIntegerField(primary_key=True)
    purchase = models.ForeignKey('Purchase', on_delete=models.DO_NOTHING, related_name='priced_items')
    product = models.ForeignKey('Product', on_delete=models.DO_NOTHING, related_name='priced_items')
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'accounting_priceditem'


class Product(models.Model):
    name = models.CharField(max_length=255)
    book = models.ForeignKey(Book, related_name='products')

    @property
    def current_price(self):
        return self.price_history.all().order_by('-date').first()

    def __str__(self):
        return self.name


class Price(models.Model):
    amount = models.DecimalField(max_digits=7, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    product = models.ForeignKey(Product, related_name='price_history')

    def __str__(self):
        return '{} kr'.format(self.amount)


class Account(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    book = models.ForeignKey(Book, related_name='accounts')
    paid_deposit = models.BooleanField(default=False)

    @property
    def balance(self):
        deposit = self.deposits.all().aggregate(total=Coalesce(Sum('amount'), 0))['total']
        purchases = PricedItem.objects.filter(purchase__account=self).aggregate(
            total=Coalesce(Sum('price'), 0))['total']
        return deposit - purchases

    def __str__(self):
        return str(self.user)

    class Meta:
        unique_together = ('user', 'book')


class Purchase(models.Model):
    date = models.DateTimeField(default=timezone.now)
    account = models.ForeignKey(Account, related_name='purchases')

    @property
    def total_price(self):
        return PricedItem.objects.filter(purchase=self).aggregate(
            total=Coalesce(Sum('price'), 0))['total']

    def __str__(self):
        return '{}: {}'.format(self.date, self.account)

    class Meta:
        ordering = ['-date', 'account']


class PurchaseItem(models.Model):
    product = models.ForeignKey(Product)
    purchase = models.ForeignKey(Purchase, related_name='items')
    amount = models.PositiveIntegerField()

    @property
    def cost(self):
        return PricedItem.objects.get(pk=self.pk).price

    def __str__(self):
        return '{} amount of {}'.format(self.amount, self.product)


class Deposit(models.Model):
    account = models.ForeignKey(Account, related_name='deposits')
    date = models.DateField(default=timezone.now)
    amount = models.DecimalField(max_digits=7, decimal_places=2)

    def __str__(self):
        return '{} kr'.format(self.amount)

    class Meta:
        ordering = ('-date',)
