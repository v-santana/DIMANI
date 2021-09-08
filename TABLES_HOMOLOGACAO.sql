CREATE DATABASE IF NOT EXISTS DB_DIMANI_HOMOLOGACAO;
USE DB_DIMANI_HOMOLOGACAO;


CREATE TABLE IF NOT EXISTS TB_ESTADO (
    ID_ESTADO INT  AUTO_INCREMENT,
    NOME_ESTADO VARCHAR(25) NOT NULL,
    PRIMARY KEY(ID_ESTADO)
);


CREATE TABLE IF NOT EXISTS TB_CIDADE (
    ID_CIDADE INT AUTO_INCREMENT,
    NOME_CIDADE VARCHAR(60) NOT NULL,
    ID_ESTADO INT NOT NULL,
    PRIMARY KEY(ID_CIDADE),
    FOREIGN KEY(ID_ESTADO) REFERENCES TB_ESTADO(ID_ESTADO)
);


CREATE TABLE IF NOT EXISTS TB_ENDERECO (
    ID_ENDERECO INT AUTO_INCREMENT,
    RUA  VARCHAR(200) NOT NULL,
    NUMERO INT NOT NULL,
    BAIRRO VARCHAR(200) NOT NULL,
    COMPLEMENTO VARCHAR(30),
    ID_CIDADE INT NOT NULL,
    PRIMARY KEY(ID_ENDERECO),
    FOREIGN KEY(ID_CIDADE) REFERENCES TB_CIDADE(ID_CIDADE)
);

CREATE TABLE IF NOT EXISTS TB_CLIENTE (
    ID_CONTA INT AUTO_INCREMENT,
    CPF CHAR(11) NOT NULL,
    NOME VARCHAR(200) NOT NULL,
    DT_NASC DATE NOT NULL,
    EMAIL VARCHAR(100) NOT NULL,
    SENHA VARCHAR(100) NOT NULL,
    CHAVE_PIX VARCHAR(50),
    /*SENHA PRECISA SER CRIPTOGRAFADA M35 OU ALGO DO TIPO*/
    
    ID_ENDERECO INT NOT NULL,
    PRIMARY KEY(ID_CONTA),
    FOREIGN KEY(ID_ENDERECO) REFERENCES TB_ENDERECO(ID_ENDERECO)
);


CREATE TABLE IF NOT EXISTS TB_DADOS_BANCARIOS(
    CONTA VARCHAR(15),
    INSTITUICAO VARCHAR(50) NOT NULL,
    AGENCIA VARCHAR(15) NOT NULL,
    ID_CONTA INT NOT NULL,
    
    PRIMARY KEY(CONTA),
    FOREIGN KEY(ID_CONTA) REFERENCES TB_CLIENTE(ID_CONTA)

);






/*INSERT INTO TB_CLIENTE(CPF,NOME,DT_NASC,EMAIL,SENHA,ID_ENDERECO) 
VALUES('49311111111','GABRIEL','2020-12-01','gabriel123@gmail.com',MD5('GABRIEL123'),1)
*/

CREATE TABLE IF NOT EXISTS TB_FUNCIONARIO (
    CPF CHAR(11),
    NOME VARCHAR(200) NOT NULL,
    EMAIL VARCHAR(100) NOT NULL,
    SENHA VARCHAR(100) NOT NULL,
    SALARIO DECIMAL(13, 4),
    ID_ENDERECO INT NOT NULL,
    CPF_SUPERVISOR CHAR(11),
    
    PRIMARY KEY(CPF),
    FOREIGN KEY(ID_ENDERECO) REFERENCES TB_ENDERECO(ID_ENDERECO),
    FOREIGN KEY(CPF_SUPERVISOR) REFERENCES TB_FUNCIONARIO(CPF)
);

CREATE TABLE IF NOT EXISTS TB_MOV (
    ID_MOV INT AUTO_INCREMENT,
    QTD_PRODUTO INT NOT NULL,
    HORARIO DATETIME NOT NULL,
    TIPO_MOV VARCHAR(100) NOT NULL,
    CPF_FUNCIONARIO CHAR(11) NOT NULL,
    
    PRIMARY KEY(ID_MOV),
    FOREIGN KEY(CPF_FUNCIONARIO) REFERENCES TB_FUNCIONARIO(CPF)
);


