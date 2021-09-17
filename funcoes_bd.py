from flask import Flask, make_response, request, render_template, redirect, send_from_directory
from wtforms import Form, BooleanField, StringField, PasswordField, validators,IntegerField,SubmitField,HiddenField
from contextlib import closing
import mariadb
import os
import werkzeug
import sys
from datetime import datetime
import abc


###############################################
#### Funções auxiliares de banco de dados. ####
###############################################

# Converte uma linha em um dicionário.
def row_to_dict(description, row):
    if row is None: return None
    d = {}
    for i in range(0, len(row)):
        d[description[i][0]] = row[i]
    return d

# Converte uma lista de linhas em um lista de dicionários.
def rows_to_dict(description, rows):
    result = []
    for row in rows:
        result.append(row_to_dict(description, row))
    return result

####################################
#### Definições básicas de DAO. ####
####################



def conectar():
    
    try:
        conn = mariadb.connect(
        user="lita9zcr0bicj9ug",
        password="wg9bdt04yfw935yb",
        host="uyu7j8yohcwo35j3.cbetxkdyhwsb.us-east-1.rds.amazonaws.com",
        port=3306,
        database="yp6j4onahooac5aj"

        )

    except mariadb.Error:
        print(f"Error connecting to MariaDB Platform: {mariadb.Error}")
        sys.exit(1)
    return conn




############################ TABELA ESTADO ##########################################        
def db_criar_estado(nome_estado):
    with closing(conectar()) as con, closing(con.cursor()) as cur:
        cur.execute("INSERT INTO TB_ESTADO (NOME_ESTADO) VALUES (?)", [nome_estado])
        id_estado = cur.lastrowid
        con.commit()
        return {'id_estado': id_estado , 'nome_estado':nome_estado}

def db_listar_estados():
    with closing(conectar()) as con, closing(con.cursor()) as cur:
        cur.execute("SELECT * FROM TB_ESTADO")
        return rows_to_dict(cur.description, cur.fetchall())

def db_localizar_estado(id_estado):
    with closing(conectar()) as con, closing(con.cursor()) as cur:
        cur.execute("SELECT * FROM TB_ESTADO WHERE ID_ESTADO = (?)", [id_estado])
        return rows_to_dict(cur.description, cur.fetchall())

def db_atualizar_nome_estado(id_estado,nome_estado):
    with closing(conectar()) as con, closing(con.cursor()) as cur:
        cur.execute("UPDATE TB_ESTADO SET NOME_ESTADO = (?) WHERE ID_ESTADO = (?) ", [nome_estado,id_estado])
        con.commit()
        return {'id_estado': id_estado , 'nome_estado':nome_estado}

def db_delete_estado(id_estado):
    with closing(conectar()) as con, closing(con.cursor()) as cur:
        cur.execute("DELETE FROM TB_ESTADO WHERE ID_ESTADO = (?) ", [id_estado])
        con.commit()
        return {"message":"Estado excluído"}

############################ TABELA CIDADE ########################################## 
def db_criar_cidade(id_estado,nome_cidade):
    with closing(conectar()) as con, closing(con.cursor()) as cur:
        cur.execute("INSERT INTO TB_CIDADE (NOME_CIDADE,ID_ESTADO) VALUES (?,?)", [nome_cidade,id_estado])
        id_cidade = cur.lastrowid
        con.commit()
        return {'id_cidade': id_cidade , 'nome_cidade':nome_cidade,'id_estado':id_estado}


def db_listar_cidades():
    with closing(conectar()) as con, closing(con.cursor()) as cur:
        cur.execute("SELECT * FROM TB_CIDADE")
        return rows_to_dict(cur.description, cur.fetchall())

def db_listar_cidades_por_estado(id_estado):
    with closing(conectar()) as con, closing(con.cursor()) as cur:
        cur.execute(f'''SELECT ci.ID_CIDADE, ci.NOME_CIDADE, es.NOME_ESTADO,es.ID_ESTADO FROM TB_CIDADE ci INNER JOIN TB_ESTADO es 
                        ON  es.ID_ESTADO = ci.ID_ESTADO WHERE es.ID_ESTADO = (?) ''',[id_estado])
        return rows_to_dict(cur.description, cur.fetchall())

