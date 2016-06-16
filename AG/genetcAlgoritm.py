'''
Created on 12 de mar de 2016

@author: Filipe Damasceno
'''
import random

from Graficos.Plotar import plotarGeracoes
from Populacao.populacao import Populacao
from individuo.Cromossomo import Cromossomo
from recurso.DBconector import DB


class AG(object):
    
    def __init__(self,ngerentes=1, nAnalistas_req=2, nArquitetos_soft=2, nProgramadores=4, nTestadores=3,\
                 Ring = 4, Lambda = 20, Taxa_CrossOver = 0.9, Taxa_mutacao = 0.04, TamanhoPop = 100,\
                 geracao_estagnada= 100, max_geracao = 100,db = DB):
        self.ngerentes = ngerentes
        self.nAnalistas_req = nAnalistas_req
        self.nArquitetos_soft = nArquitetos_soft
        self.nProgramadores = nProgramadores
        self.nTestadores = nTestadores

        self.Ring = Ring
        self.Lambda = Lambda if Lambda % 2 == 0 else Lambda+1
        self.Taxa_CrossOver = Taxa_CrossOver
        self.Taxa_mutacao = Taxa_mutacao
        self.TamanhoPop = TamanhoPop
        self.geracao_estagnada = geracao_estagnada
        self.max_geracao = max_geracao
        self.DbCon = db
        self.Codificado = [ngerentes, nAnalistas_req, nArquitetos_soft, nProgramadores, nTestadores]
        self.TamanhoCromossomo = sum([ngerentes,nAnalistas_req,nArquitetos_soft,nProgramadores,nTestadores])
        self.pop = Populacao()
        self.resultados=None
    
    def gera_populacao(self):
        ids = DB.getIdsAgente()
        vet_pop = []
        for _ in range(self.TamanhoPop):
            vet_pop.append(Cromossomo(self.TamanhoCromossomo, ids, self.Codificado))
        
        self.pop = Populacao(vet_pop)
    
    def calcFitness(self,indis=[]):
        '''
        funcao calcfitness OK
        '''
        if indis == []:
            for i in range(len(self.pop)):
                self.pop[i].calcfitness(self.DbCon)
        else:
            for i in range(len(indis)):
                indis[i].calcfitness(self.DbCon)
    
    def seleciona_pais(self):
        '''
        selecionara o numero de pais Lambda
        '''
        vetor_pais = []
        for _ in range(self.Lambda//2):
            vetor_pais.append((self.torneio(),self.torneio()))
        return vetor_pais
    
    def torneio(self):
        '''
        neste torne e retornado apartir de uma disputa/
        o melhor individuo
        '''
        ring = []
        for _ in range(self.Ring):
            individuo = random.choice(self.pop.cromossomos)
            while(individuo in ring):
                individuo = random.choice(self.pop.cromossomos)
            ring.append(individuo)
        '''
        ordena o vetor de distancias em ordem decrecente, ou seja, a maior distancia primeiro (objetivo secundario).
        ordena o vetor de rank em ordem crescente, ou seja, ordena o que tem menor rank (objetivo primario).
        '''
        ring.sort(key = lambda distancia: distancia.distancia, reverse = True) # ordenacao secundaria
        ring.sort(key = lambda rank: rank.rank)#ordenacao primaria
        
        return ring[0].copy()
    
    def crossOver(self,pais_selecionados=[]):
        '''
        eh verificada a possibilidade de ocorrer o crizamento, 
        caso ocorra o operador sobrcarregado + (soma).
        '''
        filhos = []
        for pai1,pai2 in pais_selecionados:
            if random.random() <= self.Taxa_CrossOver:
                filhos += pai1+pai2
            else:
                filhos.append(pai1)
                filhos.append(pai2)
        return filhos
    
    def mutation(self, filhos = []): 
        '''
        Mutacao com sigma e gaussiana
        funcao mutacao OK - no individuo
        ''' 
        for i in filhos:
            i.mutacao(self.Taxa_mutacao)
    
    def fast_nondominated_sort(self):
        self.pop.frentes = []
        self.pop.frentes.append([])
        
        for individuo in self.pop:
            individuo.dominados = set()
            individuo.contador_dominado = 0
            
            for outro in self.pop:
                if individuo == outro:
                    continue
                if individuo.domina(outro): #verifico se domino o outro individuo
                    individuo.dominados.add(outro)
                elif outro.domina(individuo):
                    individuo.contador_dominado += 1
            if individuo.contador_dominado == 0:
                self.pop.frentes[0].append(individuo)
                individuo.rank = 0
        
        i = 0
        while len(self.pop.frentes[i]) > 0:
            nova_frente = []
            
            for individuo in self.pop.frentes[i]:
                for outro in individuo.dominados:
                    outro.contador_dominado -= 1
                    if outro.contador_dominado == 0:
                        outro.rank = i+1
                        nova_frente.append(outro)
                        
            self.pop.frentes.append(nova_frente)
            i += 1
        
        for frente in self.pop.frentes:
            self.calculate_crowding_distance(frente)
    
    def calculate_crowding_distance(self,frente=[]):
        if len(frente) > 0:
            for individuo in frente:
                individuo.distancia = 0
            
            for objetivo in range(len(individuo.objetivos)):
                frente.sort(key=lambda c: c.objetivos[objetivo])
                frente[0].distancia = float('inf')
                frente[-1].distancia = float('inf')
                for pos in range(1,len(frente)-1):
                    frente[pos].distancia += frente[pos + 1].objetivos[objetivo] - frente[pos - 1].objetivos[objetivo]
                    
    def selection(self, filhos=[]):
        poptemp = []
        
        self.pop.cromossomos = self.pop.cromossomos + filhos
        self.fast_nondominated_sort()
        #self.pop.cromossomos.sort(key = lambda rank: rank.rank)
        
        i=0
        while len(self.pop.frentes[i])+len(poptemp) <= self.TamanhoPop:
            poptemp += self.pop.frentes[i]
            i+=1
        else:
            if len(poptemp) < self.TamanhoPop:
                self.pop.frentes[i].sort(key= lambda v: v.distancia,reverse = True)
                for j in range(self.TamanhoPop - len(poptemp)):
                    poptemp.append(self.pop.frentes[i][j])
        
        self.pop.cromossomos = poptemp
          
    
    def plotar(self):
        plotarGeracoes(self.resultados)
            
    def ag(self):
        geracaoatual = 0
        
        self.gera_populacao()
        self.calcFitness()
        self.fast_nondominated_sort()
        
        while (geracaoatual < self.max_geracao):
            pais = self.seleciona_pais()
            filhos = self.crossOver(pais)
            self.mutation(filhos)
            self.calcFitness(filhos)
            self.selection(filhos)
            geracaoatual+=1
            del filhos,pais
        self.pop.salvarfrente()
        print(self.pop.retorna_melhores(self.DbCon))
        print(self.pop.retorna_frente(self.DbCon))
        return self.pop.getDadosEstatisticos()
    
    def resultado(self,nTestes=5):
        resultados = []
        for _ in range(nTestes):
            resultados.append(self.ag())
            
        dados_curvas_execulcao =[]
        
        #plota([resultados[0][i].objetivos[0] for i in range(len(resultados[0]))],[resultados[0][i].objetivos[1] for i in range(len(resultados[0]))])
        for frente in resultados:
            ob1,ob2,ob3,ob4 = [],[],[],[]
            for individuo in frente:
                ob1.append(individuo.objetivos[0])
                ob2.append(individuo.objetivos[1])
                ob3.append(individuo.objetivos[2])
                ob4.append(individuo.objetivos[3])
            dados_curvas_execulcao.append([ob1,ob2,ob3,ob4])

        def desviop(vet=[]):
            acc = 0
            med = sum(vet)/len(vet)
            for i in vet:
                acc += (i - med)**2
            var = acc/len(vet)
            return var**0.5
            
        for i in dados_curvas_execulcao:
            for j in i:
                print("media: ",sum(j)/len(j),"desvio: ",desviop(j))
            print("#"*120)
        
        self.resultados = dados_curvas_execulcao