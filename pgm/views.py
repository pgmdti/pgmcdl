from django.shortcuts import render
from django.http import JsonResponse
from django.http import  HttpResponse
from .forms import UploadFileForm
from .forms import UploadProcessosForm
from .forms import FilterOneForm
from .forms import BuscarForm
import pandas as pd
import numpy as np
from .models import dadosImob
from .models import RemessaCDL
from .models import RegistroCDL
from .models import TrailerCDL
from .models import dadosProcessoTJ
import locale
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import render
import re
import datetime
import pycep_correios as pycep
from pycep_correios.excecoes import ExcecaoPyCEPCorreios
from pycep_correios import HOMOLOGACAO, PRODUCAO
import time

locale.setlocale(locale.LC_NUMERIC, '')

# Create your views here.
def index(requests):
    return render(requests, 'pgm/index.html')

def upload(requests):
    if requests.method == 'POST':
        form = UploadFileForm(requests.POST, requests.FILES)
        if form.is_valid:
            f = requests.FILES['arquivo']
            handle_uploaded_file2(f)
            return success(requests)
    else:
        form = UploadFileForm()
    return render(requests, 'pgm/upload.html', {'form':form})


def uploadprocs(requests):
    if requests.method == 'POST':
        form = UploadProcessosForm(requests.POST, requests.FILES)
        if form.is_valid:
            f = requests.FILES['arquivo']
            handle_uploaded_procs_file(f)
            return success(requests)
    else:
        form = UploadProcessosForm()
    return render(requests, 'pgm/uploadprocs.html', {'form':form})


def tableall(requests):
    result = dadosImob.objects.all().order_by('contrib_nome')
    paginator = Paginator(result, 8)
    page = requests.GET.get('page')
    cdas = paginator.get_page(page)
    return render(requests, 'pgm/tableall.html', {'list': cdas})

def remessacdl(requests):
    cdlheader = RemessaCDL.objects.last()

    if cdlheader:
        if cdlheader.enviada:
           cdlheader = RemessaCDL()
           cdlheader.save()
           count = cdlheader.sequencial_registro
           trailer = TrailerCDL()
           trailer.remessacdl = cdlheader
        else:
           count = cdlheader.regcdl.count()*2+1
           trailer = cdlheader.trailer.all()[0]
    else:
        cdlheader = RemessaCDL()
        cdlheader.save()
        count = cdlheader.sequencial_registro
        trailer = TrailerCDL()
        trailer.remessacdl = cdlheader

    sql = 'select a.cda as id, a.cda, contrib_nome, cpf_cnpj, logr_tipo, logr_nome, logr_num, logr_compl, bairro_nome,' \
          ' cidade, uf, cep, fixo_ddd, fixo_num, email, total_cda, vencimento, documento_data from (select distinct cda' \
          ' as id, cda, contrib_nome, cpf_cnpj, logr_tipo, logr_nome, logr_num, logr_compl, bairro_nome, cidade, uf, cep,' \
          ' fixo_ddd, fixo_num, email from pgm_dadosimob where cda = %s) as a inner join (select cda, sum(debito_atualizado)' \
          ' as total_cda, max(vencimento) as vencimento, max(documento_data) as documento_data from pgm_dadosimob where cda = %s' \
          ' group by cda) as b on a.cda = b.cda'

    qtdcdas = 0
    listcdas = requests.GET.getlist('_cdas[]')
    i = 0
    while i < len(listcdas):
        qcda = dadosImob.objects.raw(sql, [listcdas[i], listcdas[i]])[0]
        endereco = qcda.logr_tipo + ' ' + qcda.logr_nome
        cpfcnpj = re.sub(r'[^0-9]','',qcda.cpf_cnpj)
        tipodoc = ('1' if len(cpfcnpj) > 11 else '2')

        verifycda = cdlheader.regcdl.filter(contrato=listcdas[i])
        flag = True
        if verifycda:
            flag = False

        i += 1

        if flag:
            qtdcdas += 1
            count += 1
            rcdl = RegistroCDL()

            rcdl.nome_razaoc = qcda.contrib_nome[0:45]
            rcdl.cpf_cnpjc = cpfcnpj
            rcdl.tipo_documentoc = tipodoc
            rcdl.enderecoc = endereco[0:50]
            rcdl.numeroc = (None if qcda.logr_num == None else qcda.logr_num)
            rcdl.complementoc = (None if qcda.logr_compl == None else qcda.logr_compl[0:30])
            rcdl.bairroc = qcda.bairro_nome[0:25]
            rcdl.cepc = ('64000000' if qcda.cep == None else qcda.cep)
            rcdl.cidadec = ('TERESINA' if qcda.cidade == None else qcda.cidade)
            rcdl.ufc = ('PI' if qcda.uf == None else qcda.uf[0:2])
            rcdl.fone_dddc = (None if qcda.fixo_ddd == None else qcda.fixo_ddd[0:2])
            rcdl.fone_numeroc = (None if qcda.fixo_num == None else qcda.fixo_num[0:10])
            rcdl.emailc = (None if qcda.email == None else qcda.email[0:50])
            rcdl.sequencial_registroc = count
            count += 1
            rcdl.tipo_documento = tipodoc
            rcdl.cpf_cnpj = cpfcnpj
            rcdl.codigo_operacao = 'I'
            rcdl.comprador = 'C'
            rcdl.data_vencimento = qcda.vencimento
            rcdl.data_registro = qcda.documento_data
            rcdl.valor_debito = format(qcda.total_cda, '.02f')
            rcdl.contrato = qcda.cda
            rcdl.sequencial_registro = count
            rcdl.remessacdl = cdlheader
            rcdl.save()

    count += 1
    trailer.tipo_registro = 99
    trailer.total_registros = count
    trailer.sequencial_registro = count
    trailer.save()

    mensagem = format(qtdcdas, '04d') + ' CDAs adicionadas a remessa nº ' + format(cdlheader.remessa_id, '06d')

    return JsonResponse({'message':mensagem})


