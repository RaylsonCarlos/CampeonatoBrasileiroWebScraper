from lxml import html
import requests
import xml.etree.ElementTree as ET

#ano do qual se deseja obter o arquivo XML,
#atualmente o site da CBF diponibiliza as informações de 2012~2018
ano = '2018'

#serie A ou série B que dispõem da mesma estrutura de 38 rodadas de 10 partidas
serie = 'A'

#path do arquivo de saída
pathPastaSaida = 'C:/Users/Raylson/Documents/GitHub/CampeonatoBrasileiroWebScraper/XML/'

#path do arquivo XML gerado
pathArquivoXML = pathPastaSaida+ 'CB{ano}{serie}.xml'.format(ano=ano,serie=serie)

#nome do arquivo contendo o schema
nomeArquivoXMLSchema = 'CB_v2.xsd'

#link para o site da cbf
linkCBF = 'https://www.cbf.com.br/futebol-brasileiro/competicoes/campeonato-brasileiro-serie-{serie}/{anoConsulta}'

#xPath do elemento que contém as informações da rodada
#38 rodadas no total
xPathRodada = '//*[@id="menu-panel"]/article/div[1]/div/div/section/div[2]/aside/div/div[{rodada}]'

#xPath do elemento que contém as informações de data e hora de cada partida
#10 partidas por rodada
xPathJogoDataHora = '/div/ul/li[{jogo}]/div/span[1]/text()'

#xPath do elemento que contém o nome dos time
#qualidade 1 para mandante, 2 para visitante
xPathNomeTime = '/div/ul/li[{jogo}]/div/div/a/div[{qualidade}]/img/@title'

#xPath do elemento que contém o placar do jogo
xPathPlacar = '/div/ul/li[{jogo}]/div/div/a/strong/span/text()'

#captura o arquivo html da página da cbf do ano selecionado
page = requests.get(linkCBF.format(anoConsulta=ano,serie=serie.lower()))

#cria uma árvore de elementos HTML
tree = html.fromstring(page.content)

#cria o elemento raiz do XML
cb = ET.Element('cb')
cb.set('serie',serie)
cb.set('ano',ano)
cb.set('xmlns:xsi','http://www.w3.org/2001/XMLSchema-instance')
cb.set('xsi:noNamespaceSchemaLocation', nomeArquivoXMLSchema)

#seleciona os dados do HTML e constrói os subelementos da estrutura XML
for numRodada in reversed(range(1,39)):
    rodada = ET.SubElement(cb,'rodada')
    rodada.set('n',str(numRodada))
    path = xPathRodada.format(rodada=str(numRodada))
    for numJogo in range(1,11):
        tempo = tree.xpath(path + xPathJogoDataHora.format(jogo=str(numJogo)))[0].splitlines()[1].strip()
        tempo = tempo.split(' ')
        data = tempo[1].strip().split('/')
        dia = data[0]
        mes = data[1]
        ano = data[2]
        horario = tempo[2].strip()
        horario = horario + ':00'
        tempoFormatado = ano + '-' + mes + '-' + dia + 'T' + horario

        timeMandante = tree.xpath(path + xPathNomeTime.format(qualidade='1',jogo=str(numJogo)))[0].replace(' - ','-')
        timeVisitante = tree.xpath(path + xPathNomeTime.format(qualidade='2',jogo=str(numJogo)))[0].replace(' - ','-')
        
        golsElements = tree.xpath(path + xPathPlacar.format(jogo=str(numJogo)))
        if golsElements == []:
                golsMandante = '0'
                golsVisitante = '0'
        else:
                gols = golsElements[0].split(' x ')
                golsMandante = gols[0]
                golsVisitante = gols[1]

        jogo = ET.SubElement(rodada,'jogo')
        jogo.set('horario',tempoFormatado)

        equipeMandante = ET.SubElement(jogo,'equipe')
        equipeVisitante = ET.SubElement(jogo,'equipe')
        equipeMandante.set('gols',golsMandante)
        equipeVisitante.set('gols',golsVisitante)
        equipeMandante.set('time',timeMandante)
        equipeVisitante.set('time',timeVisitante)
        equipeMandante.set('tipo','mandante')
        equipeVisitante.set('tipo','visitante')

#Transforma a estrutura XML em string e grava em disco
myXML = ET.tostring(cb, encoding='unicode')
myXMLFile = open(pathArquivoXML, 'w', encoding='utf-8')
myXMLFile.write(myXML)
myXMLFile.close()
