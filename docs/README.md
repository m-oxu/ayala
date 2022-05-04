# Ayala


**Dairenkon Majime Rezende de Souza, contacts: dairenkonmajime@protonmail.com**

**Raicy Pinheiro Pantoja, contacts: raicypp@gmail.com**


---

Professores:

**Prof. Hugo Bastos de Paula**


---

_Curso de Ciência de Dados, Unidade Praça da Liberdade_

_Instituto de Informática e Ciências Exatas – Pontifícia Universidade de Minas Gerais (PUC MINAS), Belo Horizonte – MG – Brasil_

---

_**Resumo**. Escrever aqui o resumo. O resumo deve contextualizar rapidamente o trabalho, descrever seu objetivo e, ao final, 
mostrar algum resultado relevante do trabalho (até 10 linhas)._

---


## Introdução

As redes sociais se tornaram um espaço importante do fazer político. 
Os meios de comunicação antigos, apesar de utilizados ainda hoje, possuem relevância secundária na propaganda política, levantamento e discussão de pautas, organizações de atos e manifestações e local de opinião. 

###    Contextualização

Em pesquisa de opinião do Instituto DataSenado é apontado “a influência crescente das redes sociais como fonte de informação para o eleitor, o que pode em parte explicar as escolhas dos cidadãos nas eleições de 2018. Quase metade dos entrevistados (45%) afirmaram ter decidido o voto levando em consideração informações vistas em alguma rede social”.

Historicamente, os veículos de opinião foram, em muitos casos, decisivos para a vitória ou derrota dos agentes políticos em uma eleição. Um exemplo disso, foi a trajetória  de Prudencia Ayala, inspiração para nomear nosso projeto.

Prudencia Ayala foi uma figura de resistência em El Salvador. Nos anos 30, quando mulheres ainda eram proibidas de participar dos processos eleitorais, Ayala decidiu se candidatar à Presidência da República, levantando pautas sociais como o sufragismo, o sindicalismo e a garantia dos direitos sociais para a classe trabalhadora.

Como já era de se esperar, sua candidatura foi repudiada pelas parcelas privilegiadas da sociedade. No entanto, a sua aceitação entre os estudantes e os trabalhadores crescia a cada dia. Os jornais da época a taxaram de louca, feia, analfabeta e machona.