def cdadetail(requests, idcda):
    sql = "select a.cda as id, a.cda, a.contrib_id, a.cpf_cnpj, a.contrib_nome, a.fixo_ddd, a.fixo_num, a.cel_ddd, a.cel_num, a.email, a.cep," \
          " a.logr_tipo, a.logr_nome, a.logr_num, a.logr_compl, a.bairro_tipo, a.bairro_nome, a.cidade, a.uf, a.receita_tipo, a.parcela_situa," \
          " a.inscricao_num, a.inscricao_tipo, a.natureza_credito, a.tipo_doc_base_insc, a.documento_data, a.processo_num, a.parcela_num," \
          " a.processo_data, a.despacho_data, a.documento_num, a.debito_valor, a.debito_atualizacao, a.debito_juros, a.debito_multa," \
          " a.debito_desconto, a.debito_atualizado, a.lavratura_data, a.lavratura_hora, a.lavratura_usuario, a.vencimento, a.debito_dia," \
          " a.debito_mes, a.debito_ano, a.parcela_situa, total_debito as total_cda from pgm_dadosimob a inner join (select cda, debito_ano," \
          " sum(debito_atualizado) as total_debito from pgm_dadosimob where cda = %s group by cda, debito_ano order by debito_ano)" \
          " as b on a.cda = b.cda and a.cda = %s and a.debito_ano = b.debito_ano order by a.debito_ano, parcela_num"
    cda = dadosImob.objects.raw(sql, [idcda, idcda])
    sql = "select cda as id, cda, sum(debito_atualizado) as total_cda from pgm_dadosimob where cda = %s group by cda"
    totalcda = dadosImob.objects.raw(sql, [idcda])
    return render(requests, 'pgm/detail.html', {'cda': cda, 'totalcda': totalcda})

