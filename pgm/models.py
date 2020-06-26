from django.db import models
from datetime import datetime
from django.utils import timezone
import re

# Create your models here.

class dadosImob(models.Model):
    cda = models.CharField(max_length=20)
    cda_ant = models.CharField(max_length=20, null=True)
    contrib_id = models.CharField(max_length=50, null=True)
    cpf_cnpj = models.CharField(max_length=20, null=True)
    contrib_nome = models.CharField(max_length=150, null=True)
    fixo_ddd = models.CharField(max_length=50, null=True)
    fixo_num = models.CharField(max_length=20, null=True)
    cel_ddd = models.CharField(max_length=50, null=True)
    cel_num = models.CharField(max_length=20, null=True)
    email = models.CharField(max_length=150, null=True)
    cep = models.CharField(max_length=50, null=True)
    logr_tipo = models.CharField(max_length=20, null=True)
    logr_nome = models.CharField(max_length=200, null=True)
    logr_num = models.CharField(max_length=20, null=True)
    logr_compl = models.CharField(max_length=200, null=True)
    bairro_tipo = models.CharField(max_length=50, null=True)
    bairro_nome = models.CharField(max_length=200, null=True)
    cidade = models.CharField(max_length=200, null=True)
    uf = models.CharField(max_length=50, null=True)
    receita_tipo = models.CharField(max_length=50, null=True)
    inscricao_num = models.CharField(max_length=50, null=True)
    inscricao_tipo = models.CharField(max_length=50, null=True)
    natureza_credito = models.CharField(max_length=200, null=True)
    tipo_doc_base_insc = models.CharField(max_length=200, null=True)
    documento_data = models.DateField(null=True)
    processo_num = models.CharField(max_length=50, null=True)
    processo_data = models.DateField(null=True)
    despacho_data = models.DateField(null=True)
    documento_num = models.CharField(max_length=50, null=True)
    debito_valor = models.FloatField(default=0)
    debito_atualizacao = models.FloatField(default=0)
    debito_juros = models.FloatField(default=0)
    debito_multa = models.FloatField(default=0)
    debito_desconto = models.FloatField(default=0)
    debito_atualizado = models.FloatField(default=0)
    lavratura_data = models.DateField(null=True)
    lavratura_hora = models.TimeField(null=True)
    lavratura_usuario = models.CharField(max_length=200, null=True)
    vencimento = models.DateField(null=True)
    debito_dia = models.CharField(max_length=50, null=True)
    debito_mes = models.CharField(max_length=50, null=True)
    parcela_num = models.CharField(max_length=50, null=True)
    debito_ano = models.CharField(max_length=50, null=True)
    parcela_situa = models.CharField(max_length=50, null=True)
    prescricao_causa_inter = models.CharField(max_length=80, null=True)
    prescricao_data_inter = models.DateField(null=True)
    prescricao_mot_susp_prazo = models.CharField(max_length=200, null=True)
    prescricao_mot_data_ini = models.DateField(null=True)
    prescricao_mot_data_fim = models.DateField(null=True)
    fundamentacao_legal = models.CharField(max_length=200, null=True)
    logr_tipo_el = models.CharField(max_length=20, null=True)
    logr_nome_el = models.TextField(null=True)
    logr_num_el = models.CharField(max_length=20, null=True)
    logr_compl_el = models.CharField(max_length=200, null=True)
    bairro_tipo_el = models.CharField(max_length=50, null=True)
    bairro_nome_el = models.CharField(max_length=200, null=True)
    cep_el = models.CharField(max_length=50, null=True)
    cidade_el = models.CharField(max_length=200, null=True)
    uf_el = models.CharField(max_length=50, null=True)
    logr_tipo_ee = models.CharField(max_length=20, null=True)
    logr_nome_ee = models.CharField(max_length=200, null=True)
    logr_num_ee = models.CharField(max_length=20, null=True)
    logr_compl_ee = models.CharField(max_length=200, null=True)
    bairro_tipo_ee = models.CharField(max_length=50, null=True)
    bairro_nome_ee = models.CharField(max_length=200, null=True)
    cep_ee = models.CharField(max_length=50, null=True)
    cidade_ee = models.CharField(max_length=200, null=True)
    uf_ee = models.CharField(max_length=50, null=True)
    total_cda = models.FloatField(default=0)
    parcelas = models.IntegerField(default=0)

    def __str__(self):
        return "%s%s%s%s%s%s%s%s%s%s%s%s\n" % \
               (
                   self.contrib_id + ";",
                   self.contrib_nome + ";",
                   self.cpf_cnpj + ";",
                   self.cep + ";",
                   self.logr_tipo + ";",
                   self.logr_nome + ";",
                   ("SN" if self.logr_num==None else self.logr_num) + ";",
                   (" " if self.logr_compl==None else self.logr_compl) + ";",
                   self.bairro_tipo + ";",
                   self.bairro_nome + ";",
                   self.cidade + ";",
                   self.uf + ";"
               )


