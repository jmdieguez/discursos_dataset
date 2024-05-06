import pandas as pd
import matplotlib.pyplot as plt

# Leer el archivo CSV
df = pd.read_csv('discursos_sentimientos.csv')

# Convertir la columna 'fecha' al tipo de dato fecha
df['fecha'] = pd.to_datetime(df['fecha'], dayfirst=True)

# Obtener la lista de oradores únicos
oradores = df['orador'].unique()

# Para cada orador, generar un gráfico separado
for orador in oradores:
    nombre_graf = 'polaridad'
    for cols in [['POS', 'NEG', 'NEU'], ['joy', 'others', 'surprise', 'disgust', 'sadness', 'fear', 'anger']]:
        df_orador = df[df['orador'] == orador]
        df_orador.set_index('fecha', inplace=True)
        fig, ax = plt.subplots(figsize=(10, 6))
        df_orador[cols].plot(ax=ax, title=orador)
        ax.set_ylabel('Media')
        ax.grid(True)
        plt.savefig(f'app/public/images/{orador}_{nombre_graf}.png')
        nombre_graf = 'emociones'
        plt.show()
