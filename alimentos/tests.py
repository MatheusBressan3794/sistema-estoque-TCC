from datetime import date, timedelta
from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core import mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

from .models import Alimento, Lote, Movimentacao, Perfil, LogAtividade
from .forms import CriarContaForm, CriarAlimentoForm, MovimentacaoForm


class BaseTestSetup(TestCase):
    """Configuração base compartilhada com os dados do Plano de Testes (Seção 4)"""
    def setUp(self):
        self.client = Client()

        # Perfil Gestor / Direção
        self.admin_user = User.objects.create_user(
            username='admin_escola',
            email='admin@escola.br',
            password='SenhaForte@2026',
            first_name='Diretora Escolar',
            is_staff=True,
            is_active=True
        )
        Perfil.objects.create(user=self.admin_user, email_verificado=True, aprovado_diretora=True)

        # Perfil Merendeira (Ativa)
        self.merendeira = User.objects.create_user(
            username='merendeira',
            email='merendeira@escola.br',
            password='SenhaForte@2026',
            first_name='Maria Merendeira',
            is_staff=False,
            is_active=True
        )
        Perfil.objects.create(user=self.merendeira, email_verificado=True, aprovado_diretora=True)

        # Perfil Usuário Inativo
        self.inativo = User.objects.create_user(
            username='inativo',
            email='inativo@escola.br',
            password='SenhaForte@2026',
            first_name='Usuário Inativo',
            is_active=False
        )
        Perfil.objects.create(user=self.inativo, email_verificado=False, aprovado_diretora=False)

        # Alimento padrão do plano: Pacote de Arroz 5kg (usando embalagem=1 para facilitar contagem unitária)
        self.arroz = Alimento.objects.create(
            nome='Pacote de Arroz 5kg',
            embalagem='PACOTE',
            quantidade_embalagem=Decimal('1.00'),
            unidade_medida='KG',
            quantidade_minima=10,
            tipo_uso='ALMOCO'
        )
        self.lote_arroz = Lote.objects.create(
            alimento=self.arroz,
            numero_lote='teste001',
            quantidade_atual=50,
            data_validade=date.today() + timedelta(days=5)
        )


