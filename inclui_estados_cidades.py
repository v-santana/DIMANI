from app import db_criar_cidade, db_criar_estado 

import pandas as pd


############## ESTADO ########################
arquivo_estado = pd.read_csv('estados.txt',header=None, index_col=False)
arquivo_estado = arquivo_estado[0]

#for linha in arquivo_estado:
#	print(linha)
#	db_criar_estado(linha)

############## CIDADE ########################
arquivo_cidade = pd.read_csv('cidades.txt', index_col=False)


for index ,linha in arquivo_cidade.iterrows():
    #print(linha['ID_ESTADO'],linha['NOME_CIDADE'])
	db_criar_cidade(linha['ID_ESTADO'],linha['NOME_CIDADE'])