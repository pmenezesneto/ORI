from __future__ import division
import sys
import math
import nltk
import string

stopwords = nltk.corpus.stopwords.words
stopwords = nltk.corpus.stopwords.words("portuguese")

nomeArq = sys.argv[1]
consulta = sys.argv[2]
stopwords = nltk.corpus.stopwords.words("portuguese")

tokenize = lambda doc: doc.lower().split(" ")

def criaIndiceInvertido(indice, texto, i): #passo como parâmetro, um dicionário que será instanciado, o texto e o índice do arquivo lido
	for palavra in texto:
		palavra = palavra.upper()
		if indice.get(palavra) == None:
			indice[palavra] = {}
			indice[palavra][i+1] = 0
		else:
			if indice.get(palavra).get(i+1) == None :
				indice[palavra][i+1] = 0
		indice[palavra][i+1] +=1

def palavrasToRemove ():
    array = []
    for palavra in stopwords:
        array.append(palavra.replace("u", ""))
    return array

def pesquisaPalavra(indice, palavra, documento):
    resultado = []
    indice_arquivo = []
    arquivos_palavras = []
    for i in range(len(documento)):
        indice_arquivo.append(i+1)

    if indice.get(palavra) != None:
        for i in indice[palavra]:
            if i not in resultado:
                arquivos_palavras.append(i)
            return list(filter(lambda p:p not in arquivos_palavras, indice_arquivo))
    else:
        return []

palavrasRemovidas = palavrasToRemove()
palavrasRemovidas.append("&")
arrayConsulta = []
arrayConsultaAnd = []
arrayConsultaOr = []
consultaAnd = []
removerOr = []

try:
    print('inicio')
    arqBase = open(nomeArq, "r")
    arqConsulta = open(consulta, "r")

    arquivos = arqBase.readlines()
    stringConsulta = arqConsulta.readline()
    stringConsulta.replace("\n", "")
    teste = stringConsulta.strip(" ")
    for palavra in teste:
        print(palavra, 'palavra corna')
    print(stringConsulta, 'string consulta original')
    for i in range(len(stringConsulta)):
        print(stringConsulta[i], 'string consulta na posição i')
        if stringConsulta[i] == "|":
            arrayConsultaOr.append(stringConsulta[i-1])
            arrayConsultaOr.append(stringConsulta[i+1])
        if stringConsulta[i] == "&":
            print(stringConsulta[i-1], 'i menos 1')
            arrayConsultaAnd.append(stringConsulta[i-1])
            arrayConsultaAnd.append(stringConsulta[i+1])

    print(arrayConsultaAnd, 'consulta and')
    print(arrayConsultaOr, 'consulta or')

    documentList = []
    files = []
    indiceInvertido = {}

    for i in range(len(arquivos)):
        files.append(arquivos[i].replace('\n', ''))
        palavras = open(arquivos[i].replace('\n', '')).readlines()
        aux = list(set(nltk.word_tokenize("".join(palavras))).difference(palavrasRemovidas))
        print(aux, 'aux')
        criaIndiceInvertido(indiceInvertido, aux, i)

    lista = list(indiceInvertido.keys())

    print(pesquisaPalavra(indiceInvertido, "W", arquivos), 'pesquisa palavra')
    listaPesos = []
    for termo in range(len(lista)):
        ni = len(indiceInvertido[lista[termo]])
        for i in range(len(files)):
            if i >= len(listaPesos):
                listaPesos.append({})
            if listaPesos[i].get(termo+1) == None:
                if indiceInvertido[lista[termo]].get(i+1) != None:
                    tf_idf = (1+ math.log10(indiceInvertido[lista[termo]][i+1])) * (math.log10(len(files)/ni))
                    listaPesos[i][termo+1] = tf_idf
                else:
                    listaPesos[i][termo+1] = 0
    print(listaPesos)
    print(indiceInvertido)
    
    arqBase.close()

except Exception as e:
    print (e)
