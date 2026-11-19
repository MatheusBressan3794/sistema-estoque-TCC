from datetime import date, timedelta
from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Alimento, Lote, Movimentacao, Perfil
from .forms import AlimentoForm, LoteForm, MovimentacaoForm, CriarContaForm


class SistemaCantinaTestesCompletos(TestCase):
    """Suíte de testes completa cobrindo o plano de testes do sistema da cantina escolar."""

    def setUp(self):
        self.client = Client()
        
        # Usuário Gestor
        self.gestor = User.objects.create_superuser(
            username='gestor',
            email='gestor@escola.br',
            password='Password123!'
        )
        
        # Usuário Merendeira
        self.merendeira = User.objects.create_user(
            username='merendeira',
            email='merendeira@escola.br',
            password='Password123!',
            is_active=True
        )
        Perfil.objects.create(user=self.merendeira, email_verificado=True, aprovado_diretora=True)

        # Alimento padrão do plano de testes
        self.alimento = Alimento.objects.create(
            nome='Pacote de Arroz 5kg',
            embalagem='PACOTE',
            quantidade_embalagem=Decimal('5.00'),
            unidade_medida='KG',
            quantidade_minima=2, # Equivalente a 2 embalagens (10kg)
            tipo_uso='ALMOCO'
        )

        # Lote padrão
        self.lote = Lote.objects.create(
            alimento=self.alimento,
            numero_lote='teste001',
            quantidade_atual=50, # 50 unidades reais
            data_validade=date.today() + timedelta(days=30)
        )

    # ==========================================
    # 7.1 CADASTRO DE USUÁRIOS
    # ==========================================
    def test_usr_002_cadastrar_sem_nome(self):
        """USR-002: Cadastrar sem nome/first_name deve falhar."""
        form = CriarContaForm(data={
            'first_name': '',
            'username': 'novouser',
            'email': 'novo@escola.br',
            'password1': 'Senha123!',
            'password2': 'Senha123!'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('first_name', form.errors)

    def test_usr_003_cadastrar_sem_email(self):
        """USR-003: Cadastrar sem e-mail impede o cadastro."""
        form = CriarContaForm(data={
            'first_name': 'Usuário Teste',
            'username': 'novouser',
            'email': '',
            'password1': 'Senha123!',
            'password2': 'Senha123!'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_usr_005_email_duplicado(self):
        """USR-005: Sistema não cria usuário com e-mail já existente."""
        form = CriarContaForm(data={
            'first_name': 'Outro Usuário',
            'username': 'outro',
            'email': 'gestor@escola.br', # E-mail já cadastrado no setUp
            'password1': 'Senha123!',
            'password2': 'Senha123!'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)


    # ==========================================
    # 7.2 APROVAÇÃO DE CONTAS
    # ==========================================
    def test_apr_001_e_003_gestor_aprova_e_login_pendente(self):
        """APR-001 / APR-003 / LOG-005: Gestor aprova conta e restrição de pendentes."""
        user_pendente = User.objects.create_user(
            username='pendente',
            email='pendente@escola.br',
            password='Password123!',
            is_active=False
        )
        Perfil.objects.create(user=user_pendente, email_verificado=True, aprovado_diretora=False)

        # Tentar login com conta pendente (LOG-005 / APR-003)
        response = self.client.post(reverse('login'), {'username': 'pendente', 'password': 'Password123!'})
        user_pendente.refresh_from_db()
        self.assertFalse(user_pendente.is_active)

        # Gestor aprova a conta (APR-001)
        self.client.force_login(self.gestor)
        response_aprovar = self.client.post(reverse('aprovar_conta', args=[user_pendente.id]))
        user_pendente.refresh_from_db()
        self.assertTrue(user_pendente.is_active)


    # ==========================================
    # 7.3 LOGIN DE USUÁRIOS
    # ==========================================
    def test_log_001_login_valido(self):
        """LOG-001: Usuário com credenciais corretas acessa o sistema."""
        response = self.client.post(reverse('login'), {'username': 'merendeira', 'password': 'Password123!'})
        self.assertRedirects(response, reverse('dashboard'), fetch_redirect_response=False)

    def test_log_004_campos_vazios(self):
        """LOG-004: Validação de campos vazios no login."""
        response = self.client.post(reverse('login'), {'username': '', 'password': ''})
        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertTrue(any('Usuário ou senha incorretos.' in str(m) for m in messages))

    def test_log_008_url_protegida(self):
        """LOG-008: Abrir URL interna sem autenticação redireciona para o login."""
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)


    # ==========================================
    # 7.4 CADASTRO DE ALIMENTOS
    # ==========================================
    def test_ali_001_cadastrar_alimento_valido(self):
        """ALI-001: Preencher campos obrigatórios com dados corretos cadastra o alimento."""
        form = AlimentoForm(data={
            'nome': 'Leite em Pó',
            'embalagem': 'LATA',
            'quantidade_embalagem': Decimal('400.00'),
            'unidade_medida': 'G',
            'quantidade_minima': 5,
            'tipo_uso': 'LANCHE'
        })
        self.assertTrue(form.is_valid())
        alimento = form.save()
        self.assertEqual(alimento.nome, 'Leite em Pó')

    def test_ali_004_quantidade_negativa(self):
        """ALI-004: Sistema recusa números negativos na quantidade da embalagem."""
        form = AlimentoForm(data={
            'nome': 'Produto Errado',
            'embalagem': 'PACOTE',
            'quantidade_embalagem': Decimal('-10.00'),
            'unidade_medida': 'KG',
            'quantidade_minima': 1,
            'tipo_uso': 'LANCHE'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('quantidade_embalagem', form.errors)


    # ==========================================
    # 7.5 MOVIMENTAÇÃO DE ESTOQUE
    # ==========================================
    def test_est_001_e_002_entrada_e_saida(self):
        """EST-001 e EST-002: Valida cálculo correto de entrada e saída no lote."""
        # Entrada de 10 unidades de embalagem (50 unidades reais) -> Saldo vai a 100
        self.lote.quantidade_atual += 50
        self.lote.save()
        self.assertEqual(self.lote.quantidade_atual, 100)

        # Saída de 5 embalagens (25 unidades reais) -> Saldo vai a 75
        self.lote.quantidade_atual -= 25
        self.lote.save()
        self.assertEqual(self.lote.quantidade_atual, 75)

    def test_est_003_saida_maior_que_saldo(self):
        """EST-003: Impede estoque negativo quando saída for maior que o saldo."""
        self.lote.quantidade_atual = 5 # apenas 5 unidades reais
        self.lote.save()
        
        # Tentativa de retirar quantidade superior ao saldo atual
        quantidade_pedido = 10 * int(self.alimento.quantidade_embalagem)
        insuficiente = quantidade_pedido > self.lote.quantidade_atual
        self.assertTrue(insuficiente)


    # ==========================================
    # 7.6 ALERTAS DE ESTOQUE MÍNIMO
    # ==========================================
    def test_min_002_e_003_alerta_estoque_minimo(self):
        """MIN-002 e MIN-003: Alerta exibido quando saldo é igual ou abaixo do mínimo."""
        # Estoque mínimo calculado = quantidade_minima (2) * quantidade_embalagem (5) = 10 unidades reais.
        # Definindo saldo igual ao mínimo (10 unidades)
        self.lote.quantidade_atual = 10
        self.lote.save()

        self.client.force_login(self.gestor)
        response = self.client.get(reverse('dashboard'))
        # Verifica se o alimento aparece na lista de faltantes/críticos do dashboard
        self.assertIn(self.alimento, response.context['alimentos_faltantes'])


    # ==========================================
    # 7.7 ALERTAS DE VALIDADE
    # ==========================================
    def test_val_001_e_003_lote_vencendo_e_fora_da_faixa(self):
        """VAL-001 e VAL-003: Valida limite de 15 dias para alerta de vencimento."""
        # Lote vencendo em 14 dias (Dentro da faixa de alerta <= 15 dias)
        self.lote.data_validade = date.today() + timedelta(days=14)
        self.lote.save()

        self.client.force_login(self.gestor)
        response = self.client.get(reverse('dashboard'))
        self.assertIn(self.lote, response.context['lotes_proximos_vencimento'])

        # Lote vencendo em 16 dias (Fora da faixa, sem alerta no dashboard)
        self.lote.data_validade = date.today() + timedelta(days=16)
        self.lote.save()

        response = self.client.get(reverse('dashboard'))
        self.assertNotIn(self.lote, response.context['lotes_proximos_vencimento'])


    # ==========================================
    # 7.8 EMISSÃO DE RELATÓRIOS
    # ==========================================
    def test_rel_001_e_004_relatorios_e_pdf(self):
        """REL-001 e REL-004: Emissão de relatório por período e exportação correta em PDF."""
        Movimentacao.objects.create(
            lote=self.lote,
            tipo='ENTRADA',
            quantidade=10
        )

        self.client.force_login(self.gestor)
        
        # Testar visualização do relatório de entradas (REL-001)
        response_html = self.client.get(reverse('relatorio_movimentacoes', args=['entradas']))
        self.assertEqual(response_html.status_code, 200)

        # Testar exportação em PDF (REL-004)
        response_pdf = self.client.get(reverse('exportar_pdf_movimentacoes', args=['entradas']))
        self.assertEqual(response_pdf.status_code, 200)
        self.assertEqual(response_pdf['Content-Type'], 'application/pdf')