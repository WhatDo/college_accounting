from django.conf import settings
from django.db import models, connection


class Book(models.Model):
    name = models.CharField(max_length=255)
    accounts = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Account')
    deposit = models.DecimalField(max_digits=7, decimal_places=2)

    def __str__(self):
        return self.name


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
    book = models.ForeignKey(Book)
    paid_deposit = models.BooleanField(default=False)

    @property
    def balance(self):
        cursor = connection.cursor()
        cursor.execute("""
SELECT coalesce((SELECT Sum(amount) FROM accounting_deposit WHERE account_id = %s),0) -
       coalesce((
  SELECT Sum(cost)
  FROM (
    SELECT
      price * count AS cost,
      account_id
    FROM (
      SELECT
        accounting_price.amount        AS price,
        accounting_purchaseitem.amount AS count,
        accounting_purchaseitem.id,
        accounting_purchase.account_id
      FROM accounting_price
        JOIN accounting_product ON accounting_price.product_id = accounting_product.id
        JOIN accounting_purchaseitem ON accounting_product.id = accounting_purchaseitem.product_id
        JOIN accounting_purchase ON accounting_purchaseitem.purchase_id = accounting_purchase.id
      ORDER BY accounting_price.date
        DESC
    )
    GROUP BY id
  )
  WHERE account_id = %s
),0)
        """, [self.pk, self.pk])

        return cursor.fetchone()[0]

    def __str__(self):
        return str(self.user)

    class Meta:
        unique_together = ('user', 'book')


class Purchase(models.Model):
    date = models.DateField(auto_now_add=True)
    account = models.ForeignKey(Account, related_name='purchases')

    @property
    def total_price(self):
        cursor = connection.cursor()
        cursor.execute("""
SELECT Sum(cost) FROM (
SELECT price * count AS cost FROM (
SELECT accounting_price.amount AS price,
       accounting_purchaseitem.amount AS count,
       date,
       accounting_purchaseitem.purchase_id,
       accounting_purchaseitem.id
FROM accounting_price
  JOIN accounting_product ON accounting_price.product_id = accounting_product.id
  JOIN accounting_purchaseitem ON accounting_product.id = accounting_purchaseitem.product_id ORDER BY date DESC
) WHERE purchase_id = %s AND date <= %s GROUP BY id);
        """, [self.pk, self.date])
        return cursor.fetchone()[0]

    def __str__(self):
        return '{}: {}'.format(self.date, self.account)

    class Meta:
        ordering = ['-date', 'account']


class PurchaseItem(models.Model):
    product = models.ForeignKey(Product)
    purchase = models.ForeignKey(Purchase, related_name='items')
    amount = models.PositiveIntegerField()

    def __str__(self):
        return '{} amount of {}'.format(self.amount, self.product)


class Deposit(models.Model):
    account = models.ForeignKey(Account, related_name='deposits')
    date = models.DateField(auto_now_add=True)
    amount = models.DecimalField(max_digits=7, decimal_places=2)