def db_localizar_cidade_de_estado_por_nome(id_estado, nome_cidade):
    with closing(conectar()) as con, closing(con.cursor()) as cur:
        sql=f'''SELECT ci.ID_CIDADE, ci.NOME_CIDADE, es.NOME_ESTADO,es.ID_ESTADO FROM TB_CIDADE ci INNER JOIN TB_ESTADO es 
            ON  es.ID_ESTADO = ci.ID_ESTADO WHERE es.ID_ESTADO = {id_estado} AND ci.NOME_CIDADE LIKE '%{nome_cidade}%' ORDER BY ci.NOME_CIDADE LIMIT 20; '''
        params=(id_estado,nome_cidade)
        cur.execute(sql)
        return rows_to_dict(cur.description, cur.fetchall())


def db_localizar_cidade(id_cidade):
    with closing(conectar()) as con, closing(con.cursor()) as cur:
        cur.execute('''SELECT ci.ID_CIDADE, ci.NOME_CIDADE, es.NOME_ESTADO,es.ID_ESTADO FROM TB_CIDADE ci INNER JOIN TB_ESTADO es 
        ON  es.ID_ESTADO = ci.ID_ESTADO WHERE ci.ID_CIDADE = (?)''' , [id_cidade])
        return rows_to_dict(cur.description, cur.fetchall())

def db_atualizar_nome_cidade(id_cidade,nome_cidade):
    with closing(conectar()) as con, closing(con.cursor()) as cur:
        cur.execute("UPDATE TB_CIDADE SET NOME_CIDADE = (?) WHERE ID_CIDADE = (?) ", [nome_cidade,id_cidade])
        con.commit()
        return {'id_cidade': id_cidade , 'nome_cidade':nome_cidade}

def db_delete_cidade(id_cidade):
    with closing(conectar()) as con, closing(con.cursor()) as cur:
        cur.execute("DELETE FROM TB_CIDADE WHERE ID_CIDADE = (?) ", [id_cidade])
        con.commit()
        return {"message":"Cidade excluida"}

############################ TABELA ENDEREÇO ########################################## 

def db_criar_endereco(rua,numero,bairro,complemento,id_cidade):
    with closing(conectar()) as con, closing(con.cursor()) as cur:
        cur.execute("INSERT INTO TB_ENDERECO (RUA,NUMERO,BAIRRO,COMPLEMENTO,ID_CIDADE) VALUES (?,?,?,?,?)", [rua,numero,bairro,complemento,id_cidade])
        id_endereco = cur.lastrowid
        con.commit()
        return {'id_endereco': id_endereco , 'rua':rua,'numero':numero,'bairro':bairro, 'complemento':complemento,'id_cidade':id_cidade}

def db_listar_enderecos():
    with closing(conectar()) as con, closing(con.cursor()) as cur:
        cur.execute("SELECT * FROM TB_ENDERECO")
        return rows_to_dict(cur.description, cur.fetchall())

def db_localizar_endereco(id_endereco):
    with closing(conectar()) as con, closing(con.cursor()) as cur:
        cur.execute('''SELECT en.ID_ENDERECO, en.RUA, en.NUMERO, en.BAIRRO, en.COMPLEMENTO, ci.NOME_CIDADE FROM TB_ENDERECO en  INNER JOIN TB_CIDADE ci 
        ON  en.ID_CIDADE = ci.ID_CIDADE WHERE en.ID_ENDERECO = (?)''' , [id_endereco])
        return rows_to_dict(cur.description, cur.fetchall())

def db_atualizar_endereco(id_endereco, rua,numero,bairro,complemento):
    with closing(conectar()) as con, closing(con.cursor()) as cur:
        cur.execute("UPDATE TB_ENDERECO SET RUA = (?), NUMERO = (?), BAIRRO = (?), COMPLEMENTO = (?) WHERE ID_ENDERECO = (?) ", [rua,numero,bairro,complemento,id_endereco])
        con.commit()
        return {'id_endereco': id_endereco , 'rua':rua,'numero':numero,'bairro':bairro, 'complemento':complemento}

def db_delete_endereco(id_endereco):
    with closing(conectar()) as con, closing(con.cursor()) as cur:
        cur.execute("DELETE FROM TB_ENDERECO WHERE ID_ENDERECO = (?) ", [id_endereco])
        con.commit()
        return {"message":"Endereço excluido"}


############################ TABELA CLIENTE ########################################## 