[https://www12.senado.leg.br/noticias/materias/2019/12/12/redes-sociais-influenciam-voto-de-45-da-populacao-indica-pesquisa-do-datasenado](https://www12.senado.leg.br/noticias/materias/2019/12/12/redes-sociais-influenciam-voto-de-45-da-populacao-indica-pesquisa-do-datasenado) 

###    Problema

A visualização da influência de figuras públicas ainda é um problema complexo. Muitas vezes, um alto número de seguidores e um alto número de publicações não significa uma alta relevância social. O que interessa às agências de marketing eleitoral e político é a capacidade de mobilização, visibilidade e conversão de votos da base desses seguidores. Entender como cada veículo influencia na quantidade de pessoas apoiadoras não é uma tarefa fácil, muito menos uma tarefa que deve ser baseada em concepções individuais.

O uso de sistemas inteligentes à serviço dos candidatos ainda é escasso, se não distante da realidade financeira da maioria dos partidos brasileiros. Soluções baratas e acessíveis, porém efetivas, podem ajudar a entender a aceitação de uma pessoa candidata em uma determinada região, ou plataforma, provendo uma perspectiva mais clara de alocação de investimentos e densidade de votantes.


###    Objetivo geral

O objetivo deste projeto é desenvolver um sistema inteligente, que busca analisar a aceitação nas redes sociais de pessoas pré-candidatas/candidatas à Presidência da República do Brasil no ano de 2022. 

####    Objetivos específicos

Com base nisso, determinam-se objetivos específicos:

- Análise de sentimentos expressos pelos usuários do Twitter, para aceitação dos candidatos, que podem concorrer à presidência do Brasil no ano de 2022;
- Análise de hashtags, movimentação de seguidores e agentes de influências.;
- e análise de publicações de grupos fechados do Facebook.

###    Justificativas

As equipes de comunicação têm se baseado em práticas antigas e ultrapassadas para medir a popularidade e influência das pessoas concorrendo nestas eleições. A adaptação dessas equipes para o novo contexto digital ainda é lenta. Portanto, dá-se a necessidade de se utilizar recursos de inteligência artificial que consigam analisar, estimar e prever movimentações digitais concernentes às estratégias de maximização de votos.

Cada vez mais os brasileiros estão se interessando por política, valorizando ainda mais os seus votos, e se manifestando nas redes sociais sobre algum assunto em pauta no parlamento. Visualizando essa crescente politização em território nacional esse projeto vem com um propósito de analisar as manifestações políticas dos eleitores na internet utilizando sistemas inteligentes.

##    Público alvo

O público alvo da Ayala são as agências de marketing eleitoral e político, as próprias pessoas concorrendo à cargos públicos, ou até mesmo entusiastas que desejam estudar a influência política nas redes sociais.

## Análise exploratória dos dados
O notebook contendo as análises iniciais se encontra nesse [link](https://colab.research.google.com/drive/1LnkIVCLpi72Fzu0hVsB_u8BqQ_8_IsB5?usp=sharing). 

Inicialmente, a base de dados da Ayala contém 1,417 tweets, em um dataset com três campos: *created_at* (datetime[64]), *tweet_id* (object) e *text* (object). Os tweets datam do primeiro mês do ano de 2022. A data mínima do dataset é 2022-01-04, e a data máxima é 2022-01-06. As seguintes queries estão sendo utilizadas na busca de tweets: 
- '#Lula2022 -is:retweet', 
- 'bolsonaro desonesto -is:retweet', 
- '#LulaLadrao -is:retweet', 
- '#Bolsonaro2022 -is:retweet', 
- 'fechado com bolsonaro -is:retweet', 
- 'lula ladrão roubou meu coração OR lula ladrao roubou meu coracao -is:retweet', 
- '#soujovemsoubolsonaro22 -is:retweet', 
- '#lulapalooza -is:retweet', 
- 'politica brasileira -is:retweet', 
- '#Ciro2022 -is:retweet', 
- '#SergioMoro2022 -is:retweet', 
- '#LeonardoPericlesPresidente -is:retweet', 
- '#LeoPericlesPresidente -is:retweet', 
- '#SofiaManzanoParaPresidente -is:retweet', 
- '#LeoPericles -is:retweet'. 

As queries também estão incompletas. 

## Limpeza dos dados

Como a tabela se concentra em dados textuais, foi iniciada a limpeza dos dados, retirando caracteres de novas linhas (\n), retirada de urls, pontuações, porém as hashtags e menções foram mantidas. Uma lista de stopwords contendo mais de 500 palavras foi utilizada para limpar os tweets.

A função utilizada para limpar os dados é:

```
def preprocessing_data(df):
    df = df.apply(lambda x: x.lower())
    df = df.apply(lambda x: re.sub(r"http\S+","", x))
    df = df.apply(lambda x: re.sub(r"www.\S+","", x))
    df = df.apply(lambda x: x.rstrip())
    df = df.apply(lambda x: re.sub("[^a-z0-9]"," ", x))
    df = df.apply(lambda x: x.split())
    df = df.map(lambda x: ' '.join([word for word in x if word not in (stop_port)])) 

    return df
```

Logo após foi analisada a wordcloud dos textos.

![Wordcloud](https://file.io/1EB0TAMnhO0o)

Nesses tweets de janeiro, é possível observar uma predominância de comentários positivos sobre a pré-candidatura do ex-Presidente da República Luiz Inácio da Silva. Naturalmente, essa observação é bastante enviesada pela quantidade de dados disponíveis até o momento, que não representam nem 10% da quantidade de tweets realizados na primeira semana de janeiro.

## Indução de modelos

### Modelo 1: Algoritmo

Substitua o título pelo nome do algoritmo que será utilizado. P. ex. árvore de decisão, rede neural, SVM, etc.
Justifique a escolha do modelo.
Apresente o processo utilizado para amostragem de dados (particionamento, cross-validation).
Descreva os parâmetros utilizados. 
Apresente trechos do código utilizado comentados. Se utilizou alguma ferramenta gráfica, apresente imagens
com o fluxo de processamento.

### Modelo 2: Algoritmo

Repita os passos anteriores para o segundo modelo.


## Resultados

### Resultados obtidos com o modelo 1.

Apresente aqui os resultados obtidos com a indução do modelo 1. 
Apresente uma matriz de confusão quando pertinente. Apresente as medidas de performance
apropriadas para o seu problema. 
Por exemplo, no caso de classificação: precisão, revocação, F-measure, acurácia.

### Interpretação do modelo 1

Apresente os parâmetros do modelo obtido. Tentre mostrar as regras que são utilizadas no
processo de 'raciocínio' (*reasoning*) do sistema inteligente. Utilize medidas como 
o *feature importances* para tentar entender quais atributos o modelo se baseia no
processo de tomada de decisão.


### Resultados obtidos com o modelo 2.

Repita o passo anterior com os resultados do modelo 2.

### Interpretação do modelo 2

Repita o passo anterior com os parâmetros do modelo 2.


## Análise comparativa dos modelos

Discuta sobre as forças e fragilidades de cada modelo. Exemplifique casos em que um
modelo se sairia melhor que o outro. Nesta seção é possível utilizar a sua imaginação
e extrapolar um pouco o que os dados sugerem.


### Distribuição do modelo (opcional)

Tende criar um pacote de distribuição para o modelo construído, para ser aplicado 
em um sistema inteligente.


## 8. Conclusão

Apresente aqui a conclusão do seu trabalho. Discussão dos resultados obtidos no trabalho, 
onde se verifica as observações pessoais de cada aluno.

Uma conclusão deve ter 3 partes:

   * Breve resumo do que foi desenvolvido
	 * Apresenação geral dos resultados obtidos com discussão das vantagens e desvantagens do sistema inteligente
	 * Limitações e possibilidades de melhoria


# REFERÊNCIAS

Como um projeto de sistema inteligente não requer revisão bibliográfica, 
a inclusão das referências não é obrigatória. No entanto, caso você 
tenha utilizado referências na introdução ou deseje 
incluir referências relacionadas às tecnologias, padrões, ou metodologias 
que serão usadas no seu trabalho, relacione-as de acordo com a ABNT.

Verifique no link abaixo como devem ser as referências no padrão ABNT:

http://www.pucminas.br/imagedb/documento/DOC\_DSC\_NOME\_ARQUI20160217102425.pdf

Por exemplo:

**[1]** - _ELMASRI, Ramez; NAVATHE, Sham. **Sistemas de banco de dados**. 7. ed. São Paulo: Pearson, c2019. E-book. ISBN 9788543025001._

**[2]** - _COPPIN, Ben. **Inteligência artificial**. Rio de Janeiro, RJ: LTC, c2010. E-book. ISBN 978-85-216-2936-8._

**[3]** - _CORMEN, Thomas H. et al. **Algoritmos: teoria e prática**. Rio de Janeiro, RJ: Elsevier, Campus, c2012. xvi, 926 p. ISBN 9788535236996._

**[4]** - _SUTHERLAND, Jeffrey Victor. **Scrum: a arte de fazer o dobro do trabalho na metade do tempo**. 2. ed. rev. São Paulo, SP: Leya, 2016. 236, [4] p. ISBN 9788544104514._

**[5]** - _RUSSELL, Stuart J.; NORVIG, Peter. **Inteligência artificial**. Rio de Janeiro: Elsevier, c2013. xxi, 988 p. ISBN 9788535237016._



# APÊNDICES

**Colocar link:**

Do código (armazenado no repositório);

Dos artefatos (armazenado do repositório);

Da apresentação final (armazenado no repositório);

Do vídeo de apresentação (armazenado no repositório).