def search(requests):
    if requests.method == 'POST':
        form = BuscarForm(requests.POST, requests.FILES)
        if form.is_valid:
            cpf_cnpj = form['cpf_cnpj'].value()
            sql = "select distinct a.cda as id, a.cda, receita_tipo, parcela_situa, total_cda, cpf_cnpj, processo_num, processo_data, contrib_nome," \
                  " ano as debito_ano, inscricao_num, inscricao_tipo, parcelas from" \
                  " (select cda, sum(debito_atualizado) as total_cda, min(debito_ano) as ano, count(parcela_num) as parcelas from pgm_dadosimob" \
                  " group by cda order by cda) as a inner join (select cda, cda_ant, processo_num, receita_tipo, contrib_id, cpf_cnpj, inscricao_num, inscricao_tipo," \
                  " contrib_nome, documento_num, documento_data, processo_data, debito_atualizado, parcela_num, parcela_situa, vencimento" \
                  " from pgm_dadosimob where cpf_cnpj = %s) as b on a.cda = b.cda"
            result = dadosImob.objects.raw(sql, [cpf_cnpj])
            return render(requests, 'pgm/table2.html', {'list': result})
    else:
        #RemessaCDL.objects.all().delete()
        #RemessaCDL.objects.raw('ALTER SEQUENCE pgm_remessacdl_remessa_id_seq RESTART WITH 1')
        form = BuscarForm()
    return render(requests, 'pgm/search.html', {'form':form})


def cdascontribuinte(requests, doc):
    sql = "select distinct a.cda as id, a.cda, receita_tipo, parcela_situa, total_cda, cpf_cnpj, processo_num, processo_data, contrib_nome, ano as debito_ano, parcelas from" \
          " (select cda, sum(debito_atualizado) as total_cda, min(debito_ano) as ano, count(parcela_num) as parcelas from pgm_dadosimob where contrib_id = %s" \
          " group by cda order by cda) as a inner join (select cda, cda_ant, processo_num, receita_tipo, contrib_id, cpf_cnpj," \
          " contrib_nome, documento_num, documento_data, processo_data, debito_atualizado, parcela_num, parcela_situa, vencimento" \
          " from pgm_dadosimob where contrib_id = %s) as b on a.cda = b.cda"
    result = dadosImob.objects.raw(sql, [doc, doc])
    return render(requests, 'pgm/table2.html', {'list': result})


def listaremessas(requests):
    result = RemessaCDL.objects.all().order_by('-remessa_id')
    paginator = Paginator(result, 8)
    page = requests.GET.get('page')
    remessas = paginator.get_page(page)
    return render(requests, 'pgm/remessas_all.html', {'list': remessas})

def downloadremessa(requests, idremessa):
    response = HttpResponse()
    remessa = RemessaCDL.objects.get(pk=idremessa)
    remessa.enviada = True
    remessa.save()
    datarem = datetime.datetime.now().strftime('%Y%m%d')
    horarem = datetime.datetime.now().strftime('%H%M')
    namefile = '9999_99999999_'+datarem+'_'+horarem+'.txt'
    response['Content-Disposition'] = 'attachment; filename="'+namefile+'"'

    response.write(remessa)
    for reg in remessa.regcdl.all().order_by('sequencial_registro'):
        response.write(reg)

    for tr in remessa.trailer.all():
        response.write(tr)

    return response


