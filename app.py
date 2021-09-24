from funcoes_bd import *
from localStoragePy import localStoragePy

################ SENHA PARA CRIPTOGEAFIA DE SESSION ################
app = Flask(__name__)



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
#produto = db_criar_produto('MANTA',"MANTA INFANTIL",10,100.00,46211111111,1)
#movimentacao = Movimentacao()
#tipo_mov = Entrada()
#Formato para Entrada de Produto como Criação do Produto
#movimentacao.cria_movimentacao_produto(1,46211111111,tipo_mov,None,"Calça Legging","CAPA Calça",11.00)



def adiciona_carrinho(id_produto,nome_produto,descricao_produto,valor_produto):
    localStorage = localStoragePy('/DIMANI/app.py', 'text')
    lista = [id_produto, nome_produto, descricao_produto, valor_produto]
    localStorage.setItem(f"produto_{id_produto}", lista)
    return 

############################
#### Definições da API. ####
############################





# Cria o objeto principal do Flask.
app = Flask(__name__)

@app.route("/home", methods=['GET', 'POST'])
def index():
    return render_template("home.html", erro = "")


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


log_in = Blueprint("log_in",__name__)
@app.route("/login", methods=['GET','POST'])
def login():
    if request.method == 'POST':
        ########### Vai verificar se é cliente ou funcionário ########
        cliente_form_email = request.form['email']
        cliente_form_senha = request.form['senha']
        cliente = db_localizar_cliente_email(cliente_form_email)[0]
        if cliente['ID_CONTA'] != None:
            if cliente['EMAIL'] == cliente_form_email:
                if cliente['SENHA'] == cliente_form_senha:
                    session['ID_CONTA'] = cliente["ID_CONTA"]
                    session['CPF'] = cliente["CPF"]
                    session['DT_NASC'] = cliente["DT_NASC"]
                    session['EMAIL'] = cliente["EMAIL"]
                    session['NOME'] = cliente["NOME"]
                    print(session)
                    redirect('/catalogo')

        else:
            funcionario = db_localizar_funcionario_email(request.form['email'])
    return render_template('login.html')

@app.route('/logout', methods = ['POST','GET'])
def logout():
        session.clear()
        return redirect('login')

@app.route("/sobre", methods=['GET'])
def sobre():
    return render_template('sobre.html')

@app.route("/cadastro", methods=['POST','GET'])
def cadastro():
    if request.method == 'POST':
        ############# Variáveis do form dados de cadastro ###############
        cpf,nome_completo,dt_nasc,telefone = request.form['cpf'],request.form['nome_completo'],request.form['dt_nasc'],request.form['telefone'] 
        email,senha,confirmacao_senha = request.form['email'],request.form['senha'],request.form['confirmacao_senha']
        id_estado = request.form['estado']
        id_cidade = db_localizar_cidade_de_estado_por_nome(id_estado,request.form['cidade'])
        cep,rua,bairro,numero,complemento = request.form['cep'],request.form['rua'],request.form['bairro'],request.form['numero'],request.form['complemento']
        ###### verificar se email já existe no banco de dados ########
        #db_localizar_cliente_email(email)

        ##############################################################
        endereco = db_criar_endereco(rua,numero,bairro,complemento,id_cidade)
        cliente = db_criar_cliente(cpf, nome_completo, dt_nasc, email,senha,endereco['id_endereco'],"123")
        telefone_cliente = db_criar_telefone_cliente(cliente['id_conta'],telefone)
        
        ####### campos recolhidos pelo formulário #######
        print(f"{cpf} | {nome_completo} | {dt_nasc} | {telefone} | {email} | {senha} | {confirmacao_senha} | {cep} | {endereco} | {numero} | {complemento}")
        ###### Foi inserido no banco de dados #######
        print(cliente)
    return render_template('cadastro.html', estados=db_listar_estados())

@app.route("/teste", methods=['POST','GET'])
def teste():
    if request.method == 'POST':
        id_estado = request.form['estado']
        cidade= request.form['cidade']
        id_cidade = db_localizar_cidade_de_estado_por_nome(id_estado,request.form['cidade'])
        cep = request.form['cep']
        bairro=request.form['bairro']
        rua, numero, complemento = request.form['rua'],request.form['numero'], request.form['complemento']
        if len(id_cidade) > 1:
            return render_template("teste.html", mensagem = "Escolha novamente a Cidade", estados=db_listar_estados(), cidades =  id_cidade, id_estado = int(id_estado),bairro=bairro, rua = rua, complemento = complemento, numero=numero,cep=cep)
        else:
            print("Cidade escolhida!")
            cidade=request.form['cidade']
        print(f"Endereço cadastrado: Estado: {id_estado},Cidade: {cidade},Bairro:{bairro},Rua: {rua},Numero: {numero},Complemento: {complemento},CEP: {cep}")
    return render_template("teste.html", mensagem = "", estados=db_listar_estados(), cidades=None)





if __name__ == "__main__":
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'

    Session().init_app(app)

    app.debug = True
    app.run(debug=True)
