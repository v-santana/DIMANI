from funcoes_bd import *

################ SENHA PARA CRIPTOGEAFIA DE SESSION ################
app = Flask(__name__)




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


#PEDIDOS NA VISÃO FUNCIONARIO - Podemos fazer uma verificação para validar se está logado ou não, ou se é funcionário
@app.route("/pedidos", methods=['GET', 'POST'])
def pedidos():
    #lista os pedidos do cliente logado
    if 'NOME' in session:
        #PEDIDOS NA VISÃO CLIENTE
        if db_localizar_cliente_email(session['EMAIL']):
            pedidos = db_listar_pedidos_cliente(session['ID_CONTA'])
        
        #PEDIDOS NA VISÃO FUNCIONARIO
        elif db_localizar_funcionario_email(session['EMAIL']):
            pedidos = db_listar_pedidos()
            if request.method == 'POST':
                id_pedido_form, status_form = int(request.form['id_pedido']), request.form['status_pedido']
                db_atualizar_status_pedido(id_pedido_form,status_form)
                return redirect('/pedidos')       
    # SE NÃO ESTIVER LOGADO
    else:
        pedidos = []
    return render_template('pedidos_cliente.html', pedidos=pedidos)

#DESCRIÇÃO DO PEDIDO COM BASE NO ID DO PEDIDO
@app.route("/pedidos/<id_pedido>", methods=['GET', 'POST'])
def detalhes_pedido(id_pedido):
    pedidos = db_detalhes_do_pedido(id_pedido)
    id_cliente = ""
    for pedido in pedidos:
        if 'ID_CONTA' in pedido:
            id_cliente = pedido['ID_CONTA']
        break
    return render_template('detalhes_pedido.html',detalhes_pedido = pedidos, id_cliente = id_cliente)


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
    return render_template('tela_carrinho.html')

@app.route("/fechar_pedido", methods=['GET'])
def fechar_pedido():
    return render_template('fechar_pedido.html')

@app.route('/itens_carrinho', methods = ['POST','GET'])
def itens_carrinho():
    itens = request.get_json()
    print(itens)


    return jsonify({'status':'success'})

log_in = Blueprint("log_in",__name__)
@app.route("/login", methods=['GET','POST'])
def login():
    print('EMAIL:::::',session.keys())
    if request.method == 'POST':

        ########### Vai verificar se é cliente ou funcionário ########
        form_email = request.form['email']
        form_senha = request.form['senha']
        cliente = db_localizar_cliente_email(form_email)
        if cliente:
            cliente = cliente[0]
            if cliente['EMAIL'] == form_email:
                if cliente['SENHA'] == form_senha:
                    session['ID_CONTA'] = cliente["ID_CONTA"]
                    session['CPF'] = cliente["CPF"]
                    session['DT_NASC'] = cliente["DT_NASC"]
                    session['EMAIL'] = cliente["EMAIL"]
                    session['NOME'] = cliente["NOME"]
                    return redirect('/catalogo')

        else:
            funcionario = db_localizar_funcionario_email(form_email)
            if funcionario:
                funcionario = funcionario[0]
                if funcionario['EMAIL'] == form_email:
                    if funcionario['SENHA'] == form_senha:
                        session['CPF'] = funcionario["CPF"]
                        session['EMAIL'] = funcionario["EMAIL"]
                        session['ID_ENDERECO'] = funcionario["ID_ENDERECO"]
                        session['SALARIO'] = funcionario["SALARIO"]
                        session['NOME'] = funcionario["NOME"]
                        return redirect('/catalogo')
            else:
                return render_template('login.html', message="E-mail ou senha invalidos")

    return render_template('login.html', message="")

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