def filterone(requests):
    if requests.method == 'POST':
        form = FilterOneForm(requests.POST, requests.FILES)
        if form.is_valid:
            dt = form['vencimento_de'].value()
            dataini = dt[6:10]+'-'+dt[3:5]+'-'+dt[0:2]
            dt = form['vencimento_ate'].value()
            datafim = dt[6:10] + '-' + dt[3:5] + '-' + dt[0:2]
            cod_rec = form['codigo_receita'].value()
            vl = form['valor_de'].value()
            vl = vl.replace('.','')
            valorini = vl.replace(',', '.')
            vl = form['valor_ate'].value()
            vl = vl.replace('.','')
            valorfim = vl.replace(',', '.')
            ajuizado = form['ajuizado'].value()
            queryajuizado = 'not processo_num is null'
            if ajuizado == 'nao':
                queryajuizado = 'processo_num is null'

            sql = " select a.id, a.cda, a.receita_tipo, a.parcela_situa, a.total_cda, a.cpf_cnpj, a.contrib_nome, a.debito_ano, a.parcelas, a.inscricao_num, a.inscricao_tipo from" \
                  " (select a.cda as id, a.cda, receita_tipo, parcela_situa, total_cda, cpf_cnpj, contrib_nome, ano as debito_ano, parcelas, inscricao_num, inscricao_tipo from" \
                  " (select r.cda, total_cda, parcelas, ano from (select cda, sum(debito_atualizado) as total_cda, count(parcela_num) as parcelas" \
                  " from pgm_dadosimob group by cda having sum(debito_atualizado) between %s and %s) as r inner join" \
                  " (select cda, min(debito_ano) as ano from pgm_dadosimob group by cda) as k on r.cda = k.cda) as a inner join" \
                  " (select distinct cda, cda_ant, processo_num, receita_tipo, contrib_id, cpf_cnpj, contrib_nome, processo_data, parcela_situa" \
                  " ,inscricao_num, inscricao_tipo from pgm_dadosimob where vencimento between %s and %s and receita_tipo = %s and not cpf_cnpj is null" \
                  " and not cidade is null and parcela_situa = 'Aberta' and "+queryajuizado+") as b on a.cda = b.cda order by contrib_nome) as a left join pgm_registrocdl as b" \
                  " on a.cda = b.contrato where b.contrato is null"
            result = dadosImob.objects.raw(sql, [valorini, valorfim, dataini, datafim, cod_rec])
            return render(requests, 'pgm/table1.html', {'list': result})
    else:
        form = FilterOneForm()
    return render(requests, 'pgm/filter1.html', {'form':form})



def cdasantigas1(requests):
    sql = "select a.cda_ant as id, a.cda_ant, receita_tipo, parcela_situa, total_cda, cpf_cnpj, contrib_nome, ano as debito_ano, parcelas," \
          " inscricao_num, inscricao_tipo, b.processo_num from (select r.cda_ant, total_cda, parcelas, ano from (select cda_ant," \
          " sum(debito_atualizado) as total_cda, count(parcela_num) as parcelas from pgm_dadosimob group by cda_ant) as r inner join" \
          " (select cda_ant, min(debito_ano) as ano from pgm_dadosimob group by cda_ant) as k on r.cda_ant = k.cda_ant) as a inner join" \
          " (select distinct cda_ant, processo_num, receita_tipo, contrib_id, cpf_cnpj, contrib_nome, processo_data, parcela_situa," \
          " inscricao_num, inscricao_tipo from pgm_dadosimob where not cda_ant is null and cda_ant like %s and parcela_situa = 'Aberta') as b" \
          " on a.cda_ant = b.cda_ant order by contrib_nome"
    result = dadosImob.objects.raw(sql, ['0%'])
    return render(requests, 'pgm/table3.html', {'list': result})


def cdasantigas2(requests):
    sql = "select a.cda_ant as id, a.cda_ant, receita_tipo, parcela_situa, total_cda, cpf_cnpj, contrib_nome, parcelas, inscricao_num, inscricao_tipo," \
          " b.processo_num, b.parcela_num, b.debito_ano, b.debito_atualizado, b.vencimento from (select r.cda_ant, total_cda, parcelas, ano from (select cda_ant," \
          " sum(debito_atualizado) as total_cda, count(parcela_num) as parcelas from pgm_dadosimob group by cda_ant) as r inner join (select cda_ant," \
          " min(debito_ano) as ano from pgm_dadosimob group by cda_ant) as k on r.cda_ant = k.cda_ant) as a inner join (select cda_ant, processo_num," \
          " receita_tipo, contrib_id, cpf_cnpj, contrib_nome, processo_data, parcela_situa ,inscricao_num, inscricao_tipo, parcela_num, debito_ano," \
          " debito_atualizado, vencimento from pgm_dadosimob where not cda_ant is null and cda_ant like %s and parcela_situa = 'Aberta') as b on a.cda_ant = b.cda_ant" \
          " order by contrib_nome, a.cda_ant, b.debito_ano, b.parcela_num"
    result = dadosImob.objects.raw(sql, ['0%'])
    return render(requests, 'pgm/table4.html', {'list': result})