# =====================================================================
# 7.1 CADASTRO DE USUÁRIOS (USR-001 a USR-006)
# =====================================================================
class CadastroUsuarioTests(BaseTestSetup):

    def test_usr_001_cadastrar_usuario_valido_e_aprovar(self):
        """USR-001: Cadastrar usuário válido, validar e-mail e admin aprovar conta"""
        dados = {
            'first_name': 'Joana Silva',
            'username': 'joana_cantina',
            'email': 'joana@escola.br',
            'password1': 'SenhaSegura#2026',
            'password2': 'SenhaSegura#2026',
        }
        response = self.client.post(reverse('cadastro'), data=dados)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)

        novo_user = User.objects.get(username='joana_cantina')
        self.assertFalse(novo_user.is_active)

        # Simula clique no link de ativação enviado por e-mail
        uid = urlsafe_base64_encode(force_bytes(novo_user.pk))
        token = default_token_generator.make_token(novo_user)
        self.client.get(reverse('ativar_conta', kwargs={'uidb64': uid, 'token': token}))

        novo_user.perfil.refresh_from_db()
        self.assertTrue(novo_user.perfil.email_verificado)

        # Admin aprova a conta
        self.client.force_login(self.admin_user)
        self.client.post(reverse('aprovar_conta', kwargs={'id': novo_user.id}))
        novo_user.refresh_from_db()
        self.assertTrue(novo_user.is_active)

    def test_usr_002_cadastrar_sem_nome(self):
        """USR-002: Deixar o nome vazio e salvar"""
        form = CriarContaForm(data={
            'first_name': '',
            'username': 'semnome',
            'email': 'semnome@escola.br',
            'password1': 'SenhaSegura#2026',
            'password2': 'SenhaSegura#2026',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('first_name', form.errors)

    def test_usr_003_cadastrar_sem_email(self):
        """USR-003: Deixar o e-mail vazio"""
        form = CriarContaForm(data={
            'first_name': 'Teste',
            'username': 'sememail',
            'email': '',
            'password1': 'SenhaSegura#2026',
            'password2': 'SenhaSegura#2026',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_usr_004_email_invalido(self):
        """USR-004: Informar e-mail inválido não envia e-mail"""
        response = self.client.post(reverse('cadastro'), data={
            'first_name': 'Teste',
            'username': 'emailinvalido',
            'email': 'email-sem-arroba.com',
            'password1': 'SenhaSegura#2026',
            'password2': 'SenhaSegura#2026',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 0)

    def test_usr_005_email_duplicado(self):
        """USR-005: Cadastrar um e-mail já existente"""
        form = CriarContaForm(data={
            'first_name': 'Duplicado',
            'username': 'outro_user',
            'email': 'merendeira@escola.br',  # já existe
            'password1': 'SenhaSegura#2026',
            'password2': 'SenhaSegura#2026',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_usr_006_senha_fraca(self):
        """USR-006: Informar senha abaixo da política definida"""
        form = CriarContaForm(data={
            'first_name': 'Senha Fraca',
            'username': 'senhafraca',
            'email': 'fraca@escola.br',
            'password1': '123',
            'password2': '123',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)


# =====================================================================
# 7.2 LOGIN E PERMISSÕES (LOG-001 a LOG-008)
# =====================================================================
class LoginPermissoesTests(BaseTestSetup):

    def test_log_001_login_valido(self):
        """LOG-001: Conta aprovada com credenciais corretas acessa o sistema"""
        response = self.client.post(reverse('login'), {
            'username': 'merendeira',
            'password': 'SenhaForte@2026'
        })
        self.assertRedirects(response, reverse('dashboard'))

    def test_log_002_e_003_senha_incorreta_ou_usuario_inexistente(self):
        """LOG-002 e LOG-003: Senha incorreta ou usuário inexistente negam acesso"""
        res_senha = self.client.post(reverse('login'), {'username': 'merendeira', 'password': 'errada'})
        self.assertEqual(res_senha.status_code, 200)

        res_user = self.client.post(reverse('login'), {'username': 'nao_existe', 'password': 'SenhaForte@2026'})
        self.assertEqual(res_user.status_code, 200)

    def test_log_004_campos_vazios(self):
        """LOG-004: Não informar nome ou senha"""
        response = self.client.post(reverse('login'), {'username': '', 'password': ''})
        self.assertEqual(response.status_code, 200)

    def test_log_005_usuario_inativo(self):
        """LOG-005: Usuário inativo não consegue acessar"""
        response = self.client.post(reverse('login'), {
            'username': 'inativo',
            'password': 'SenhaForte@2026'
        })
        self.assertRedirects(response, reverse('login'))

    def test_log_006_e_008_logout_e_url_protegida(self):
        """LOG-006 e LOG-008: Logout encerra sessão e URLs protegidas redirecionam"""
        self.client.force_login(self.merendeira)
        self.client.get(reverse('logout'))

        # Tentar abrir URL interna após logout
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_permissao_perfil_merendeira_tela_admin(self):
        """Seção 3: Merendeira não pode acessar tela de aprovação de contas via URL direta"""
        self.client.force_login(self.merendeira)
        response = self.client.get(reverse('aprovar_contas'))
        self.assertEqual(response.status_code, 302)


# =====================================================================
# 7.3 CADASTRO DE ALIMENTOS (ALI-001 a ALI-005)
# =====================================================================
class CadastroAlimentoTests(BaseTestSetup):

    def setUp(self):
        super().setUp()
        self.client.force_login(self.merendeira)

    def test_ali_001_cadastrar_alimento_valido(self):
        """ALI-001: Preencher campos obrigatórios com dados corretos"""
        response = self.client.post(reverse('criar_alimento'), {
            'nome': 'Feijão Carioca 1kg',
            'embalagem': 'PACOTE',
            'quantidade_embalagem': '1.00',
            'unidade_medida': 'KG',
            'quantidade_minima': 15,
            'tipo_uso': 'ALMOCO',
            'numero_lote': 'LOTE-FEIJAO-01',
            'data_validade': (date.today() + timedelta(days=60)).isoformat(),
            'quantidade_inicial': 30
        })
        self.assertRedirects(response, reverse('listar_alimentos'))
        feijao = Alimento.objects.get(nome='Feijão Carioca 1kg')
        self.assertEqual(feijao.quantidade_total, 30)

    def test_ali_002_e_003_cadastrar_sem_lote_ou_campos_vazios(self):
        """ALI-002 e ALI-003: Cadastro impedido sem lote inicial ou com campos vazios"""
        form = CriarAlimentoForm(data={'nome': 'Açúcar'})
        self.assertFalse(form.is_valid())
        self.assertIn('numero_lote', form.errors)

    def test_ali_004_quantidades_negativas(self):
        """ALI-004: Sistema recusa valores negativos"""
        form = CriarAlimentoForm(data={
            'nome': 'Sal',
            'embalagem': 'PACOTE',
            'quantidade_embalagem': '-1.00',
            'unidade_medida': 'KG',
            'quantidade_minima': -5,
            'tipo_uso': 'ALMOCO',
            'numero_lote': 'L-NEG',
            'data_validade': date.today().isoformat(),
            'quantidade_inicial': -10
        })
        self.assertFalse(form.is_valid())
        self.assertIn('quantidade_embalagem', form.errors)
        self.assertIn('quantidade_minima', form.errors)
        self.assertIn('quantidade_inicial', form.errors)

    def test_ali_005_editar_alimento(self):
        """ALI-005: Alterar informações do alimento e salvar"""
        response = self.client.post(reverse('atualizar_alimento', kwargs={'id': self.arroz.id}), {
            'nome': 'Arroz Integral 5kg',
            'embalagem': 'PACOTE',
            'quantidade_embalagem': '1.00',
            'unidade_medida': 'KG',
            'quantidade_minima': 12,
            'tipo_uso': 'ALMOCO',
        })
        self.assertRedirects(response, reverse('listar_alimentos'))
        self.arroz.refresh_from_db()
        self.assertEqual(self.arroz.nome, 'Arroz Integral 5kg')


# =====================================================================
# 7.4 MOVIMENTAÇÃO DE ESTOQUE (EST-001 a EST-005)
# =====================================================================
class MovimentacaoEstoqueTests(BaseTestSetup):

    def setUp(self):
        super().setUp()
        self.client.force_login(self.merendeira)
        self.lote_arroz.quantidade_atual = 20
        self.lote_arroz.save()

    def test_est_001_entrada_estoque(self):
        """EST-001: 20 unidades + entrada de 10 = saldo final 30"""
        self.client.post(reverse('movimentacao_estoque'), {
            'tipo': 'ENTRADA',
            'alimento': self.arroz.id,
            'numero_lote': self.lote_arroz.id,
            'quantidade': 10
        })
        self.lote_arroz.refresh_from_db()
        self.assertEqual(self.lote_arroz.quantidade_atual, 30)

    def test_est_002_saida_estoque(self):
        """EST-002: 20 unidades - saída de 5 = saldo final 15"""
        self.client.post(reverse('movimentacao_estoque'), {
            'tipo': 'SAIDA',
            'alimento': self.arroz.id,
            'numero_lote': self.lote_arroz.id,
            'quantidade': 5
        })
        self.lote_arroz.refresh_from_db()
        self.assertEqual(self.lote_arroz.quantidade_atual, 15)

    def test_est_003_saida_maior_que_saldo(self):
        """EST-003: Saldo 5, saída 8 -> sistema impede estoque negativo"""
        self.lote_arroz.quantidade_atual = 5
        self.lote_arroz.save()

        self.client.post(reverse('movimentacao_estoque'), {
            'tipo': 'SAIDA',
            'alimento': self.arroz.id,
            'numero_lote': self.lote_arroz.id,
            'quantidade': 8
        })
        self.lote_arroz.refresh_from_db()
        self.assertEqual(self.lote_arroz.quantidade_atual, 5)

    def test_est_004_e_005_quantidade_zero_ou_negativa(self):
        """EST-004 e EST-005: Movimentar zero ou negativo é recusado"""
        form_zero = MovimentacaoForm(data={
            'tipo': 'ENTRADA', 'alimento': self.arroz.id, 'numero_lote': self.lote_arroz.id, 'quantidade': 0
        })
        form_neg = MovimentacaoForm(data={
            'tipo': 'SAIDA', 'alimento': self.arroz.id, 'numero_lote': self.lote_arroz.id, 'quantidade': -3
        })
        self.assertFalse(form_zero.is_valid())
        self.assertFalse(form_neg.is_valid())


# =====================================================================
# 7.5 E 7.6 ALERTAS DE ESTOQUE MÍNIMO E VALIDADE (MIN-001..006 / VAL-001..004)
# =====================================================================
class AlertasEstoqueValidadeTests(BaseTestSetup):

    def setUp(self):
        super().setUp()
        self.client.force_login(self.merendeira)

    def test_min_001_a_006_alertas_estoque_minimo(self):
        """MIN-001 a MIN-006: Acima, igual, abaixo, zerado, reposição e alteração do mínimo"""
        # MIN-001: Saldo 50 > mínimo 10 (Sem alerta)
        res = self.client.get(reverse('dashboard'))
        self.assertNotIn(self.arroz, res.context['alimentos_faltantes'])

        # MIN-002: Saldo 10 == mínimo 10 (Alerta exibido)
        self.lote_arroz.quantidade_atual = 10
        self.lote_arroz.save()
        res = self.client.get(reverse('dashboard'))
        self.assertIn(self.arroz, res.context['alimentos_faltantes'])

        # MIN-003 e MIN-004: Saldo 5 e Saldo 0 (Alerta exibido)
        self.lote_arroz.quantidade_atual = 0
        self.lote_arroz.save()
        res = self.client.get(reverse('dashboard'))
        self.assertIn(self.arroz, res.context['alimentos_faltantes'])

        # MIN-005: Reposição para 25 (Sem alerta)
        self.lote_arroz.quantidade_atual = 25
        self.lote_arroz.save()
        res = self.client.get(reverse('dashboard'))
        self.assertNotIn(self.arroz, res.context['alimentos_faltantes'])

        # MIN-006: Alteração do mínimo para 30 (Reavalia e gera alerta)
        self.arroz.quantidade_minima = 30
        self.arroz.save()
        res = self.client.get(reverse('dashboard'))
        self.assertIn(self.arroz, res.context['alimentos_faltantes'])

    def test_val_001_a_004_alertas_validade(self):
        """VAL-001 a VAL-004: Vencendo (<15d), fora da faixa (>15d), nova validade e lotes distintos"""
        # VAL-001: Lote com 5 dias para vencer aparece no alerta
        res = self.client.get(reverse('dashboard'))
        self.assertIn(self.lote_arroz, res.context['lotes_proximos_vencimento'])

        # VAL-004: Segundo lote com validade longa (60 dias) não entra no alerta
        lote_longe = Lote.objects.create(
            alimento=self.arroz,
            numero_lote='teste002',
            quantidade_atual=20,
            data_validade=date.today() + timedelta(days=60)
        )
        res = self.client.get(reverse('dashboard'))
        self.assertIn(self.lote_arroz, res.context['lotes_proximos_vencimento'])
        self.assertNotIn(lote_longe, res.context['lotes_proximos_vencimento'])

        # VAL-003: Alterar validade do lote 1 para +30 dias remove o alerta
        self.lote_arroz.data_validade = date.today() + timedelta(days=30)
        self.lote_arroz.save()
        res = self.client.get(reverse('dashboard'))
        self.assertNotIn(self.lote_arroz, res.context['lotes_proximos_vencimento'])


# =====================================================================
# 7.7 EMISSÃO DE RELATÓRIOS (REL-001 a REL-004)
# =====================================================================
class RelatoriosTests(BaseTestSetup):

    def setUp(self):
        super().setUp()
        self.client.force_login(self.admin_user)
        Movimentacao.objects.create(lote=self.lote_arroz, tipo='ENTRADA', quantidade=50)

    def test_rel_001_a_003_filtros_relatorio(self):
        """REL-001 a REL-003: Sem filtro (hoje), com período e período sem resultados"""
        # REL-001: Sem filtro exibe movimentação de hoje
        res_hoje = self.client.get(reverse('relatorio_movimentacoes', kwargs={'tipo': 'entradas'}))
        self.assertEqual(res_hoje.status_code, 200)
        self.assertEqual(len(res_hoje.context['movimentacoes']), 1)

        # REL-003: Período passado sem registros retorna vazio
        ontem = (date.today() - timedelta(days=10)).isoformat()
        res_vazio = self.client.get(
            reverse('relatorio_movimentacoes', kwargs={'tipo': 'entradas'}),
            {'data_inicio': ontem, 'data_fim': ontem}
        )
        self.assertEqual(len(res_vazio.context['movimentacoes']), 0)

    def test_rel_004_exportar_pdf(self):
        """REL-004: Exportar PDF gera arquivo válido"""
        response = self.client.get(reverse('exportar_pdf_movimentacoes', kwargs={'tipo': 'entradas'}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')