def db_criar_cliente(cpf, nome, dt_nasc, email,senha,id_endereco,chave_pix):
    with closing(conectar()) as con, closing(con.cursor()) as cur:
        cur.execute("INSERT INTO TB_CLIENTE (CPF,NOME,DT_NASC,EMAIL,SENHA,ID_ENDERECO, CHAVE_PIX) VALUES (?,?,?,?,?,?,?)", [cpf, nome, dt_nasc, email,senha,id_endereco,chave_pix])
        id_conta = cur.lastrowid
        con.commit()
        return {'id_conta':id_conta, 'cpf':cpf, 'nome':nome, 'dt_nasc':dt_nasc, 'email':email,'senha':senha,'id_endereco':id_endereco, 'chave_pix':chave_pix}

def db_listar_clientes():
    with closing(conectar()) as con, closing(con.cursor()) as cur:
        cur.execute("SELECT * FROM TB_CLIENTE")
        return rows_to_dict(cur.description, cur.fetchall())

def db_localizar_cliente(id_conta):
    with closing(conectar()) as con, closing(con.cursor()) as cur:
        cur.execute('''SELECT cl.ID_CONTA, cl.CPF, cl.NOME, cl.DT_NASC, cl.EMAIL, cl.SENHA, en.RUA, en.NUMERO FROM TB_CLIENTE cl  INNER JOIN TB_ENDERECO en 
        ON  cl.ID_ENDERECO = en.ID_ENDERECO WHERE cl.ID_CONTA = (?)''' , [id_conta])
        return rows_to_dict(cur.description, cur.fetchall())


def db_atualizar_cliente(id_conta, nome, dt_nasc, email,chave_pix):
    with closing(conectar()) as con, closing(con.cursor()) as cur:
        cur.execute("UPDATE TB_CLIENTE SET NOME = (?), DT_NASC = (?), EMAIL= (?), CHAVE_PIX = (?) WHERE ID_CONTA = (?) ", [nome, dt_nasc, email,chave_pix,id_conta])
        con.commit()
        return {'id_conta':id_conta,'nome':nome, 'dt_nasc':dt_nasc, 'email':email, 'chave_pix':chave_pix}

def db_atualizar_cpf_cliente(id_conta,cpf):
    with closing(conectar()) as con, closing(con.cursor()) as cur:
        cur.execute("UPDATE TB_CLIENTE SET CPF = (?) WHERE ID_CONTA = (?) ", [cpf,id_conta])
        con.commit()
        return {'id_conta':id_conta,'cpf':cpf}

def db_atualizar_senha_cliente(id_conta,senha):
    with closing(conectar()) as con, closing(con.cursor()) as cur:
        cur.execute("UPDATE TB_CLIENTE SET SENHA = (?) WHERE ID_CONTA = (?) ", [senha,id_conta])
        con.commit()
        return {'id_conta':id_conta, "message":"Senha alterada com sucesso"}

def db_delete_cliente(id_cliente):
    with closing(conectar()) as con, closing(con.cursor()) as cur:
        cur.execute("DELETE FROM TB_CLIENTE WHERE ID_CLIENTE = (?) ", [id_cliente])
        con.commit()
        return {"message":"Cliente excluído"}


############################ TABELA DADOS_BANCARIOS ########################################## 

def db_criar_dados_bancarios(conta,instituicao,agencia,id_conta):
    with closing(conectar()) as con, closing(con.cursor()) as cur:
        cur.execute("INSERT INTO TB_DADOS_BANCARIOS(CONTA,INSTITUICAO,AGENCIA,ID_CONTA) VALUES (?,?,?,?)", [conta,instituicao,agencia,id_conta])
        con.commit()
        return {'conta':conta,'instituicao':instituicao,'agencia':agencia,'id_conta':id_conta}

def db_listar_dados_bancarios():
    with closing(conectar()) as con, closing(con.cursor()) as cur:
        cur.execute("SELECT * FROM TB_DADOS_BANCARIOS")
        return rows_to_dict(cur.description, cur.fetchall())



############################ TABELA FUNCIONARIO ########################################## 

def db_criar_funcionario(cpf, nome, email,senha,salario,id_endereco,cpf_supervisor):
    with closing(conectar()) as con, closing(con.cursor()) as cur:
        cur.execute("INSERT INTO TB_FUNCIONARIO (CPF,NOME,EMAIL,SENHA,SALARIO,ID_ENDERECO,CPF_SUPERVISOR) VALUES (?,?,?,?,?,?,?)", [cpf, nome, email, senha,salario,id_endereco,cpf_supervisor])
        con.commit()
        return {'cpf':cpf, 'nome':nome,'email':email,'senha':senha,'salario':salario,'id_endereco':id_endereco,'cpf_supervisor':cpf_supervisor}