def validacep(requests):
    response = HttpResponse()
    namefile = 'cep_invalido_siat.csv'
    response['Content-Disposition'] = 'attachment; filename="'+namefile+'"'

    sql_cep_test = "select distinct contrib_id as id, contrib_id, contrib_nome, cpf_cnpj, cep, logr_tipo," \
                   " logr_nome, logr_num, logr_compl, bairro_tipo, bairro_nome, cidade, uf" \
                   " from pgm_dadosimob where not cep isnull and not cpf_cnpj isnull" \
                   " and not cidade isnull and not uf isnull" \
                   " and cep <> '64000000'"

    result = dadosImob.objects.raw(sql_cep_test)

    for r in result:
       try:
           pycep.consultar_cep(r.cep, ambiente=PRODUCAO)
       except ExcecaoPyCEPCorreios as exc:
            print(exc.message + " :::: " + r.cep)
            response.write(r)

    return response

def event(requests):
    print(requests)
    return JsonResponse({'status':'true', 'message':'worked'})


def success(requests):
    return render(requests, 'success/success.html')


def handle_uploaded_procs_file(f):
    df1 = pd.read_csv(f, sep=';', error_bad_lines=False, index_col=False, engine='c', header=None, skiprows=1,
                      dtype=object)
    df = df1.where((pd.notnull(df1)), None)
    df[5] = pd.to_datetime(df[5], infer_datetime_format=True, errors='ignore')
    df[6] = df[6].str.strip()
    df[6] = pd.to_numeric(df[6].str.replace(',', '.').fillna('0'), errors='ignore')
    df[6] = df[6].astype(np.float)

    dadosProcessoTJ.objects.all().delete()

    for row in df.itertuples():
        dados = dadosProcessoTJ()
        dados.sistema = row[1]
        dados.num_antigo = row[2]
        dados.num_novo = row[3]
        dados.classe = row[4]
        dados.classe_descr = row[5]
        dados.data_abertura = row[6].date()
        dados.valor_acao = row[7]
        dados.status_atual = row[8]
        dados.secretaria = row[9]
        dados.vara = row[10]
        dados.polo_ativo = row[11]
        dados.polo_passivo = row[12]
        dados.save()
    del df


