import pandas as pd
from pysentimiento import create_analyzer

sentiment_analyzer = create_analyzer(task="sentiment", lang="es")
emotion_analyzer = create_analyzer(task="emotion", lang="es")

def split_text(text, chunk_size=256):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

def average_sentiment(text):
    total_sentiment_emotion = {'POS': 0.0, 'NEG': 0.0, 'NEU': 0.0,
                               'joy': 0.0, 'others': 0.0, 'surprise': 0.0, 
                               'disgust': 0.0, 'sadness': 0.0, 'fear': 0.0, 'anger': 0.0}

    chunks = split_text(text)
    count = len(chunks)
    if count == 0:
        return total_sentiment_emotion
    
    for chunk in chunks:
        sentiment_output = sentiment_analyzer.predict(chunk)
        emotion_output = emotion_analyzer.predict(chunk)

        total_sentiment_emotion['POS'] += sentiment_output.probas['POS']
        total_sentiment_emotion['NEG'] += sentiment_output.probas['NEG']
        total_sentiment_emotion['NEU'] += sentiment_output.probas['NEU']

        total_sentiment_emotion['joy'] += emotion_output.probas.get('joy', 0.0)
        total_sentiment_emotion['others'] += emotion_output.probas.get('others', 0.0)
        total_sentiment_emotion['surprise'] += emotion_output.probas.get('surprise', 0.0)
        total_sentiment_emotion['disgust'] += emotion_output.probas.get('disgust', 0.0)
        total_sentiment_emotion['sadness'] += emotion_output.probas.get('sadness', 0.0)
        total_sentiment_emotion['fear'] += emotion_output.probas.get('fear', 0.0)
        total_sentiment_emotion['anger'] += emotion_output.probas.get('anger', 0.0)

    return {metric: total_sentiment_emotion[metric] / count for metric in total_sentiment_emotion}

df = pd.read_csv('discursos_sample.csv') # .sample(n=100)
res = df['discurso'].apply(average_sentiment).apply(pd.Series)
df = pd.concat([df, res], axis=1)
df.to_csv('discursos_sentimientos.csv', sep=',', index=False)