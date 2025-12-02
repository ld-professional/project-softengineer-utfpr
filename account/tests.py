import json
from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch
from clientes.models import Cliente
from account.models import UserPersonalizado


class SignupViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse("signup")

        self.valid_payload = {
            "username": "usuario_teste",
            "email": "teste@example.com",
            "telefone": "11999999999",
            "password": "senhaSegura123",
            "password_confirm": "senhaSegura123",
        }

    def test_01_get_retorna_template(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_02_post_valido_cria_usuario_e_cliente(self):
        response = self.client.post(
            self.url,
            data=json.dumps(self.valid_payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)

        # Usuário criado
        self.assertTrue(
            UserPersonalizado.objects.filter(username="usuario_teste").exists()
        )

        # Cliente criado
        user = UserPersonalizado.objects.get(username="usuario_teste")
        self.assertTrue(Cliente.objects.filter(fk_user=user).exists())

        # JSON correto
        data = response.json()
        self.assertEqual(data["status"], "ok")
        self.assertIn("redirect_url", data)

    def test_03_post_invalido_retorna_400(self):
        payload = self.valid_payload.copy()
        payload["password_confirm"] = "errada"

        response = self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)

        data = response.json()
        self.assertIn("errors", data)

    @patch("account.forms.CadastroClienteForm.is_valid", return_value=True)
    @patch("account.views.UserPersonalizado.objects.create_user")
    def test_04_post_dispara_erro_interno(self, mock_create_user, mock_form_valid):
        mock_create_user.side_effect = Exception("Erro simulado")

        response = self.client.post(
            self.url,
            data=json.dumps(self.valid_payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 500)
        self.assertIn("error", response.json())