CREATE TABLE IF NOT EXISTS TB_PRODUTO (
    ID_PRODUTO INT AUTO_INCREMENT,
    NOME_PRODUTO VARCHAR(100) NOT NULL,
    DESCRICAO VARCHAR(300) NOT NULL,
    QTD_ESTOQUE INT NOT NULL ,
    VALOR DECIMAL(13, 4) NOT NULL,
    CPF_FUNCIONARIO CHAR(11) NOT NULL,
    ID_MOV INT NOT NULL UNIQUE,
    
    PRIMARY KEY(ID_PRODUTO),
    FOREIGN KEY(CPF_FUNCIONARIO) REFERENCES TB_FUNCIONARIO(CPF),
    FOREIGN KEY(ID_MOV) REFERENCES TB_MOV(ID_MOV)
);

CREATE TABLE IF NOT EXISTS TB_COR_PRODUTO (
    COR VARCHAR(20),
    ID_PRODUTO INT,

    PRIMARY KEY(COR,ID_PRODUTO),
    FOREIGN KEY(ID_PRODUTO) REFERENCES TB_PRODUTO(ID_PRODUTO)
);

CREATE TABLE IF NOT EXISTS TB_TAMANHO_PRODUTO (
    TAMANHO VARCHAR(5),
    ID_PRODUTO INT,

    PRIMARY KEY(TAMANHO, ID_PRODUTO),
    FOREIGN KEY(ID_PRODUTO) REFERENCES TB_PRODUTO(ID_PRODUTO)
);

CREATE TABLE IF NOT EXISTS TB_PEDIDO (
    ID_PEDIDO INT AUTO_INCREMENT,
    VALOR_TOTAL DECIMAL(13, 4) NOT NULL,
    ID_CONTA INT NOT NULL,


    PRIMARY KEY(ID_PEDIDO),
    FOREIGN KEY(ID_CONTA) REFERENCES TB_CLIENTE(ID_CONTA)
);

CREATE TABLE IF NOT EXISTS TB_POSSUI_PEDIDO_PRODUTO (
    ID_PEDIDO INT NOT NULL,
    QTD_PRODUTO INT NOT NULL,
    PRECO DECIMAL(13, 4) NOT NULL,
    ID_PRODUTO INT NOT NULL,


    PRIMARY KEY(ID_PEDIDO, ID_PRODUTO),
    FOREIGN KEY(ID_PEDIDO) REFERENCES TB_PEDIDO(ID_PEDIDO),
    FOREIGN KEY(ID_PRODUTO) REFERENCES TB_PRODUTO(ID_PRODUTO)
);

CREATE TABLE IF NOT EXISTS TB_PAGAMENTO(
    ID_PAG INT AUTO_INCREMENT,
    FORMA_PAG VARCHAR(50) NOT NULL,
    DATA_PAG DATETIME NOT NULL,
    ID_CONTA INT NOT NULL,
    ID_PEDIDO INT NOT NULL,
    
    PRIMARY KEY(ID_PAG),
    FOREIGN KEY(ID_CONTA) REFERENCES TB_CLIENTE(ID_CONTA),
    FOREIGN KEY(ID_PEDIDO) REFERENCES TB_PEDIDO(ID_PEDIDO)
);

CREATE TABLE IF NOT EXISTS TB_TELEFONE_CLIENTE (
    ID_CONTA INT NOT NULL,
    TELEFONE VARCHAR(13) NOT NULL,

    PRIMARY KEY(ID_CONTA, TELEFONE),
    FOREIGN KEY(ID_CONTA) REFERENCES TB_CLIENTE(ID_CONTA)
);

CREATE TABLE IF NOT EXISTS TB_TELEFONE_FUNCIONARIO (
    CPF_FUNCIONARIO CHAR(11) NOT NULL,
    TELEFONE VARCHAR(13) NOT NULL,

    PRIMARY KEY(CPF_FUNCIONARIO, TELEFONE),
    FOREIGN KEY(CPF_FUNCIONARIO) REFERENCES TB_FUNCIONARIO(CPF)
);






