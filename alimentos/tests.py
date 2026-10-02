from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from .models import Etec, Perfil


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class CadastroDoubleOptInTests(TestCase):
	def setUp(self):
		self.etec = Etec.objects.create(
			codigo='058',
			nome='Etec de Teste',
			cidade='Araras',
		)

	def criar_conta(self, username, email):
		return self.client.post(reverse('cadastro'), {
			'username': username,
			'first_name': 'Pessoa Teste',
			'email': email,
			'etec': self.etec.pk,
			'password1': 'Teste-seguro-2026!',
			'password2': 'Teste-seguro-2026!',
		})

	def test_cadastro_cria_conta_inativa_e_envia_verificacao(self):
		response = self.criar_conta('pessoa', 'pessoa@example.com')

		self.assertRedirects(response, reverse('login'))
		user = User.objects.get(username='pessoa')
		self.assertFalse(user.is_active)
		self.assertFalse(user.perfil.email_verificado)
		self.assertEqual(user.perfil.etec, self.etec)
		self.assertEqual(len(mail.outbox), 1)
		self.assertIn('ativar/', mail.outbox[0].body)

	def test_confirmacao_verifica_email_sem_ativar_usuario(self):
		self.criar_conta('pessoa', 'pessoa@example.com')
		user = User.objects.get(username='pessoa')
		uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
		token = default_token_generator.make_token(user)
		activation_url = reverse('ativar_conta', kwargs={'uidb64': uidb64, 'token': token})

		response = self.client.get(activation_url)

		user.refresh_from_db()
		user.perfil.refresh_from_db()
		self.assertRedirects(response, reverse('login'))
		self.assertTrue(user.perfil.email_verificado)
		self.assertFalse(user.is_active)

	def test_fila_mostra_somente_contas_com_email_verificado(self):
		verificado = User.objects.create_user(
			username='verificado', password='Teste-seguro-2026!', is_active=False
		)
		Perfil.objects.create(user=verificado, etec=self.etec, email_verificado=True)
		nao_verificado = User.objects.create_user(
			username='nao-verificado', password='Teste-seguro-2026!', is_active=False
		)
		Perfil.objects.create(user=nao_verificado, etec=self.etec, email_verificado=False)
		coordenadora = User.objects.create_user(
			username='coordenadora', password='Teste-seguro-2026!', is_staff=True
		)
		self.client.force_login(coordenadora)

		response = self.client.get(reverse('aprovar_contas'))

		pendentes = list(response.context['pendentes'])
		self.assertEqual([user.pk for user in pendentes], [verificado.pk])
