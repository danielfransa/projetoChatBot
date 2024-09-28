import spacy
import en_core_web_md
import nltk
from goose3 import Goose
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


nlp=spacy.load('en_core_web_md')
nltk.download('punkt')

g=Goose()
url='https://en.wikipedia.org/wiki/Natural_language_processing'
article=g.extract(url)

original_sentences = [sentence for sentence in nltk.sent_tokenize(article.cleaned_text)]

#Limpeza e processamento das frases
def preprocessing(sentence):
  sentence = sentence.lower() #tudo minúsculas

  tokens = []
  tokens = [token.text for token in nlp(sentence) if not (token.is_stop or token.like_num
                                                          or token.is_punct or token.is_space
                                                          or len(token)==1)]
  tokens=' '.join([element for element in tokens])
  return tokens

#função para comparar a pergunta do usuário com a base de conhecimento do sistema

def answer(user_text, threshold = 0.1):
  #Limpa as sentenças
  cleaned_sentences = []
  #preprocessar a base de conhecimento para retirar pontuação, stopwords...
  for sentence in original_sentences:
    cleaned_sentences.append(preprocessing(sentence))

  #o texto do usuário também será preprocessado e adicionado a lista que
  #contém a base de conhecimento (na ultima posição da lista)
  user_text = preprocessing(user_text)
 
  cleaned_sentences.append(user_text)

  #criando a variável e efetuando a extração dos índices TF-IDF das sentenças
  tfidf = TfidfVectorizer()
  x_sentences = tfidf.fit_transform(cleaned_sentences)

  #calculando a similaridade entre a última posição das sentenças (pergunta do usuário)
  #e todas as outras sentenças disponíveis (base de conhecimento)
  similarity = cosine_similarity(x_sentences[-1], x_sentences)

  sentence_index = similarity.argsort()[0][-2] #a segunda maior correspondência
  #print(sentence_index)
  #print(similarity[0][sentence_index])

  chatbot_answer = ''

  #se a similaridade for menor que o limiar estabelecido
  if similarity[0][sentence_index] < threshold:
    chatbot_answer += 'sorry, no answer was found'

  else:
    chatbot_answer += original_sentences[sentence_index]

  return chatbot_answer


pergunta = input("Digite sua pergunta: ")

print(answer(pergunta))