def handle_uploaded_file(f):

    df1 = pd.read_csv(f, sep=';', error_bad_lines=False, index_col=False, engine='c', header=None, skiprows=1, dtype=object)

    df = df1.where((pd.notnull(df1)), None)

    df[24] = pd.to_datetime(df[24], infer_datetime_format=True, errors='ignore')
    df[26] = pd.to_datetime(df[26], infer_datetime_format=True, errors='ignore')
    df[27] = pd.to_datetime(df[27], infer_datetime_format=True, errors='ignore')
    df[35] = pd.to_datetime(df[35], infer_datetime_format=True, errors='ignore')
    df[38] = pd.to_datetime(df[38], infer_datetime_format=True, errors='ignore')
    df[45] = pd.to_datetime(df[45], infer_datetime_format=True, errors='ignore')
    df[47] = pd.to_datetime(df[47], infer_datetime_format=True, errors='ignore')
    df[48] = pd.to_datetime(df[48], infer_datetime_format=True, errors='ignore')

    df[29] = df[29].str.strip()
    df[30] = df[30].str.strip()
    df[31] = df[31].str.strip()
    df[32] = df[32].str.strip()
    df[33] = df[33].infer_objects()
    df[34] = df[34].str.strip()

    df[29] = pd.to_numeric(df[29].str.replace(',', '.').fillna('0'), errors='ignore')
    df[30] = pd.to_numeric(df[30].str.replace(',', '.').fillna('0'), errors='ignore')
    df[31] = pd.to_numeric(df[31].str.replace(',', '.').fillna('0'), errors='ignore')
    df[32] = pd.to_numeric(df[32].str.replace(',', '.').fillna('0'), errors='ignore')
    df[34] = pd.to_numeric(df[34].str.replace(',', '.').fillna('0'), errors='ignore')

    df[29] = df[29].astype(np.float)
    df[30] = df[30].astype(np.float)
    df[31] = df[31].astype(np.float)
    df[32] = df[32].astype(np.float)
    df[33] = df[33].astype(np.float)
    df[34] = df[34].astype(np.float)

    dadosImob.objects.all().delete()
    #dadosImob.objects.raw("ALTER SEQUENCE pgm_dadosimob_id_seq RESTART WITH 1")

    for row in df.itertuples():
        dados = dadosImob()
        dados.cda = row[1]
        dados.cda_ant = row[2]
        dados.contrib_id = row[3]
        dados.cpf_cnpj = row[4]
        dados.contrib_nome = row[5]
        dados.fixo_ddd = row[6]
        dados.fixo_num = row[7]
        dados.cel_ddd = row[8]
        dados.cel_num = row[9]
        dados.email = row[10]
        dados.cep = row[11]
        dados.logr_tipo = row[12]
        dados.logr_nome = row[13]
        dados.logr_num = row[14]
        dados.logr_compl = row[15]
        dados.bairro_tipo = row[16]
        dados.bairro_nome = row[17]
        dados.cidade = row[18]
        dados.uf = row[19]
        dados.receita_tipo = row[20]
        dados.inscricao_num = row[21]
        dados.inscricao_tipo = row[22]
        dados.natureza_credito = row[23]
        dados.tipo_doc_base_insc = row[24]
        if isinstance(row[25], pd.datetime) and row[25] is not pd.NaT:
            dados.documento_data = row[25].date()
        dados.processo_num = row[26]
        if isinstance(row[27], pd.datetime) and row[27] is not pd.NaT:
            dados.processo_data = row[27].date()
        if isinstance(row[28], pd.datetime) and row[28] is not pd.NaT:
            dados.despacho_data = row[28].date()
        dados.documento_num = row[29]
        dados.debito_valor = row[30]
        dados.debito_atualizacao = row[31]
        dados.debito_juros = row[32]
        dados.debito_multa = row[33]
        dados.debito_desconto = row[34]
        dados.debito_atualizado = row[35]
        if isinstance(row[36], pd.datetime) and row[36] is not pd.NaT:
            dados.lavratura_data = row[36].date()
        dados.lavratura_hora = row[37]
        dados.lavratura_usuario = row[38]
        if isinstance(row[39], pd.datetime) and row[39] is not pd.NaT:
            dados.vencimento = row[39].date()
        dados.debito_dia = row[40]
        dados.debito_mes = row[41]
        dados.parcela_num = row[42]
        dados.debito_ano = row[43]
        dados.parcela_situa = row[44]
        dados.prescricao_causa_inter = row[45]
        if isinstance(row[46], pd.datetime) and row[46] is not pd.NaT:
            dados.prescricao_data_inter = row[46].date()
        dados.prescricao_mot_susp_prazo = row[47]
        if isinstance(row[48], pd.datetime) and row[48] is not pd.NaT:
            dados.prescricao_mot_data_ini = row[48].date()
        if isinstance(row[49], pd.datetime) and row[49] is not pd.NaT:
            dados.prescricao_mot_data_fim = row[49].date()
        dados.fundamentacao_legal = row[50]
        dados.logr_tipo_el = row[51]
        dados.logr_nome_el = row[52]
        dados.logr_num_el = row[53]
        dados.logr_compl_el = row[54]
        dados.bairro_tipo_el = row[55]
        dados.bairro_nome_el = row[56]
        dados.cep_el = row[57]
        dados.cidade_el = row[58]
        dados.uf_el = row[59]
        dados.logr_tipo_ee = row[60]
        dados.logr_nome_ee = row[61]
        dados.logr_num_ee = row[62]
        dados.logr_compl_ee = row[63]
        dados.bairro_tipo_ee = row[64]
        dados.bairro_nome_ee = row[65]
        dados.cep_ee = row[66]
        dados.cidade_ee = row[67]
        dados.uf_ee = row[68]

        dados.save()
    del df



