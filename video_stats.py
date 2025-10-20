import requests
import os
from dotenv import load_dotenv
import json

load_dotenv()
CHANNEL_HANDLE = "MrBeast"

def get_playlistId():
    
    try:
        url = f"https://youtube.googleapis.com/youtube/v3/channels?part=contentDetails&forHandle={CHANNEL_HANDLE}&key={os.getenv('youtube_api_key')}"

        response = requests.get(url)
        
        response.raise_for_status()  # Verifica si la solicitud fue exitosa

        data = response.json() # Convierte un objeto en un formato string de JSON

        # print(json.dumps(data, indent=4))  # Imprime el JSON de forma legible

        # data.items[0].contentDetails.relatedPlaylists.uploads # Esto es un diccionario de Python, el cual podemos acceder con las llaves
        # ["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]  # Esto es equivalente a la linea de arriba

        # Ahora para obtener los channel items
        channel_items = data["items"][0]
        # Ahora para obtener el playlistId de los videos subidos por el canal
        channel_playlistId = channel_items["contentDetails"]["relatedPlaylists"]["uploads"]
        # Imprimir el playlistId
        print(channel_playlistId)

        return channel_playlistId
    
    except requests.exceptions.RequestException as e:
        raise e # Re-raise the exception for further handling if needed
    
if __name__ == "__main__":
    # print('get_playlistId() será ejecutado')
    get_playlistId()
# este if sirve para que el codigo dentro de el solo se ejecute cuando se corre este archivo directamente, y no cuando se importa como un modulo en otro archivo
# else:
  #  print('get_playlistId() no será ejecutado')