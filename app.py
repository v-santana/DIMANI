from funcoes_bd import *

################ CONFIGURANDO APP PARA UPLOAD DE IMAGENS ################
UPLOAD_FOLDER = 'static/images/produtos'
ALLOWED_EXTENSIONS = set(['jpg','jpeg','png'])
    
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def upload_file(name_file,nome_arquivo):
        if name_file not in request.files:
            flash('No file part')
            print('primeira verificacao')
            return redirect('catalogo')
        file = request.files[name_file]
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            print('segunda verificacao')
            flash('No selected file')
            return redirect('catalogo')
        if file and allowed_file(file.filename):
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], nome_arquivo))

# Cria o objeto principal do Flask.
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER





############################
#### Definições da API. ####
############################







@app.route("/home", methods=['GET', 'POST'])
def index():
    return render_template("home.html", erro = "")


@app.route("/", methods=['GET', 'POST'])
def index_redirect():
    return redirect ("home")


#PEDIDOS NA VISÃO FUNCIONARIO - Podemos fazer uma verificação para validar se está logado ou não, ou se é funcionário
@app.route("/pedidos", methods=['GET', 'POST'])
def pedidos():
    pedidos = []
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


@app.route("/catalogo", methods=['GET','POST'])
def catalogo():
    #lista o catálogo de produtos
    catalogo_produtos = db_listar_produtos()
    if request.method == "POST":
        if db_localizar_funcionario_email(session['EMAIL']): #verifica se é funcionario
            #cria o produto
            produto = db_criar_produto(request.form['nome_produto'],request.form['descricao_produto'],request.form['qtd_produto'],request.form['valor_produto'],session['CPF'])
            id_produto = produto['id_produto']
            upload_file('imagem_produto',f"produto_{id_produto}.jpg") #sobe imagem do produto no sistema /static/images/produtos
            return redirect('/catalogo')
    return render_template('catalogo.html', catalogo=catalogo_produtos, eh_funcionario=db_localizar_funcionario_email)

@app.route("/editar_produto/<id_produto>", methods=['GET','POST'])
def editar_produto(id_produto):

    #expande detalhes do produto selecionado no catálogo
    produto = db_localiza_produto(id_produto)[0]

    #se o formulário for enviado
    if request.method == "POST":
        id,nome_produto = request.form['id_produto'],request.form['nome_produto']
        valor_produto,descricao_produto = request.form['valor_produto'],request.form['descricao_produto']
        print(db_editar_produto(id,nome_produto,float(valor_produto.replace(',','.')),descricao_produto))
        print(upload_file('imagem_nova_produto',f"produto_{id}.jpg")) #sobe imagem do produto no sistema /static/images/produtos
        return redirect(url_for(f"catalogo"))
    return render_template('editar_produto.html', detalhes_produto=produto)

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
    concluir_pedido(itens,session['ID_CONTA'])
    return jsonify({'status':'success'})

@app.route('/navbar', methods=['GET'])
def navbar():
    return render_template('navbar.html')

log_in = Blueprint("log_in",__name__)
@app.route("/login", methods=['GET','POST'])
def login():
    if request.method == 'POST':
        ########### Vai verificar se é cliente ou funcionário ########
        form_email = request.form['email']
        form_senha = request.form['senha']
        cliente = db_localizar_cliente_email(form_email)
        if cliente:
            cliente = cliente[0]
            if cliente['EMAIL'] == form_email:
                if cliente['SENHA'] == form_senha:
                    efetua_login_cliente(cliente['ID_CONTA'],cliente['CPF'],cliente['DT_NASC'],cliente['EMAIL'],cliente['NOME'])
                    return redirect('/catalogo')
        else:
            funcionario = db_localizar_funcionario_email(form_email)
            if funcionario:
                funcionario = funcionario[0]
                if funcionario['EMAIL'] == form_email:
                    if funcionario['SENHA'] == form_senha:
                        efetua_login_funcionario(funcionario['CPF'],funcionario['SALARIO'],funcionario['EMAIL'],funcionario['NOME'])
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