def db_listar_funcionarios():
    with closing(conectar()) as con, closing(con.cursor()) as cur:
        cur.execute("SELECT * FROM TB_FUNCIONARIO")
        return rows_to_dict(cur.description, cur.fetchall())




############################ TABELA MOVIMENTACAO ########################################## 

##################### CLASSE ABSTRATA DE TIPO DE MOVIMENTACAO #####################
class TipoMovimentacao(metaclass=abc.ABCMeta):
    def __init__(self):
        self.nome_movimentacao = None
        self.id_mov = None

    def get_id_mov(self):
        return self.id_mov

    def set_id_mov(self,id_mov):
        self.id_mov = id_mov
        return

    def get_nome_mov(self):
        return self.nome_movimentacao

    def set_nome_mov(self,nome_mov):
        self.nome_movimentacao = nome_mov
        return
    @abc.abstractmethod
    def cria_mov_produto(self,tipo_mov,qtd_produto,cpf_funcionario,id_produto=None, nome_produto=None,descricao=None,valor=None):
        pass

##################### CLASSE MOVIMENTACAO #####################
class Movimentacao(object):

    def db_criar_mov(self,qtd_produto,horario,tipo_mov,cpf_funcionario,id_produto):
            with closing(conectar()) as con, closing(con.cursor()) as cur:
                cur.execute("INSERT INTO TB_MOV (QTD_PRODUTO,HORARIO,TIPO_MOV,CPF_FUNCIONARIO, ID_PRODUTO) VALUES (?,?,?,?,?)", [qtd_produto,horario,tipo_mov,cpf_funcionario,id_produto])
                id_mov = cur.lastrowid
                con.commit()
                return {'id_mov':id_mov,'qtd_produto':qtd_produto,'horario':horario,'tipo_mov':tipo_mov,'cpf_funcionario':cpf_funcionario, 'id_produto':id_produto}

    def db_listar_mov(self):
        with closing(conectar()) as con, closing(con.cursor()) as cur:
            cur.execute("SELECT * FROM TB_MOV")
            return rows_to_dict(cur.description, cur.fetchall())

    def db_atualiza_mov_id_produto(self,id_mov,id_produto):
        with closing(conectar()) as con, closing(con.cursor()) as cur:
            cur.execute("UPDATE TB_MOV SET ID_PRODUTO = (?) WHERE ID_MOV = (?) ", [id_produto,id_mov])
            con.commit()
            return {'id_produto': id_produto , 'id_mov':id_mov}


    def cria_movimentacao_produto(self, qtd_produto,cpf_funcionario, tipo_mov,id_produto=None, nome_produto=None,descricao=None,valor=None):
            movimentacao = tipo_mov.cria_mov_produto(qtd_produto,cpf_funcionario,tipo_mov.get_nome_mov(),id_produto, nome_produto,descricao,valor)    
            return movimentacao


##################### CLASSE ENTRADA QUE HERDA A TIPO MOVIMENTACAO #####################
class Entrada(TipoMovimentacao):
    def __init__(self):
        self.set_nome_mov("ENTRADA")

    def cria_mov_produto(self, qtd_produto, cpf_funcionario,tipo_mov,id_produto=None, nome_produto=None,descricao=None,valor=None):
        if not db_localiza_produto(id_produto):
                movimentacao = Movimentacao()
                mov = movimentacao.db_criar_mov(qtd_produto,datetime.today(),self.get_nome_mov(),cpf_funcionario,None)
                self.set_id_mov(mov['id_mov'])
                produto = db_criar_produto(nome_produto,descricao,qtd_produto,valor,cpf_funcionario,self.get_id_mov())
                mov = movimentacao.db_atualiza_mov_id_produto(self.get_id_mov(),produto['id_produto'])
                return (mov,produto)
        else:
                produto = db_localiza_produto(id_produto)[0]
                movimentacao = Movimentacao()
                mov = movimentacao.db_criar_mov(qtd_produto,datetime.today(),self.get_nome_mov(),cpf_funcionario,produto['ID_PRODUTO'])
                self.set_id_mov(mov['id_mov'])
                qtd_estoque_atual = mov['qtd_produto'] + produto['QTD_ESTOQUE']
                produto_atual = db_atualizar_qtd_produto(id_produto,qtd_estoque_atual,self.get_id_mov(),cpf_funcionario)
                return (mov,produto)

