from __future__ import division
import sys
import math
import nltk
import string
import re
from unicodedata import normalize
from nltk import ngrams
from collections import Counter

stopwords = nltk.corpus.stopwords.words
stopwords = nltk.corpus.stopwords.words("portuguese")

nomeArq = sys.argv[1]
consulta = sys.argv[2]
stopwords = nltk.corpus.stopwords.words("portuguese")

tokenize = lambda doc: doc.lower().split(" ")

def criaIndiceInvertido(indice, texto, i):
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

def transformArray (texto):
    array = []
    for palavra in texto:
        array.append(palavra)
    return array

def gravaArquivoPeso(pesos, arquivos):
    arqPeso = open('pesos.txt','w')
    for pes in range(0, len(pesos)) :
        arqPeso.write(arquivos[pes] + ':')
        for term in pesos[pes]:
            if pesos[pes][term] != 0:
                arqPeso.write(' ' + str(term) + ',' + str(pesos[pes][term]))
        arqPeso.write('\n')

#Regex para encontrar tokens
REGEX_WORD = re.compile(r'\w+')

#Numero de tokens em sequencia
N_GRAM_TOKEN = 3

#Faz a normalizacao do texto removendo espacos a mais e tirando acentos
def text_normalizer(src):
    return re.sub('\s+', ' ',
                normalize('NFKD', src)
                   .encode('ASCII','ignore')
                   .decode('ASCII')
           ).lower().strip()

#Faz o calculo de similaridade baseada no coseno
def cosine_similarity(vec1, vec2):
    intersection = set(vec1.keys()) & set(vec2.keys())
    numerator = sum([vec1[x] * vec2[x] for x in intersection])

    sum1 = sum([vec1[x]**2 for x in vec1.keys()])
    sum2 = sum([vec2[x]**2 for x in vec2.keys()])
    denominator = math.sqrt(sum1) * math.sqrt(sum2)

    if not denominator:
        return 0.0
    else:
        coef = float(numerator) / denominator
        if coef > 1:
            coef = 1
        return coef

#Monta o vetor de frequencia da sentenca
def sentence_to_vector(text, use_text_bigram):
    words = REGEX_WORD.findall(text)
    accumulator = []
    for n in range(1,N_GRAM_TOKEN):
        gramas = ngrams(words, n)
        for grama in gramas:
            accumulator.append(str(grama))

    if use_text_bigram:
        pairs = obtem_bigramas_texto(text)
        for pair in pairs:
            accumulator.append(pair)

    return Counter(accumulator)

#Obtem a similaridade entre duas sentencas
def obtem_similaridade(sentence1, sentence2, use_text_bigram=False):
    vector1 = sentence_to_vector(text_normalizer(sentence1), use_text_bigram)
    vector2 = sentence_to_vector(text_normalizer(sentence2), use_text_bigram)
    return cosine_similarity(vector1, vector2)

#Metodo de gerar bigramas de uma string
def obtem_bigramas_texto(src):
    s = src.lower()
    return [s[i:i+2] for i in range(len(s) - 1)]

palavrasRemovidas = palavrasToRemove()
palavrasRemovidas.append("&")
arrayConsulta = []
arrayConsultaAnd = []
arrayConsultaOr = []
consultaAnd = []
removerOr = []

try:
    arqBase = open(nomeArq, "r")
    arqConsulta = open(consulta, "r")

    arquivos = arqBase.readlines()
    stringConsulta = arqConsulta.read()
    arrayPalavras = transformArray(stringConsulta.split())

    for i in range(len(arrayPalavras)):
        if arrayPalavras[i] == "|":
            arrayConsultaOr.append(arrayPalavras[i-1])
            arrayConsultaOr.append(arrayPalavras[i+1])
        if arrayPalavras[i] == "&":
            arrayConsultaAnd.append(arrayPalavras[i-1])
            arrayConsultaAnd.append(arrayPalavras[i+1])
            
    documentList = []
    arq = []
    indiceInvertido = {}

    for i in range(len(arquivos)):
        arq.append(arquivos[i].replace('\n', ''))
        palavras = open(arquivos[i].replace('\n', '')).readlines()
        aux = list(set(nltk.word_tokenize("".join(palavras))).difference(palavrasRemovidas))
        criaIndiceInvertido(indiceInvertido, aux, i)

    lista = list(indiceInvertido.keys())

    listaPesos = []
    for termo in range(len(lista)):
        ni = len(indiceInvertido[lista[termo]])
        for i in range(len(arq)):
            if i >= len(listaPesos):
                listaPesos.append({})
            if listaPesos[i].get(termo+1) == None:
                if indiceInvertido[lista[termo]].get(i+1) != None:
                    tf_idf = (1+ math.log10(indiceInvertido[lista[termo]][i+1])) * (math.log10(len(arq)/ni))
                    listaPesos[i][termo+1] = tf_idf
                else:
                    listaPesos[i][termo+1] = 0
    gravaArquivoPeso(listaPesos,arq)

    listaIndices = []
    cutoff = 0.001
    palavraAnd = " ".join(arrayConsultaAnd)

    for i in range(len(arquivos)):
        print(listaPesos[i], 'lista Peso posição i')
        texto = open(arquivos[i].replace('\n', '')).readlines()
        aux = " ".join(set(nltk.word_tokenize("".join(texto))).difference(palavrasRemovidas))

        print(aux)
        
        #Calculo usando similaridade do coseno com apenas tokens
        sentenca_similar = obtem_similaridade(aux, palavraAnd)
        print('\tSimilarity sentence: ' + str(sentenca_similar))

        #Calculo usando similaridade do coseno com tokens e com ngramas do texto
        sentenca_similaridade_texto_bigrama = obtem_similaridade(aux, palavraAnd, use_text_bigram=True)
        print('\tSimilarity sentence: ' + str(sentenca_similaridade_texto_bigrama))

        if sentenca_similar >= cutoff:
            listaIndices.append((palavraAnd, sentenca_similar))

    print(listaIndices)


    arqBase.close()

except Exception as e:
    print (e)
