from funcoes_bd import *





#estado = db_criar_estado('São Paulo')
#cidade = db_criar_cidade('São Paulo',1)
#endereco = db_criar_endereco('Rua mauá',333,'Vila Conde','',9321)
#cliente = db_criar_cliente('49311111111','GABRIEL','2020-12-01','gabriel123@gmail.com','GABRIEL123',1,'gabriel123@gmail.com')
#funcionario = db_criar_funcionario(46211111111,'LUCAS','lucas123@gmail.com','SENHA123',500.00,1,46211111111)
#movimentacao = db_criar_mov(10,'2021-09-01 12:10:10','ENTRADA DE MATERIAL',46211111111) 
#produto = db_criar_produto('MANTA',"MANTA INFANTIL",10,100.00,46211111111,1)
#tamanho_produto= db_criar_tamanho_produto('GG',1)
#cor_produto=db_criar_cor_produto('Amarelo',1)
#pedido = db_criar_pedido('500.00',1)
#possui_pedido_produto = db_criar_possui_pedido_produto(1,10,10.00,1)
#pagamento = db_criar_pagamento('PIX','2021-08-31 13:44:58', 1,1)
#dados_bancarios = db_criar_dados_bancarios(121314,'ITAU',7774,1)
#telefone_cliente=db_criar_telefone_cliente(1,11991677866)
#telefone_funcionario=db_criar_telefone_funcionario(46211111111,1145183646)


#estados = db_listar_estados()
#cidades= db_listar_cidades()
#enderecos = db_listar_enderecos()
#clientes = db_listar_clientes()
#funcionarios= db_listar_funcionarios()
#movimentacoes = db_listar_mov()
#produtos = db_listar_produtos()
#tamanho_produtos = db_listar_tamanho_produtos()
#cor_produtos= db_listar_cor_produtos()
#pedidos = db_listar_pedidos()
#possui_pedido_produtos = db_listar_possui_pedido_produto()
#pagamentos = db_listar_pagamentos()
#dados_bancarios = db_listar_dados_bancarios()
#telefone_clientes= db_listar_telefone_cliente()
#telefone_funcionarios= db_listar_telefone_funcionario()
#print(f" ENDEREÇOS: {enderecos}\n CLIENTES: {clientes}\n FUNCIONARIOS: {funcionarios}\n MOVIMENTACOES: {movimentacoes}\n PRODUTOS: {produtos}\n TAMANHO: {tamanho_produtos}\n COR: {cor_produtos}\n PEDIDO: {pedidos}\n POSSUI_PEDIDO_PRODUTO: {possui_pedido_produtos}\n PAGAMENTOS: {pagamentos}\n DADOS_BANCARIOS: {dados_bancarios}\n telefone_clientes: {telefone_clientes}\n telefone_funcionarios: {telefone_funcionarios}")
#criar = criar_mov_produto(5,'ENTRADA',46211111111,None,'MEIA','MEIA INFANTIL',20.00)

############################
#### Definições da API. ####
############################





# Cria o objeto principal do Flask.
app = Flask(__name__)

@app.route("/home", methods=['GET', 'POST'])
def index():
    return render_template("index.html", erro = "")


@app.route("/", methods=['GET', 'POST'])
def index_redirect():
    return redirect ("home")


#PEDIDOS NA VISÃO CLIENTE - Podemos fazer uma verificação para validar se está logado ou não, ou se é funcionário
@app.route("/pedidos", methods=['GET', 'POST'])
def pedidos_cliente():
    #lista os pedidos do cliente
    pedidos = db_listar_pedidos_cliente(1)
    return render_template('pedidos_cliente.html', pedidos=pedidos)

#DESCRIÇÃO DO PEDIDO COM BASE NO ID DO PEDIDO
@app.route("/pedidos/<id_pedido>", methods=['GET', 'POST'])
def detalhes_pedido(id_pedido):
    pedido = db_detalhes_do_pedido(id_pedido)
    return render_template('detalhes_pedido.html',detalhes_pedido = pedido)


@app.route("/catalogo", methods=['GET'])
def catalogo():
    #lista o catálogo de produtos
    catalogo_produtos = db_listar_produtos()
    return render_template('catalogo.html', catalogo=catalogo_produtos)

@app.route("/detalhes_produto/<id_produto>", methods=['GET'])
def detalhes_produto(id_produto):
    #expande detalhes do produto selecionado no catálogo
    produto = db_localiza_produto(id_produto) [0]
    return render_template('detalhes_produto.html', detalhes_produto=produto)

@app.route("/carrinho", methods=['GET'])
def carrinho():
    return render_template('carrinho.html')



def teste():
    if request.method == 'POST':
        estado_form =  request.form['estado']
        cidade= request.form['cidade']
        cidade_form = db_localizar_cidade_de_estado_por_nome(estado_form, cidade)
        print(cidade_form)
    return render_template("teste.html", erro = "", estados=db_listar_estados(),consulta_cidade = db_localizar_cidade_de_estado_por_nome)





if __name__ == "__main__":
    app.run(debug=True)