##################### CLASSE SAIDA QUE HERDA A TIPO MOVIMENTACAO #####################
class Saida(TipoMovimentacao):
    def __init__(self):
        self.set_nome_mov("SAIDA")

    def cria_mov_produto(self,qtd_produto,cpf_funcionario,tipo_mov,id_produto=None, nome_produto=None,descricao=None,valor=None):
            if not db_localiza_produto(id_produto):
                return {'message':'PRODUTO NÃO EXISTE'}
            else:
                produto = db_localiza_produto(id_produto)[0]
                if produto['QTD_ESTOQUE'] > 0:
                        mov = movimentacao.db_criar_mov(qtd_produto,datetime.today(),self.get_nome_mov(),cpf_funcionario,produto['ID_PRODUTO'])
                        self.set_id_mov(mov['id_mov'])
                        qtd_estoque_atual = produto['QTD_ESTOQUE'] - mov['qtd_produto']
                        produto_atual = db_atualizar_qtd_produto(id_produto,qtd_estoque_atual,self.get_id_mov(),cpf_funcionario)
                        mov = movimentacao.db_atualiza_mov_id_produto(self.get_id_mov(),produto['ID_PRODUTO'])
                        return (mov,produto)
                else:
                    return {'message': f"QUANTIDADE DO PRODUTO NÃO PODE SER RETIRADA QTD: {produto['QTD_ESTOQUE']}"}


##################### CLASSE DEVOLUCAO QUE HERDA ENTRADA #####################
class Devolucao(Entrada):
    def __init__(self):
        self.set_nome_mov('DEVOLUCAO')

    def movimentacao_especifica(self):
            devolucao = self.cria_mov_produto(get_nome_mov(),qtd_produto,cpf_funcionario,id_produto=None, nome_produto=None,descricao=None,valor=None)
            return (devolucao)

##################### CLASSE EXTRAVIOPERDA QUE HERDA SAIDA#####################
class ExtravioPerda(Saida):
    def __init__(self):
        self.set_nome_mov('EXTRAVIO OU PERDA')
    def movimentacao_especifica(self):
            extravio_perda = self.cria_mov_produto(get_nome_mov(),qtd_produto,cpf_funcionario,id_produto=None, nome_produto=None,descricao=None,valor=None)
            return (extravio_perda)



############################ TABELA PRODUTO ########################################## 

def db_criar_produto(nome_produto,descricao,qtd_estoque,valor,cpf_funcionario,id_mov):
    with closing(conectar()) as con, closing(con.cursor()) as cur:
        cur.execute("INSERT INTO TB_PRODUTO (NOME_PRODUTO,DESCRICAO, QTD_ESTOQUE,VALOR,CPF_FUNCIONARIO,ID_MOV) VALUES (?,?,?,?,?,?)", [nome_produto,descricao,qtd_estoque,valor,cpf_funcionario,id_mov])
        id_produto = cur.lastrowid
        con.commit()
        return {'id_produto':id_produto,'nome_produto':nome_produto,'descricao':descricao,'qtd_estoque':qtd_estoque,'valor':valor,'cpf_funcionario':cpf_funcionario,'id_mov':id_mov}

def db_listar_produtos():
    with closing(conectar()) as con, closing(con.cursor()) as cur:
        cur.execute("SELECT * FROM TB_PRODUTO")
        return rows_to_dict(cur.description, cur.fetchall())

def db_localiza_produto(id_produto):
    with closing(conectar()) as con, closing(con.cursor()) as cur:
        cur.execute("SELECT * FROM TB_PRODUTO WHERE ID_PRODUTO = (?)", [id_produto])
        return rows_to_dict(cur.description, cur.fetchall())

def db_atualizar_qtd_produto(id_produto, qtd_estoque,id_mov,cpf_funcionario):
    with closing(conectar()) as con, closing(con.cursor()) as cur:
        cur.execute("UPDATE TB_PRODUTO SET QTD_ESTOQUE = (?), ID_MOV = (?), CPF_FUNCIONARIO = (?) WHERE ID_PRODUTO = (?) ", [qtd_estoque,id_mov,cpf_funcionario,id_produto])
        con.commit()
        return {'id_produto':id_produto,'qtd_estoque':qtd_estoque,'cpf_funcionario':cpf_funcionario,'id_mov':id_mov}


