from funcoes_bd import *

################ CONFIGURANDO APP PARA UPLOAD DE IMAGENS ################
UPLOAD_FOLDER = 'static/images/produtos'
ALLOWED_EXTENSIONS = set(['jpg','jpeg','png','pdf'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def upload_file(name_file,nome_arquivo,pasta):
        if name_file not in request.files:
            flash('No file part')
            return redirect('catalogo')
        file = request.files[name_file]

        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect('catalogo')
        if file and allowed_file(file.filename):
            file.save(os.path.join(pasta, nome_arquivo))



# Cria o objeto principal do Flask.
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


############### FLUXO DE COMPROVANTE DE PAGAMENTO ###############
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
mail = Mail()

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'maildev.dimani@gmail.com'
app.config['MAIL_PASSWORD'] = 'Ope_202!'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_ASCII_ATTACHMENTS'] = True

mail.init_app(app)


############ ENVIO DE E-MAIL ##############
def send_message(corpo,assunto,lista_de_contatos,email):
    UPLOAD_FOLDER = '/home/DimaniAtelier/DIMANI/temp/'
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    upload_file('comprovante',f"comprovante.pdf",UPLOAD_FOLDER)
    msg = Message(assunto, sender = email,
            recipients = lista_de_contatos,
            body= corpo
    )

    arquivo = f'/home/DimaniAtelier/DIMANI/temp/comprovante.pdf'

    with app.open_resource(arquivo) as fp:
        msg.attach('comprovante', "application/pdf", fp.read())
    mail.send(msg)
    UPLOAD_FOLDER = 'static/images/produtos'
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


############################
#### Defini????es da API. ####
############################

############ ENVIO DE E-MAIL SENHA ##############
def send_senha(corpo,assunto,lista_de_contatos,email):
    UPLOAD_FOLDER = 'temp'
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    msg = Message(assunto, sender = email,
            recipients = lista_de_contatos,
            body= corpo
    )
    mail.send(msg)



@app.route("/home", methods=['GET', 'POST'])
def index():
    return render_template("home.html", erro = "",eh_funcionario=db_localizar_funcionario_email)


@app.route("/", methods=['GET', 'POST'])
def index_redirect():
    return redirect ("home")


#PEDIDOS NA VIS??O FUNCIONARIO - Podemos fazer uma verifica????o para validar se est?? logado ou n??o, ou se ?? funcion??rio
@app.route("/pedidos", methods=['GET', 'POST'])
def pedidos():
    try:
        pedidos = []
        #lista os pedidos do cliente logado
        if 'NOME' in session:
            #PEDIDOS NA VIS??O CLIENTE
            if db_localizar_cliente_email(session['EMAIL']):
                pedidos = db_listar_pedidos_cliente(session['ID_CONTA'])
                ### LISTA DE TELEFONES ###
                telefones = []
                for cliente in db_localizar_telefones_cliente(session['ID_CONTA']):
                    telefones.append(cliente['TELEFONE'])
                ###########################
                if request.method == 'POST':
                    lista_de_contatos = []
                    for usuario in db_listar_funcionarios():
                        lista_de_contatos.append(usuario['EMAIL'])
                    dados_pedido = db_localizar_pedido(request.form['id_pedido'])
                    html_comprovante = f'''Ol??, segue dados referente ao comprovante\n
                    NOME: {session['NOME']}\n
                    N?? PEDIDO: {request.form['id_pedido']}\n
                    VALOR TOTAL: {dados_pedido[0]['VALOR_TOTAL']}\n
                    TELEFONE: {telefones}\n
                    OBSERVA????ES: {request.form['observacoes_comprovante']}'''

                    send_message(html_comprovante,f"COMPROVANTE PEDIDO N??{request.form['id_pedido']}",lista_de_contatos,'maildev.dimani@gmail.com')

            #PEDIDOS NA VIS??O FUNCIONARIO
            elif db_localizar_funcionario_email(session['EMAIL']):
                pedidos = db_listar_pedidos()
                if request.method == 'POST':
                    id_pedido_form, status_form = int(request.form['id_pedido']), request.form['status_pedido']
                    db_atualizar_status_pedido(id_pedido_form,status_form)
                    return redirect('/pedidos')
        # SE N??O ESTIVER LOGADO

        return render_template('pedidos_cliente.html', pedidos=pedidos,eh_funcionario=db_localizar_funcionario_email)
    except Exception as e:
        return render_template('alert.html',mensagem_alerta=e)

#DESCRI????O DO PEDIDO COM BASE NO ID DO PEDIDO
@app.route("/pedidos/<id_pedido>", methods=['GET', 'POST'])
def detalhes_pedido(id_pedido):
    try:
        pedidos = db_detalhes_do_pedido(id_pedido)
        id_cliente = ""
        for pedido in pedidos:
            if 'ID_CONTA' in pedido:
                id_cliente = pedido['ID_CONTA']
            break
        return render_template('detalhes_pedido.html',detalhes_pedido = pedidos, id_cliente = id_cliente,eh_funcionario=db_localizar_funcionario_email)
    except Exception as e:
        return render_template('alert.html',mensagem_alerta=e)

@app.route("/catalogo", methods=['GET','POST'])
def catalogo():
    try:
        #lista o cat??logo de produtos
        catalogo_produtos = db_listar_produtos_cliente()
        if request.method == "POST":
            if db_localizar_funcionario_email(session['EMAIL']): #verifica se ?? funcionario
                #cria o produto
                produto = db_criar_produto(request.form['nome_produto'],request.form['descricao_produto'],request.form['qtd_produto'],request.form['valor_produto'],'ATIVO',session['CPF'])
                id_produto = produto['id_produto']
                upload_file('imagem_produto',f"produto_{id_produto}.jpg",'/home/DimaniAtelier/DIMANI/static/images/produtos/') #sobe imagem do produto no sistema /static/images/produtos
                return redirect('/catalogo')
        return render_template('catalogo.html', catalogo=catalogo_produtos, eh_funcionario=db_localizar_funcionario_email)
    except Exception as e:
        return render_template('alert.html',mensagem_alerta=e)

@app.route("/editar_produto/<id_produto>", methods=['GET','POST'])
def editar_produto(id_produto):
    try:
        #expande detalhes do produto selecionado no cat??logo
        produto = db_localiza_produto(id_produto)[0]
        #se o formul??rio for enviado
        if request.method == "POST":
            id,nome_produto = request.form['id_produto'],request.form['nome_produto']
            valor_produto,descricao_produto = request.form['valor_produto'],request.form['descricao_produto']
            db_editar_produto(id,nome_produto,string_para_float(valor_produto),descricao_produto)
            upload_file('imagem_nova_produto',f"produto_{id}.jpg",'home/DimaniAtelier/DIMANI/static/images/produtos') #sobe imagem do produto no sistema /static/images/produtos
            return redirect("/catalogo")
        return render_template('editar_produto.html', detalhes_produto=produto,eh_funcionario=db_localizar_funcionario_email)
    except Exception as e:
        return render_template('alert.html',mensagem_alerta=e)

@app.route("/remover_produto/<id_produto>", methods=['GET','POST'])
def remover_produto(id_produto):
    try:
        #expande detalhes do produto selecionado no cat??logo
        produto = db_localiza_produto(id_produto)[0]
        #se o formul??rio for enviado
        if request.method == "POST":
            if valida_login_funcionario(session['EMAIL'],request.form['senha_confirmacao']):
                db_remover_produto(request.form['id_produto'])
                time.sleep(1)
                return redirect("/catalogo")
            else:
                return render_template('remover_produto.html', detalhes_produto=produto, message="SENHA INV??LIDA",eh_funcionario=db_localizar_funcionario_email)
        return render_template('remover_produto.html', detalhes_produto=produto,eh_funcionario=db_localizar_funcionario_email, message="")
    except Exception as e:
        return render_template('alert.html',mensagem_alerta=e)

@app.route("/detalhes_produto/<id_produto>", methods=['GET'])
def detalhes_produto(id_produto):
    try:
        #expande detalhes do produto selecionado no cat??logo
        produto = db_localiza_produto(id_produto) [0]
        return render_template('detalhes_produto.html', detalhes_produto=produto, eh_funcionario=db_localizar_funcionario_email)
    except Exception as e:
        return render_template('alert.html',mensagem_alerta=e)

@app.route("/carrinho", methods=['GET'])
def carrinho():
    try:
        return render_template('tela_carrinho.html', eh_funcionario=db_localizar_funcionario_email)
    except Exception as e:
        return render_template('alert.html',mensagem_alerta=e)

@app.route("/fechar_pedido", methods=['GET'])
def fechar_pedido():
    try:
        return render_template('fechar_pedido.html', eh_funcionario=db_localizar_funcionario_email)
    except Exception as e:
        return render_template('alert.html',mensagem_alerta=e)

@app.route('/itens_carrinho', methods = ['POST','GET'])
def itens_carrinho():
    itens = request.get_json()
    concluir_pedido(itens,session['ID_CONTA'])
    return jsonify({'status':'success'})

@app.route('/navbar', methods=['GET'])
def navbar():
    try:
        return render_template('navbar.html', eh_funcionario=db_localizar_funcionario_email)
    except Exception as e:
        return render_template('alert.html',mensagem_alerta=e)

log_in = Blueprint("log_in",__name__)
@app.route("/login", methods=['GET','POST'])
def login():
    try:
        if request.method == 'POST':
            ########### Vai verificar se ?? cliente ou funcion??rio ########
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
                        return render_template('login.html', message="E-mail ou senha inv??lidos", eh_funcionario=db_localizar_funcionario_email)
            else:
                    if valida_login_funcionario(form_email,form_senha):
                            funcionario = db_localizar_funcionario_email(form_email)[0]
                            efetua_login_funcionario(funcionario['CPF'],funcionario['SALARIO'],funcionario['EMAIL'],funcionario['NOME'])
                            return redirect('/catalogo')
                    else:
                        return render_template('login.html', message="E-mail ou senha inv??lidos", eh_funcionario=db_localizar_funcionario_email)

        return render_template('login.html', message="", eh_funcionario=db_localizar_funcionario_email)
    except Exception as e:
        return render_template('alert.html',mensagem_alerta=e)

@app.route('/logout', methods = ['POST','GET'])
def logout():
    session.clear()
    return redirect('/login')

@app.route('/esqueci_senha', methods = ['POST','GET'])
def esqueci_senha():
    try:
        if request.method == 'POST':
            try:
                #para clientes em localizar cliente pelo cpf
                for cliente in db_localizar_cliente_cpf(request.form['cpf']):
                    #verifica se e-mail e cpf s??o do mesmo cliente
                    if cliente['EMAIL'] == request.form['email']:
                        #cria texto de senha e encaminha via e-mail
                        html_senha = f"Ol?? {cliente['NOME'].split(' ')[0]},\nSua senha de acesso no site DiMani Atelier ??:\nSENHA: {cliente['SENHA']}\natt, DiMani Atelier."
                        send_senha(html_senha,f"ACESSO DIMANI" ,[cliente['EMAIL']],'maildev.dimani@gmail.com')
                        return render_template('esqueci_senha.html',mensagem="E-mail encaminhado, confira sua caixa de entrada.",eh_funcionario=db_localizar_funcionario_email)
                    else:
                        #retorna mensagem de e-mail n??o correspondente
                        return render_template('esqueci_senha.html',mensagem="E-mail n??o correspondente ao CPF cadastrado, confira os dados e tente novamente.",eh_funcionario=db_localizar_funcionario_email)
            except:
                return render_template('esqueci_senha.html',mensagem="Ocorreu um erro inesperado, tente novamente ou contate um administrador.",eh_funcionario=db_localizar_funcionario_email)
        return render_template('esqueci_senha.html',eh_funcionario=db_localizar_funcionario_email)
    except Exception as e:
        return render_template('alert.html',mensagem_alerta=e)

@app.route("/sobre", methods=['GET'])
def sobre():
    try:
        return render_template('sobre.html', eh_funcionario=db_localizar_funcionario_email)
    except Exception as e:
        return render_template('alert.html',mensagem_alerta=e)

@app.route("/dados_cadastro", methods=['POST','GET'])
def dados():
    try:
        if 'ID_CONTA' in session:
            cliente = db_localizar_cliente(session['ID_CONTA'])
            telefone_cliente = db_localizar_telefones_cliente(cliente[0]['ID_CONTA'])
            if request.method == 'POST':
                atualiza_dados_cadastrais(session['ID_CONTA'],request.form['cpf'],request.form['nome_completo'],
                    request.form['dt_nasc'],request.form['email'],request.form['chave_pix'])
                return redirect('/dados_cadastro')
        elif 'SALARIO' in session:
            funcionario = db_localizar_funcionario_email(session['EMAIL'])
            if request.method == 'POST':
                atualiza_dados_cadastrais_funcionario(session['CPF'],request.form['nome_completo'],request.form['email'],request.form['cpf_supervisor'],request.form['salario'])
                return redirect('/dados_cadastro')
            return render_template('dados_funcionario.html', funcionario=funcionario, eh_funcionario=db_localizar_funcionario_email)
        else:
            cliente = [""]
            telefone_cliente=[""]
        return render_template('dados_cliente.html', cliente=cliente, eh_funcionario=db_localizar_funcionario_email)
    except Exception as e:
        return render_template('alert.html',mensagem_alerta=e)

@app.route("/dados_cadastro/editar_telefones", methods=['POST','GET'])
def editar_telefones():
    try:
        if 'ID_CONTA' in session:
            cliente = db_localizar_cliente(session['ID_CONTA'])
            telefone_cliente = db_localizar_telefones_cliente(cliente[0]['ID_CONTA'])
            if request.method == 'POST':
                resposta = db_criar_telefone_cliente(session['ID_CONTA'],request.form['adicionar_telefone'])
                return redirect('/dados_cadastro/editar_telefones')
                #return render_template('editar_telefone.html',telefone_cliente=telefone_cliente,message=resposta['message'], eh_funcionario=db_localizar_funcionario_email)
        else:
            cliente = [""]
            telefone_cliente=[""]

        return render_template('editar_telefone.html',telefone_cliente= telefone_cliente,message="", eh_funcionario=db_localizar_funcionario_email)
    except Exception as e:
        return render_template('alert.html',mensagem_alerta=e)

@app.route("/cadastro", methods=['POST','GET'])
def cadastro():
    if request.method == 'POST':
        ############# Vari??veis do formul??rio dados de cadastro ###############
        cpf,nome_completo,dt_nasc,telefone = request.form['cpf'],request.form['nome_completo'],request.form['dt_nasc'],request.form['telefone']
        email,senha,confirmacao_senha = request.form['email'],request.form['senha'],request.form['confirmacao_senha']

        #verifica se selecionou chave pix
        if 'inlineRadioOptions' not in request.form: pix = "NAO_INFORMOU"
        elif request.form['inlineRadioOptions'] != "nao_informou": pix = request.form[request.form['inlineRadioOptions']]
        else: pix = "NAO_INFORMOU"

        ###### Verifica se email e CPF j?? existe no banco de dados ########
        if db_localizar_cliente_cpf(cpf):
            return render_template('cadastro.html', estados=db_listar_estados(), cidades=None,mensagem="CPF j?? utilizado, verifique se j?? tem uma conta.", eh_funcionario=db_localizar_funcionario_email)
        elif db_localizar_cliente_email(email) or db_localizar_funcionario_email(email):
            return render_template('cadastro.html', estados=db_listar_estados(), cidades=None,mensagem="E-mail j?? utilizado, por favor escolha outro e-mail ou verifique se j?? tem uma conta.", eh_funcionario=db_localizar_funcionario_email)
        else:
            session['NOME'],session['CPF'],session['DT_NASC'],session['EMAIL']  = nome_completo,cpf,dt_nasc,email
            session['SENHA'],session['TELEFONE'],session['PIX'],session['TELEFONE'] = senha,telefone, pix, telefone
            return redirect('/cadastro/endereco')
    return render_template('cadastro.html', estados=db_listar_estados(), cidades=None, mensagem="", eh_funcionario=db_localizar_funcionario_email)


@app.route("/cadastro/endereco", methods=['POST','GET'])
def cadastro_endereco():
    try:
        if request.method == 'POST':
            id_estado = request.form['estado']
            cidade= request.form['cidade']
            id_cidade = db_localizar_cidade_de_estado_por_nome(id_estado,request.form['cidade'])
            cep = request.form['cep']
            bairro=request.form['bairro']
            print(cidade)
            rua, numero, complemento = request.form['rua'],request.form['numero'], request.form['complemento']
            #Se a quantidade de cidades na consulta for maior que 1
            if len(id_cidade) > 1:
                return render_template("cadastro_endereco.html", mensagem = "Escolha novamente a Cidade", estados=db_listar_estados(), cidades =  id_cidade, id_estado = int(id_estado),bairro=bairro, rua = rua, complemento = complemento, numero=numero,cep=cep,eh_funcionario=db_localizar_funcionario_email)
            elif db_localizar_cidade(request.form['cidade']):
                id_cidade = db_localizar_cidade(request.form['cidade'])
                cidade=request.form['cidade']
                endereco = db_criar_endereco(rua,numero,bairro,complemento,id_cidade[0]['ID_CIDADE'])
                cliente = db_criar_cliente(session['CPF'],session['NOME'],session['DT_NASC'],session['EMAIL'],session['SENHA'],endereco['id_endereco'],session['EMAIL'])
                telefone_cliente = db_criar_telefone_cliente(cliente['id_conta'],session['TELEFONE'])
                return redirect('/logout')
            elif db_localizar_cidade_de_estado_por_nome(id_estado, request.form['cidade']):
                id_cidade = db_localizar_cidade_de_estado_por_nome(id_estado, request.form['cidade'])
                cidade=request.form['cidade']
                endereco = db_criar_endereco(rua,numero,bairro,complemento,id_cidade[0]['ID_CIDADE'])
                cliente = db_criar_cliente(session['CPF'],session['NOME'],session['DT_NASC'],session['EMAIL'],session['SENHA'],endereco['id_endereco'],session['EMAIL'])
                telefone_cliente = db_criar_telefone_cliente(cliente['id_conta'],session['TELEFONE'])
                return redirect('/logout')
            else:
                return render_template("cadastro_endereco.html", mensagem = "Cidade n??o localizada na base de dados", estados=db_listar_estados(), cidades=None, eh_funcionario=db_localizar_funcionario_email)
        return render_template("cadastro_endereco.html", mensagem = "", estados=db_listar_estados(), cidades=None, eh_funcionario=db_localizar_funcionario_email)
    except Exception as e:
        return render_template('alert.html',mensagem_alerta=e)

@app.route("/cadastro_funcionario", methods=['POST','GET'])
def cadastro_funcionario():
    try:
        if request.method == 'POST':
            ############# Vari??veis do formul??rio dados de cadastro ###############
            cpf,nome_completo,salario,telefone = request.form['cpf'],request.form['nome_completo'],request.form['salario'],request.form['telefone']
            email,senha = request.form['email'],request.form['senha']
            cpf_supervisor = request.form['cpf_supervisor']
            ###### Verifica se email e CPF j?? existe no banco de dados ########
            if db_localizar_funcionario_cpf(cpf):
                return render_template('cadastro_funcionario.html', estados=db_listar_estados(), cidades=None,mensagem="CPF j?? utilizado, verifique se j?? tem uma conta.", eh_funcionario=db_localizar_funcionario_email)
            elif db_localizar_cliente_email(email) or db_localizar_funcionario_email(email):
                return render_template('cadastro_funcionario.html', estados=db_listar_estados(), cidades=None,mensagem="E-mail j?? utilizado, por favor escolha outro e-mail ou verifique se j?? tem uma conta.", eh_funcionario=db_localizar_funcionario_email)
            else:
                session['NOME_FUNCIONARIO'],session['CPF_FUNCIONARIO'],session['SALARIO_FUNCIONARIO'],session['EMAIL_FUNCIONARIO']  = nome_completo,cpf,salario,email
                session['SENHA_FUNCIONARIO'],session['TELEFONE_FUNCIONARIO'],session['CPF_SUPERVISOR'] = senha,telefone, cpf_supervisor,
                return redirect('/cadastro_funcionario/endereco')
        return render_template('cadastro_funcionario.html', estados=db_listar_estados(), cidades=None, mensagem="", eh_funcionario=db_localizar_funcionario_email)
    except Exception as e:
        return render_template('alert.html',mensagem_alerta=e)

@app.route("/cadastro_funcionario/endereco", methods=['POST','GET'])
def cadastro_endereco_funcionario():
    try:
        if request.method == 'POST':
            id_estado = request.form['estado']
            cidade= request.form['cidade']
            id_cidade = db_localizar_cidade_de_estado_por_nome(id_estado,request.form['cidade'])
            cep = request.form['cep']
            bairro=request.form['bairro']
            rua, numero, complemento = request.form['rua'],request.form['numero'], request.form['complemento']
            #Se a quantidade de cidades na consulta for maior que 1
            if len(id_cidade) > 1:
                return render_template("cadastro_endereco_funcionario.html", mensagem = "Escolha novamente a Cidade", estados=db_listar_estados(), cidades =  id_cidade, id_estado = int(id_estado),bairro=bairro, rua = rua, complemento = complemento, numero=numero,cep=cep,eh_funcionario=db_localizar_funcionario_email)
            elif db_localizar_cidade(request.form['cidade']):
                id_cidade = db_localizar_cidade(request.form['cidade'])
                cidade=request.form['cidade']
                endereco = db_criar_endereco(rua,numero,bairro,complemento,id_cidade[0]['ID_CIDADE'])
                funcionario = db_criar_funcionario(cpf=session['CPF_FUNCIONARIO'],nome=session['NOME_FUNCIONARIO'],email=session['EMAIL_FUNCIONARIO'],salario=session['SALARIO_FUNCIONARIO'],senha=session['SENHA_FUNCIONARIO'],id_endereco=endereco['id_endereco'],cpf_supervisor=session['CPF_SUPERVISOR'])
                telefone_funcionario = db_criar_telefone_funcionario(funcionario['cpf'],session['TELEFONE_FUNCIONARIO'])
                return redirect('/catalogo')
            elif db_localizar_cidade_de_estado_por_nome(id_estado, request.form['cidade']):
                id_cidade = db_localizar_cidade_de_estado_por_nome(id_estado, request.form['cidade'])
                cidade=request.form['cidade']
                endereco = db_criar_endereco(rua,numero,bairro,complemento,id_cidade[0]['ID_CIDADE'])
                funcionario = db_criar_funcionario(cpf=session['CPF_FUNCIONARIO'],nome=session['NOME_FUNCIONARIO'],email=session['EMAIL_FUNCIONARIO'],salario=session['SALARIO_FUNCIONARIO'],senha=session['SENHA_FUNCIONARIO'],id_endereco=endereco['id_endereco'],cpf_supervisor=session['CPF_SUPERVISOR'])
                telefone_funcionario = db_criar_telefone_funcionario(funcionario['cpf'],session['TELEFONE_FUNCIONARIO'])
                return redirect('/catalogo')
            else:
                return render_template("cadastro_endereco.html", mensagem = "Cidade n??o localizada na base de dados", estados=db_listar_estados(), cidades=None, eh_funcionario=db_localizar_funcionario_email)
        return render_template("cadastro_endereco_funcionario.html", mensagem = "", estados=db_listar_estados(), cidades=None, eh_funcionario=db_localizar_funcionario_email)
    except Exception as e:
        return render_template('alert.html',mensagem_alerta=e)

if __name__ == "__main__":
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'

    Session().init_app(app)
    app.debug = True
    app.run(debug=True)
