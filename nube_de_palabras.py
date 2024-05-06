import os
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import nltk
from nltk.corpus import stopwords
from textblob import TextBlob

nltk.download('punkt')
nltk.download('stopwords')
stop_words = set(stopwords.words('spanish'))
data = pd.read_csv('discursos.csv')
oradores_unicos = data['orador'].unique()
plt.figure(figsize=(10, 5))

directorio_img = os.path.join(os.getcwd(), 'app/public/images')

def guardar_todas_las_palabras(orador, texto):
    WordCloud(width=800, height=400, background_color='white') \
        .generate(texto).to_file(os.path.join(directorio_img, f"{orador}_palabras.png"))

def guardar_palabras_sentimentales(orador, palabras):
    polaridades = [TextBlob(palabras).sentiment.polarity for palabras in palabras]
    palabras_sentimentales = [palabra for palabra, polaridad in zip(palabras, polaridades) if polaridad != 0]
    texto_sentimental = ' '.join(palabras_sentimentales)
    
    WordCloud(width=800, height=400, background_color='white') \
        .generate(texto_sentimental).to_file(os.path.join(directorio_img, f"{orador}_palabras_sentimentales.png"))

for orador in oradores_unicos:
    discursos_orador = data[data['orador'] == orador]['discurso']
    texto = ' '.join(discursos_orador).lower()
    tokens = nltk.word_tokenize(texto, "spanish")
    palabras_filtradas = [palabra.lower() for palabra in tokens if palabra.lower() not in stop_words]
    texto_filtrado = ' '.join(palabras_filtradas)

    guardar_todas_las_palabras(orador, texto_filtrado)
    guardar_palabras_sentimentales(orador, palabras_filtradas)