class RemessaCDL(models.Model):
    tipo_registro = models.CharField(max_length=2, default='00')
    operacao = models.CharField(max_length=7, default='REMESSA')
    data_movimento = models.DateField(auto_now_add=True) #DDMMAAAA
    remessa_id = models.AutoField(primary_key=True) #tamanho 8 no arquivo
    #entidade = models.CharField(max_length=5, null=True)
    #associado = models.CharField(max_length=8, null=True)
    data_movimento_arquivo = models.DateField(default=timezone.now) #AAAAMMDD
    unidade_negocio = models.CharField(max_length=5, default='SPC  ')
    numero_versao = models.CharField(max_length=2, default='12')
    codigo_retorno = models.CharField(max_length=10, null=True)
    sequencial_registro = models.IntegerField(null=True, default=1)
    enviada = models.BooleanField(default=False)

    def __str__(self):
        return "%s%s%s%s%s%s%s%s%s%s%s%s\n" % \
               (
                self.tipo_registro,
                self.operacao,
                self.data_movimento.strftime('%d%m%Y'),
                format(self.remessa_id, '08d'),
                '13001',
                '00004085',
                self.data_movimento_arquivo.strftime('%Y%m%d'),
                repeat_to_length(' ', 321),
                self.unidade_negocio,
                self.numero_versao,
                repeat_to_length(' ', 10) if self.codigo_retorno == None else self.codigo_retorno.ljust(10),
                format(self.sequencial_registro, '06d')
               )