@app.route("/dados_cadastro", methods=['POST','GET'])
def dados():
    if 'ID_CONTA' in session:
        cliente = db_localizar_cliente(session['ID_CONTA'])
        telefone_cliente = db_localizar_telefones_cliente(cliente[0]['ID_CONTA'])
        if request.method == 'POST':
            atualiza_dados_cadastrais(session['ID_CONTA'],request.form['cpf'],request.form['nome_completo'],
                request.form['dt_nasc'],request.form['telefone'],request.form['email'],request.form['chave_pix'])
            return redirect('/dados_cadastro')
    else:
        cliente = [""]
        telefone_cliente=[""]
    return render_template('dados_cliente.html', cliente=cliente)

@app.route("/dados_cadastro/editar_telefones", methods=['POST','GET'])
def editar_telefones():
    if 'ID_CONTA' in session:
        cliente = db_localizar_cliente(session['ID_CONTA'])
        telefone_cliente = db_localizar_telefones_cliente(cliente[0]['ID_CONTA'])
        print(db_localizar_telefones_cliente(session['ID_CONTA']))
        if request.method == 'POST':
            resposta = db_criar_telefone_cliente(session['ID_CONTA'],request.form['adicionar_telefone'])
            return render_template('editar_telefone.html',telefone_cliente=telefone_cliente,message=resposta['message'])
    else:
        cliente = [""]
        telefone_cliente=[""]

    return render_template('editar_telefone.html',telefone_cliente= telefone_cliente,message="")

@app.route("/cadastro", methods=['POST','GET'])
def cadastro():
    if request.method == 'POST':
        ############# Variáveis do formulário dados de cadastro ###############
        cpf,nome_completo,dt_nasc,telefone = request.form['cpf'],request.form['nome_completo'],request.form['dt_nasc'],request.form['telefone'] 
        email,senha,confirmacao_senha = request.form['email'],request.form['senha'],request.form['confirmacao_senha']
        
        #verifica se selecionou chave pix
        if 'inlineRadioOptions' not in request.form: pix = "NAO_INFORMOU" 
        elif request.form['inlineRadioOptions'] != "nao_informou": pix = request.form[request.form['inlineRadioOptions']]
        else: pix = "NAO_INFORMOU"

        ###### Verifica se email e CPF já existe no banco de dados ########
        if db_localizar_cliente_cpf(cpf):
            return render_template('cadastro.html', estados=db_listar_estados(), cidades=None,mensagem="CPF já utilizado, verifique se já tem uma conta.") 
        elif db_localizar_cliente_email(email) or db_localizar_funcionario_email(email):
            return render_template('cadastro.html', estados=db_listar_estados(), cidades=None,mensagem="E-mail já utilizado, por favor escolha outro e-mail ou verifique se já tem uma conta.") 
        else:
            session['NOME'],session['CPF'],session['DT_NASC'],session['EMAIL']  = nome_completo,cpf,dt_nasc,email
            session['SENHA'],session['TELEFONE'],session['PIX'],session['TELEFONE'] = senha,telefone, pix, telefone
            return redirect('/cadastro/endereco')
    return render_template('cadastro.html', estados=db_listar_estados(), cidades=None, mensagem="")

@app.route("/cadastro/endereco", methods=['POST','GET'])
def cadastro_endereco():
    if request.method == 'POST':
        id_estado = request.form['estado']
        cidade= request.form['cidade']
        id_cidade = db_localizar_cidade_de_estado_por_nome(id_estado,request.form['cidade'])
        cep = request.form['cep']
        bairro=request.form['bairro']
        rua, numero, complemento = request.form['rua'],request.form['numero'], request.form['complemento']
        #Se a quantidade de cidades na consulta for maior que 1
        if len(id_cidade) > 1:
            return render_template("cadastro_endereco.html", mensagem = "Escolha novamente a Cidade", estados=db_listar_estados(), cidades =  id_cidade, id_estado = int(id_estado),bairro=bairro, rua = rua, complemento = complemento, numero=numero,cep=cep)
        else:
            cidade=request.form['cidade']
            endereco = db_criar_endereco(rua,numero,bairro,complemento,cidade)
            cliente = db_criar_cliente(session['CPF'],session['NOME'],session['DT_NASC'],session['EMAIL'],session['SENHA'],endereco['id_endereco'],session['EMAIL'])
            telefone_cliente = db_criar_telefone_cliente(cliente['id_conta'],session['TELEFONE'])
            return redirect('/catalogo')
    return render_template("cadastro_endereco.html", mensagem = "", estados=db_listar_estados(), cidades=None)




if __name__ == "__main__":
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'

    Session().init_app(app)

    app.debug = True
    app.run(debug=True)
