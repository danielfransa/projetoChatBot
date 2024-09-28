from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
from wordcloud import WordCloud
from goose3 import Goose
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.sum_basic import SumBasicSummarizer
import matplotlib.pyplot as plt
import spacy
import nltk
from spacy.matcher import PhraseMatcher 
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

root = Tk()
 
class Application():
  def __init__(self):
    self.root = root
    self.screen()
    self.frames()
    self.widgets_frame1()
    self.widgets_frame2()
    self.widgets_frame3()
    root.mainloop()

  def screen(self):
    self.root.title("Projeto ChatBot")
    self.root.configure(background='#1e3743')
    self.root.geometry("1200x1000")
    self.root.resizable(True, True)
    self.root.maxsize(width=1400, height=1200)
    self.root.minsize(width=400, height=200)

  def frames(self):
    # Frame 1: Entrada do usuário
    self.frame_1 = Frame(self.root, bd=4, bg='#dfe3ee', highlightbackground='#759fe6', highlightthickness=2)
    self.frame_1.place(relx=0.03, rely=0.02, relwidth=0.94, relheight=0.15)

    # Frame 2: Nuvem de palavras
    self.frame_2 = Frame(self.root, bd=4, bg='#dfe3ee', highlightbackground='#759fe6', highlightthickness=2)
    self.frame_2.place(relx=0.03, rely=0.18, relwidth=0.94, relheight=0.3)

    # Frame 3: Chat
    self.frame_3 = Frame(self.root, bd=4, bg='#dfe3ee', highlightbackground='#759fe6', highlightthickness=2)
    self.frame_3.place(relx=0.03, rely=0.49, relwidth=0.94, relheight=0.5)

  def widgets_frame1(self):
    # Título e instruções
    Label(self.frame_1, text="Escolha um assunto do seu interesse para conversar com o chatbot:", bg='#dfe3ee', font=('Arial', 12, 'bold')).place(relx=0.25, rely=0.0)

    # Entrada para o link
    Label(self.frame_1, text="Link:", bg='#dfe3ee', font=('Arial', 10)).place(relx=0.01, rely=0.3)
    self.entry_link = Entry(self.frame_1, width=90)
    self.entry_link.place(relx=0.1, rely=0.3)

    # Opção de idioma
    Label(self.frame_1, text="Idioma:", bg='#dfe3ee', font=('Arial', 10)).place(relx=0.01, rely=0.7)
    self.lang_var = StringVar(value='portugues')
    Radiobutton(self.frame_1, text="Português", variable=self.lang_var, value='portugues', bg='#dfe3ee').place(relx=0.1, rely=0.7)
    Radiobutton(self.frame_1, text="Inglês", variable=self.lang_var, value='ingles', bg='#dfe3ee').place(relx=0.2, rely=0.7)

    # Botão de processar
    self.btn_processar = Button(self.frame_1, text="Processar", font=('Arial', 10), command=self.processar)
    self.btn_processar.place(relx=0.75, rely=0.65)

  def widgets_frame2(self):
    # Nuvem de palavras
    Label(self.frame_2, text="Nuvem de Palavras:", bg='#dfe3ee', font=('Arial', 12, 'bold')).place(relx=0.01, rely=0.0)
    self.canvas_nuvem = Canvas(self.frame_2, bg='white')
    self.canvas_nuvem.place(relx=0.03, rely=0.15, relwidth=0.94, relheight=0.80)

  def widgets_frame3(self):
    # Chat
    Label(self.frame_3, text="Chat:", bg='#dfe3ee', font=('Arial', 12, 'bold')).place(relx=0.01, rely=0.0)
    self.text_resultados = Text(self.frame_3)
    self.text_resultados.place(relx=0.03, rely=0.05, relwidth=0.94, relheight=0.80)
    self.entry_termo_busca = Entry(self.frame_3, width=107)
    self.entry_termo_busca.place(relx=0.03, rely=0.9)
    # Botão para fazer a pergunta do termo ao chat
    self.btn_buscar = Button(self.frame_3, text="Enviar", font=('Arial', 10), command=self.fazer_pergunta)
    self.btn_buscar.place(relx=0.908, rely=0.89)
  
  def processar(self):
    url = self.entry_link.get()
    g = Goose()
    self.article = g.extract(url)
    self.gerar_nuvem(self.article.cleaned_text)

    # Prepara as sentenças para o chatbot
    self.original_sentences = [sentence for sentence in nltk.sent_tokenize(self.article.cleaned_text)]

  def gerar_nuvem(self, texto):
    nlp = spacy.load("en_core_web_md") if self.lang_var.get() == 'ingles' else spacy.load("pt_core_news_md")
    cleaned_text = self.preprocessing(texto, nlp)

    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(cleaned_text)
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')

    plt.savefig("nuvem.png", format="png")
    imagem = Image.open("nuvem.png")
    imagem = imagem.resize((800, 150), Image.Resampling.LANCZOS)
    self.nuvem_img = ImageTk.PhotoImage(imagem)
    self.canvas_nuvem.create_image(0, 0, anchor=NW, image=self.nuvem_img)

  def preprocessing(self, sentence: str, nlp) -> str:
    sentence = sentence.lower()
    tokens = [token.text for token in nlp(sentence) if not (token.is_stop or token.like_num or token.is_punct or token.is_space or len(token) == 1)]
    return ' '.join(tokens)
  
  
  def fazer_pergunta(self):
      pergunta = self.entry_termo_busca.get()
      resposta = self.answer(pergunta)
      self.text_resultados.insert(END, f"Você: {pergunta}\n")
      self.text_resultados.insert(END, f"Chatbot: {resposta}\n\n")

  def answer(self, user_text, threshold=0.1):
      # Limpa as sentenças
      cleaned_sentences = []
      nlp = spacy.load("en_core_web_md") if self.lang_var.get() == 'ingles' else spacy.load("pt_core_news_md")
      for sentence in self.original_sentences:
          cleaned_sentences.append(self.preprocessing(sentence, nlp))

      # Preprocessa a pergunta do usuário
      user_text = self.preprocessing(user_text, nlp)
      cleaned_sentences.append(user_text)

      # Calcula a similaridade usando TF-IDF
      tfidf = TfidfVectorizer()
      x_sentences = tfidf.fit_transform(cleaned_sentences)
      similarity = cosine_similarity(x_sentences[-1], x_sentences)

      sentence_index = similarity.argsort()[0][-2]  # A segunda maior correspondência

      chatbot_answer = ''
      if similarity[0][sentence_index] < threshold:
          chatbot_answer += 'Desculpe, não encontrei uma resposta.'
      else:
          chatbot_answer += self.original_sentences[sentence_index]

      return chatbot_answer

Application()