class RegistroCDL(models.Model):
    tipo_registroc = models.CharField(max_length=2, default='01')
    praca_concessaoc = models.CharField(max_length=8, default='64000070')
    nome_razaoc = models.CharField(max_length=45, null=True)
    tipo_documentoc = models.CharField(max_length=1, default='2')
    cpf_cnpjc = models.CharField(max_length=15, null=True)
    rgc = models.CharField(max_length=20, null=True)
    data_nascimentoc = models.DateField(null=True) #DDMMAAAA
    filiacaoc = models.CharField(max_length=45, null=True) #Nome da mãe
    enderecoc = models.CharField(max_length=50, null=True)
    numeroc = models.CharField(max_length=5, null=True)
    complementoc = models.CharField(max_length=30, null=True)
    bairroc = models.CharField(max_length=25, null=True)
    cepc = models.CharField(max_length=8, default='64000000')
    cidadec = models.CharField(max_length=30, null=True)
    ufc = models.CharField(max_length=2, default='PI', null=True)
    fone_dddc = models.CharField(max_length=2, default='86', null=True)
    fone_numeroc = models.CharField(max_length=10, default='0', null=True)
    emailc = models.CharField(max_length=50, null=True)
    codigo_retornoc = models.CharField(max_length=10, null=True)
    sequencial_registroc = models.IntegerField(null=True, default=2)
    tipo_registro = models.CharField(max_length=2, default='02')
    tipo_documento = models.CharField(max_length=1, default='2')
    cpf_cnpj = models.CharField(max_length=15, null=True)
    codigo_operacao = models.CharField(max_length=1, default='I')
    comprador = models.CharField(max_length=1, default='C')
    data_vencimento = models.DateField(null=True) #DDMMAAAA vencimento da CDA
    data_registro = models.DateField(null=True) #DDMMAAAA data da lavratura
    valor_debito = models.FloatField(null=True) #tamanho 13, dois decimais sem pontos
    contrato = models.CharField(max_length=30, null=True) #numero da CDA
    associado = models.CharField(max_length=8, null=True) #codigo do associado (PGM)
    natureza_inclusao = models.CharField(max_length=2, default='75')
    motivo_exclusao = models.CharField(max_length=3, null=True)
    cpf_cnpj_devedor = models.CharField(max_length=15, null=True) #quando se tratar de avalista ou fiador
    tipo_documento_devedor = models.CharField(max_length=1, null=True) #quando se tratar de avalista ou fiador
    notificar_email = models.CharField(max_length=1, default='N')
    codigo_retorno = models.CharField(max_length=10, null=True)
    sequencial_registro = models.IntegerField(null=True, default=2)
    remessacdl = models.ForeignKey(RemessaCDL, related_name='regcdl', on_delete=models.CASCADE)

    def __str__(self):
        return '%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s\n%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s\n' % \
               (
                   self.tipo_registroc,
                   self.praca_concessaoc,
                   self.nome_razaoc[0:44].ljust(45),
                   self.tipo_documentoc,
                   str(self.cpf_cnpjc).zfill(15),
                   repeat_to_length(' ', 20),
                   '00000000',  #self.data_nascimento.strftime('%d%m%Y'),
                   repeat_to_length(' ', 45),
                   self.enderecoc[0:49].ljust(50),
                   repeat_to_length('0', 5) if self.numeroc == None else str(self.numeroc[0:4]).zfill(5),
                   repeat_to_length(' ', 30) if self.complementoc == None else self.complementoc[0:29].ljust(30),
                   self.bairroc[0:24].ljust(25),
                   self.cepc,
                   self.cidadec[0:29].ljust(30),
                   'PI' if self.ufc == None else self.ufc,
                   '86' if self.fone_dddc == None else self.fone_dddc,
                   repeat_to_length(' ', 18),
                   repeat_to_length('0', 10) if self.fone_numeroc == None else str(self.fone_numeroc).zfill(10),
                   repeat_to_length(' ', 50) if self.emailc == None else self.emailc.ljust(50),
                   repeat_to_length(' ', 10) if self.codigo_retornoc == None else self.codigo_retornoc.ljust(10),
                   format(self.sequencial_registroc, '06d'),
                   '02',  # tipo de registro padrão 02
                   self.tipo_documento,
                   str(self.cpf_cnpj).zfill(15),
                   self.codigo_operacao,
                   self.comprador,
                   self.data_vencimento.strftime('%d%m%Y'),
                   self.data_registro.strftime('%d%m%Y'),
                   re.sub(r'[^0-9]', '', format(self.valor_debito, '.02f').zfill(14)),
                   self.contrato.rjust(30),
                   '00000000',  # format(self.associado).zfill(8)
                   '75',  # natureza_inclusao
                   ' 00' if self.motivo_exclusao == None else self.motivo_exclusao.ljust(3),
                   repeat_to_length(' ', 16),  # cpf avalista / tipo documento
                   'N',  # notificar por email ? N
                   repeat_to_length(' ', 265),
                   repeat_to_length(' ', 10) if self.codigo_retorno == None else self.codigo_retorno.ljust(10),
                   format(self.sequencial_registro, '06d')
               )


class TrailerCDL(models.Model):
    tipo_registro = models.IntegerField(null=True, default=99)
    total_registros = models.IntegerField(null=True)
    codigo_retorno = models.CharField(max_length=10, null=True)
    sequencial_registro = models.IntegerField(null=True)
    remessacdl = models.ForeignKey(RemessaCDL, related_name='trailer', on_delete=models.CASCADE)

    def __str__(self):
        return '%s%s%s%s%s\n' % \
               (
                   self.tipo_registro,
                   format(self.total_registros, '06d'),
                   repeat_to_length(' ', 366),
                   repeat_to_length(' ', 10) if self.codigo_retorno == None else self.codigo_retorno.ljust(10),
                   format(self.sequencial_registro, '06d')
               )


def repeat_to_length(string_to_expand, length):
    return (string_to_expand * (int(length/len(string_to_expand))+1))[:length]


class dadosProcessoTJ(models.Model):
    sistema = models.CharField(max_length=50, null=True)
    num_antigo = models.CharField(max_length=50, null=True)
    num_novo = models.CharField(max_length=50, null=True)
    classe = models.IntegerField(null=True, default=0)
    classe_descr = models.CharField(max_length=200, null=True)
    data_abertura = models.DateField(null=True)
    valor_acao = models.FloatField(default=0)
    status_atual = models.CharField(max_length=200, null=True)
    secretaria = models.CharField(max_length=200, null=True)
    vara = models.CharField(max_length=200, null=True)
    polo_ativo = models.TextField(null=True)
    polo_passivo = models.TextField(null=True)