############################ TABELA TB_TAMANHO_PRODUTO ########################################## 

def db_criar_tamanho_produto(tamanho, id_produto):
    with closing(conectar()) as con, closing(con.cursor()) as cur:
        cur.execute("INSERT INTO TB_TAMANHO_PRODUTO (TAMANHO, ID_PRODUTO) VALUES (?,?)", [tamanho,id_produto])
        con.commit()
        return {'tamanho':tamanho, 'id_produto':id_produto}

def db_listar_tamanho_produtos():
    with closing(conectar()) as con, closing(con.cursor()) as cur:
        cur.execute("SELECT * FROM TB_TAMANHO_PRODUTO")
        return rows_to_dict(cur.description, cur.fetchall())


############################ TABELA TB_TAMANHO_PRODUTO ########################################## 

def db_criar_cor_produto(cor, id_produto):
    with closing(conectar()) as con, closing(con.cursor()) as cur:
        cur.execute("INSERT INTO TB_COR_PRODUTO (COR, ID_PRODUTO) VALUES (?,?)", [cor,id_produto])
        con.commit()
        return {'cor':cor, 'id_produto':id_produto}

def db_listar_cor_produtos():
    with closing(conectar()) as con, closing(con.cursor()) as cur:
        cur.execute("SELECT * FROM TB_COR_PRODUTO")
        return rows_to_dict(cur.description, cur.fetchall())



############################ TABELA PEDIDO ########################################## 

def db_criar_pedido(valor_total,id_conta, status):
    with closing(conectar()) as con, closing(con.cursor()) as cur:
        cur.execute("INSERT INTO TB_PEDIDO (VALOR_TOTAL, ID_CONTA, STATUS) VALUES (?,?,?)", [valor_total,id_conta,status])
        id_pedido = cur.lastrowid
        con.commit()
        return {'id_pedido':id_pedido,'valor_total':valor_total, 'id_conta':id_conta,'status':status}

def db_listar_pedidos():
    with closing(conectar()) as con, closing(con.cursor()) as cur:
        cur.execute("SELECT * FROM TB_PEDIDO")
        return rows_to_dict(cur.description, cur.fetchall())

def db_localizar_pedido(id_pedido):
    with closing(conectar()) as con, closing(con.cursor()) as cur:
        cur.execute('''SELECT * FROM TB_PEDIDO WHERE ID_PEDIDO = (?)''' , [id_pedido])
        return rows_to_dict(cur.description, cur.fetchone())

def db_listar_pedidos_cliente(id_conta):
    with closing(conectar()) as con, closing(con.cursor()) as cur:
        cur.execute('''SELECT * FROM TB_PEDIDO WHERE ID_CONTA = (?)''' , [id_conta])
        return rows_to_dict(cur.description, cur.fetchall())


def db_atualizar_valor_pedido(id_pedido,valor_total):
    with closing(conectar()) as con, closing(con.cursor()) as cur:
        cur.execute("UPDATE TB_PEDIDO SET VALOR_TOTAL = (?) WHERE ID_PEDIDO=(?)", [valor_total, id_pedido])
        con.commit()
        return {'valor_total':valor_total, 'id_pedido':id_pedido}

def db_atualizar_status_pedido(id_pedido,status):
    with closing(conectar()) as con, closing(con.cursor()) as cur:
        cur.execute("UPDATE TB_PEDIDO SET STATUS = (?) WHERE ID_PEDIDO=(?)", [status, id_pedido])
        con.commit()
        return {'status':status, 'id_pedido':id_pedido}

def db_detalhes_do_pedido(id_pedido):
    with closing(conectar()) as con, closing(con.cursor()) as cur:
        cur.execute('''
                        SELECT  
                                PEDIDO.ID_PEDIDO,
                                PRODUTO.NOME_PRODUTO,
                                PRODUTO.DESCRICAO, 
                                POSSUI.QTD_PRODUTO,
                                POSSUI.PRECO,
                                PEDIDO.VALOR_TOTAL,
                                PEDIDO.ID_CONTA,
                                PEDIDO.STATUS,
                                POSSUI.OBSERVACAO
                        FROM TB_POSSUI_PEDIDO_PRODUTO POSSUI  
                        INNER JOIN TB_PRODUTO PRODUTO  ON PRODUTO.ID_PRODUTO = POSSUI.ID_PRODUTO
                        INNER JOIN TB_PEDIDO PEDIDO ON  POSSUI.ID_PEDIDO = PEDIDO.ID_PEDIDO
                        WHERE POSSUI.ID_PEDIDO = (?)
                    ''' , [id_pedido])
        return rows_to_dict(cur.description, cur.fetchall())





