import os
import pandas as pd
from googleapiclient.discovery import build
from dotenv import load_dotenv
import google.generativeai as genai
import re

#--CARGAR VARIABLES DE ENTORNO---
load_dotenv("api_key_gemini.env") #Clave api en el archivo .env
load_dotenv("api_key_youtube.env")

#--CONFIGURACION--
YOUTUBE_API_KEY=os.getenv("YOUTUBE_API_KEY")
GEMINI_API_KEY=os.getenv("GEMINI_API_KEY")
VIDEO_ID="mm8c6kKK40c"
  
#--Conectar a youtube y gemini
youtube=build("youtube","v3",developerKey=YOUTUBE_API_KEY)
genai.configure(api_key=GEMINI_API_KEY)
modelo=genai.GenerativeModel("models/gemini-1.5-flash")


#--FUNCIONES DEL SCRIPT
def obtener_titulo_video(video_id):
    try:
         respuesta=youtube.videos().list(
                part="snippet",id=video_id
          ).execute()
         if respuesta["items"]:
            return respuesta["items"][0]["snippet"]["title"]
    except Exception as e:
        print(f"Error al obtener el titulo: {e}")
    return "Título no encontrado" 
    
def obtener_comentarios(video_id,max_results=100):
    comentarios=[]
    next_page_token=None
    
    while len(comentarios) < max_results:
        respuesta=youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=min(100,max_results-len(comentarios)),
            pageToken=next_page_token,
            textFormat="plainText"
        ).execute()
        
        for item in respuesta["items"]:
            comentario= item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
            comentarios.append(comentario)
            
        next_page_token=respuesta.get("nextPageToken")
        if not next_page_token:
            break
    return comentarios
    
def analizar_con_ia(comentarios):
        prompt= f"""
        Eres un analista de datos experto en detectar patrones en comentarios de Youtube.
        Te pasare una lista de comentarios. Tus tareas son:
        1. Entender el contexto general.
        2. Detectar menciones a videojuegos, incluso si estan mal escritos
        3. Devolver una lista de los juegos más pedidos o mencionados, ordenados por frecuencia (sin texto adicional) en este formato exacto :
        -Nombre del juego (número de menciones)
        
        Comentarios:
        {comentarios}
        
        Devuelve solo la lista de juegos mas pedidos o mencionados. Añade entre paréntesis cuantas veces fue mencionado cada uno.
        """
        try:
             respuesta= modelo.generate_content(prompt)
             if hasattr(respuesta,"text"):
                 return respuesta.text
        except Exception as e:
            print(f"Error al procesar con IA {e}")
        return ""
    

    
def procesar_resultado(resultados):
    """
    Convierte el texto analizado por IA en un diccionario {juego:menciones}
    """
    juegos={}
    lineas=resultados.strip().split("\n")
    for linea in lineas:
        match= re.match(r"-\s*(.+?)\s*\((\d+)",linea)
        if match:
            nombre= match.group(1).strip()
            cantidad=int(match.group(2))
            juegos[nombre]=cantidad
    return juegos

if os.path.exists('resultados_analisis_comentarios.csv'):
    df_existente=pd.read_csv('resultados_analisis_comentarios.csv')
    if VIDEO_ID in df_existente["video_id"].values:
        print("Este video ya fue procesado")
        exit()

def actualizar_csv(juegos_nuevos,titulo_video,video_id,csv_path='resultados_analisis_comentarios.csv'):
    """
    Actualiza el CSV con las nuevas menciones
    """
    if os.path.exists(csv_path):
        df=pd.read_csv(csv_path)
    else:
        df=pd.DataFrame(columns=["juego","menciones","titulo_video","video_id"])
        
    for juego,cantidad in juegos_nuevos.items():
        #Si ya existe juego + video_id sumamos
        existe=(df["juego"]==juego)&(df["video_id"]==video_id)
        if existe.any():
            df.loc[existe,"menciones"]+= cantidad
        else: 
            nueva_fila=pd.DataFrame([[juego,cantidad,titulo_video,video_id]],
                                    columns=["juego","menciones","titulo_video","video_id"])
            df=pd.concat([df,nueva_fila],ignore_index=True)
            
    df.sort_values(by="menciones",ascending=False,inplace=True)
    df.to_csv(csv_path,index=False)
    print(f"CSV actualizado:{csv_path}")
            
    
    #---EJECUCION---
if __name__== "__main__":
        print("Extrayendo comentarios")
        comentarios=obtener_comentarios(VIDEO_ID,max_results=200)
        print(f"Se extrajeron {len(comentarios)} comentarios.")
        
        #Titulo del video
        titulo_video=obtener_titulo_video(VIDEO_ID)
        print(f"\n Titulo del video: {titulo_video}")
        
        #--Limitamos solo los primeros 30 comentarios,para que no se sature
        comentarios_limitados=comentarios[:30]   
        texto_unido="\n".join(comentarios_limitados)
        
        print("Analizando con IA")
        resultados=analizar_con_ia(texto_unido)
        
        print("\n🔍 Juegos más pedidos/mencionados:\n")
        print(resultados)
        

        
#--Procesar y guardar resultados

juegos_dict=procesar_resultado(resultados)

if not juegos_dict:
    print("No se detectaron juegos. El CSV no se actualizó")
        

print("\n Juegos detectados:")
for juego,cantidad in juegos_dict.items():
    print(f"{juego} ({cantidad})")
    
actualizar_csv(juegos_dict, titulo_video, VIDEO_ID)