def handle_uploaded_file2(f):

    dateparse = lambda dates: [pd.datetime.strptime(d, '%d/%m/%Y') for d in dates]

    df1 = pd.read_csv(f, sep=';', parse_dates=True, date_parser=dateparse, error_bad_lines=False, index_col=False, engine='c', header=None, skiprows=1, dtype=object)

    df = df1.where((pd.notnull(df1)), None)

    df[15] = df[15].str.strip()
    df[16] = df[16].str.strip()
    df[17] = df[17].str.strip()
    df[18] = df[18].str.strip()
    df[19] = df[19].infer_objects()
    df[20] = df[20].str.strip()

    df[15] = pd.to_numeric(df[15].str.replace(',', '.').fillna('0'), errors='ignore')
    df[16] = pd.to_numeric(df[16].str.replace(',', '.').fillna('0'), errors='ignore')
    df[17] = pd.to_numeric(df[17].str.replace(',', '.').fillna('0'), errors='ignore')
    df[18] = pd.to_numeric(df[18].str.replace(',', '.').fillna('0'), errors='ignore')
    df[19] = pd.to_numeric(df[19].str.replace(',', '.').fillna('0'), errors='ignore')
    df[20] = pd.to_numeric(df[20].str.replace(',', '.').fillna('0'), errors='ignore')

    df[15] = df[15].astype(np.float)
    df[16] = df[16].astype(np.float)
    df[17] = df[17].astype(np.float)
    df[18] = df[18].astype(np.float)
    df[19] = df[19].astype(np.float)
    df[20] = df[20].astype(np.float)

    dadosImob.objects.all().delete()

    for row in df.itertuples():
        dados = dadosImob()
        dados.cda = row[1]
        dados.cda_ant = row[2]
        dados.contrib_id = row[3]
        dados.cpf_cnpj = row[4]
        dados.contrib_nome = row[5]
        dados.receita_tipo = row[6]
        dados.inscricao_num = row[7]
        dados.inscricao_tipo = row[8]
        dados.natureza_credito = row[9]
        dados.tipo_doc_base_insc = row[10]
        if row[11] is not None:
            date_obj = datetime.datetime.strptime(row[11], '%d/%m/%Y')
            dados.documento_data = date_obj.date()
        dados.processo_num = row[12]
        if row[13] is not None:
            date_obj = datetime.datetime.strptime(row[13], '%d/%m/%Y')
            dados.processo_data = date_obj.date()
        if row[14] is not None:
            date_obj = datetime.datetime.strptime(row[14], '%d/%m/%Y')
            dados.despacho_data = date_obj.date()
        dados.documento_num = row[15]
        dados.debito_valor = row[16]
        dados.debito_atualizacao = row[17]
        dados.debito_juros = row[18]
        dados.debito_multa = row[19]
        dados.debito_desconto = row[20]
        dados.debito_atualizado = row[21]
        if row[22] is not None:
            date_obj = datetime.datetime.strptime(row[22], '%d/%m/%Y')
            dados.lavratura_data = date_obj.date()
        dados.lavratura_hora = row[23]
        dados.lavratura_usuario = row[24]
        if row[25] is not None:
            date_obj = datetime.datetime.strptime(row[25], '%d/%m/%Y %H:%M:%S')
            dados.vencimento = date_obj.date()
        dados.debito_dia = row[26]
        dados.debito_mes = row[27]
        dados.parcela_num = row[28]
        dados.debito_ano = row[29]
        dados.parcela_situa = row[30]
        dados.prescricao_causa_inter = row[31]
        if row[32] is not None:
            date_obj = datetime.datetime.strptime(row[32], '%d/%m/%Y')
            dados.prescricao_data_inter = date_obj.date()
        dados.prescricao_mot_susp_prazo = row[33]
        if row[34] is not None:
            date_obj = datetime.datetime.strptime(row[34], '%d/%m/%Y')
            dados.prescricao_mot_data_ini = date_obj.date()
        if row[35] is not None:
            date_obj = datetime.datetime.strptime(row[35], '%d/%m/%Y')
            dados.prescricao_mot_data_fim = date_obj.date()
        dados.fundamentacao_legal = row[36]
        #dados.logr_nome_el = row[37]

        dados.save()

    del df