############################ TABELA POSSUI_PEDIDO_PRODUTO ########################################## 

def db_criar_possui_pedido_produto(id_pedido,qtd_produto,preco,id_produto,observacao):
    with closing(conectar()) as con, closing(con.cursor()) as cur:
        cur.execute("INSERT INTO TB_POSSUI_PEDIDO_PRODUTO (ID_PEDIDO,QTD_PRODUTO,PRECO,ID_PRODUTO,OBSERVACAO) VALUES (?,?,?,?,?)", [id_pedido,qtd_produto,preco,id_produto,observacao])
        con.commit()
        return {'id_pedido':id_pedido,'qtd_produto':qtd_produto,'preco':preco,'id_produto':id_produto,'observacao':observacao}

def db_listar_possui_pedido_produto():
    with closing(conectar()) as con, closing(con.cursor()) as cur:
        cur.execute("SELECT * FROM TB_POSSUI_PEDIDO_PRODUTO")
        return rows_to_dict(cur.description, cur.fetchall())

def db_atualizar_observacao_pedido(id_pedido,id_produto,observacao):
    with closing(conectar()) as con, closing(con.cursor()) as cur:
        cur.execute("UPDATE TB_POSSUI_PEDIDO_PRODUTO SET OBSERVACAO = (?) WHERE ID_PEDIDO=(?) and ID_PRODUTO=(?)", [observacao, id_pedido,id_produto])
        con.commit()
        return {'observacao':observacao, 'id_pedido':id_pedido,'id_produto':id_produto}



############################ TABELA TB_PAGAMENTO ########################################## 

def db_criar_pagamento(forma_pag,data_pag, id_conta,id_pedido):
    with closing(conectar()) as con, closing(con.cursor()) as cur:
        cur.execute("INSERT INTO TB_PAGAMENTO (FORMA_PAG,DATA_PAG,ID_CONTA,ID_PEDIDO) VALUES (?,?,?,?)", [forma_pag,data_pag, id_conta,id_pedido])
        id_pag = cur.lastrowid
        con.commit()
        return {'forma_pag':forma_pag,'data_pag':data_pag, 'id_conta':id_conta,'id_pedido':id_pedido}

def db_listar_pagamentos():
    with closing(conectar()) as con, closing(con.cursor()) as cur:
        cur.execute("SELECT * FROM TB_PAGAMENTO")
        return rows_to_dict(cur.description, cur.fetchall())


############################ TABELA TB_TELEFONE_CLIENTE ########################################## 

def db_criar_telefone_cliente(id_conta,telefone):
    with closing(conectar()) as con, closing(con.cursor()) as cur:
        cur.execute("INSERT INTO TB_TELEFONE_CLIENTE (ID_CONTA, TELEFONE) VALUES (?,?)", [id_conta,telefone])
        con.commit()
        return {'id_conta':id_conta,'telefone':telefone}

def db_listar_telefone_cliente():
    with closing(conectar()) as con, closing(con.cursor()) as cur:
        cur.execute("SELECT * FROM TB_TELEFONE_CLIENTE")
        return rows_to_dict(cur.description, cur.fetchall())

############################ TABELA TB_TELEFONE_FUNCIONARIO ########################################## 

def db_criar_telefone_funcionario(cpf_funcionario,telefone):
    with closing(conectar()) as con, closing(con.cursor()) as cur:
        cur.execute("INSERT INTO TB_TELEFONE_FUNCIONARIO (CPF_FUNCIONARIO, TELEFONE) VALUES (?,?)", [cpf_funcionario,telefone])
        con.commit()
        return {'cpf':cpf_funcionario,'telefone':telefone}

def db_listar_telefone_funcionario():
    with closing(conectar()) as con, closing(con.cursor()) as cur:
        cur.execute("SELECT * FROM TB_TELEFONE_FUNCIONARIO")
        return rows_to_dict(cur.description, cur.fetchall())

