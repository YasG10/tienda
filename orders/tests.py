from django.test import TestCase, Client
from django.urls import reverse
from users.models import User
from catalog.models import Category, Product
from addresses.models import Address
from orders.models import Order


class CheckoutFlowTest(TestCase):
	def setUp(self):
		self.client = Client()
		# create user
		self.user = User.objects.create_user(username='alice', password='pass123')

		# create category and product
		self.cat = Category.objects.create(name='Test')
		self.product = Product.objects.create(
			category=self.cat,
			name='Widget',
			description='Test product',
			price=10.00,
			stock=5
		)

	def test_checkout_requires_address_and_creates_order(self):
		# login
		self.client.login(username='alice', password='pass123')

		# add product to session cart
		session = self.client.session
		session['cart'] = {str(self.product.id): 2}
		session.save()

		# Access checkout: since no address, should redirect to create
		resp = self.client.get(reverse('orders:checkout'))
		self.assertEqual(resp.status_code, 302)
		self.assertIn(reverse('addresses:create'), resp.url)

		# Create an address
		addr = Address.objects.create(
			user=self.user,
			province='P', city='C', street='Street 1', phone='123'
		)

		# Try checkout POST
		resp = self.client.post(reverse('orders:checkout'), data={'address_id': addr.id}, follow=True)
		# After checkout should redirect to confirmation
		self.assertTrue(Order.objects.filter(user=self.user).exists())
		order = Order.objects.get(user=self.user)
		self.assertEqual(order.total_amount, self.product.price * 2)

	def test_checkout_insufficient_stock(self):
		# login
		self.client.login(username='alice', password='pass123')

		# add product to session cart with excessive qty
		session = self.client.session
		session['cart'] = {str(self.product.id): 10}
		session.save()

		# create address
		addr = Address.objects.create(
			user=self.user,
			province='P', city='C', street='Street 1', phone='123'
		)

		resp = self.client.post(reverse('orders:checkout'), data={'address_id': addr.id}, follow=True)
		# Should not create an order due to insufficient stock
		self.assertFalse(Order.objects.filter(user=self.user).exists())

	def test_multi_product_order(self):
		# create second product
		p2 = Product.objects.create(category=self.cat, name='Gadget', description='Gadget', price=5.00, stock=3)
		self.client.login(username='alice', password='pass123')
		session = self.client.session
		session['cart'] = {str(self.product.id): 1, str(p2.id): 2}
		session.save()

		addr = Address.objects.create(
			user=self.user,
			province='P', city='C', street='Street 1', phone='123'
		)

		resp = self.client.post(reverse('orders:checkout'), data={'address_id': addr.id}, follow=True)
		self.assertTrue(Order.objects.filter(user=self.user).exists())
		order = Order.objects.get(user=self.user)
		expected_total = self.product.price * 1 + p2.price * 2
		self.assertEqual(order.total_amount, expected_total)

