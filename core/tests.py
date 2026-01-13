from django.test import TestCase, Client
from django.urls import reverse
from users.models import User
from catalog.models import Category, Product
from addresses.models import Address
from orders.models import Order


class SmokeTest(TestCase):
	def setUp(self):
		self.client = Client()
		self.user = User.objects.create_user(username='bob', password='secret')
		self.cat = Category.objects.create(name='Smoke')
		self.product = Product.objects.create(
			category=self.cat,
			name='SmokeProduct',
			description='Product for smoke tests',
			price=12.5,
			stock=10
		)

	def test_public_pages_and_navigation(self):
		# Home
		resp = self.client.get(reverse('catalog:home'))
		self.assertEqual(resp.status_code, 200)

		# Catalog list
		resp = self.client.get(reverse('catalog:product_list'))
		self.assertEqual(resp.status_code, 200)

		# Product detail
		resp = self.client.get(reverse('catalog:product_detail', args=[self.product.id]))
		self.assertEqual(resp.status_code, 200)

		# Add to cart (POST)
		resp = self.client.post(reverse('orders:cart_add', args=[self.product.id]), data={'quantity': 1})
		# Should redirect to cart
		self.assertIn(resp.status_code, (302, 303))

		# Cart view
		resp = self.client.get(reverse('orders:cart'))
		self.assertEqual(resp.status_code, 200)

		# Checkout (anonymous -> redirected to login)
		resp = self.client.get(reverse('orders:checkout'))
		self.assertIn(resp.status_code, (302, 303))

	def test_authenticated_checkout_flow_navigation(self):
		# login
		self.client.login(username='bob', password='secret')

		# prepare cart
		session = self.client.session
		session['cart'] = {str(self.product.id): 1}
		session.save()

		# create address
		addr = Address.objects.create(user=self.user, province='P', city='C', street='S', phone='555')

		# GET checkout (should show form)
		resp = self.client.get(reverse('orders:checkout'))
		self.assertEqual(resp.status_code, 200)

		# POST checkout -> should create order and redirect to confirmation
		resp = self.client.post(reverse('orders:checkout'), data={'address_id': addr.id}, follow=True)
		self.assertTrue(Order.objects.filter(user=self.user).exists())
		order = Order.objects.get(user=self.user)
		self.assertIn('confirmation', resp.request['PATH_INFO'])
		self.assertEqual(order.total_amount, self.product.price)
