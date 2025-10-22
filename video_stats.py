import requests
import os
from dotenv import load_dotenv
import json
from datetime import date

load_dotenv()
CHANNEL_HANDLE = "MrBeast"
maxResults = 50

def get_playlistId():
    
    # en el bloque try intentamos ejecutar el codigo que puede generar una excepcion
    try:
        url = f"https://youtube.googleapis.com/youtube/v3/channels?part=contentDetails&forHandle={CHANNEL_HANDLE}&key={os.getenv('youtube_api_key')}"

        response = requests.get(url)
        
        response.raise_for_status()  # Verifica si la solicitud fue exitosa, mediante el codigo de estado HTTP

        data = response.json() # Convierte un objeto en un formato string de JSON

        # print(json.dumps(data, indent=4))  # Imprime el JSON de forma legible

        # data.items[0].contentDetails.relatedPlaylists.uploads # Esto es un diccionario de Python, el cual podemos acceder con las llaves
        # ["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]  # Esto es equivalente a la linea de arriba

        # Ahora para obtener los channel items, aqui obtengo las playlist de videos subidos por el canal
        channel_items = data["items"][0]
        # Ahora para obtener el playlistId de los videos subidos por el canal
        channel_playlistId = channel_items["contentDetails"]["relatedPlaylists"]["uploads"]
        # Imprimir el playlistId
        #print(channel_playlistId)

        return channel_playlistId
    
    # En except capturamos la excepcion si ocurre un error en la solicitud HTTP, raise lanza una excepcion si la respuesta HTTP indica un error
    except requests.exceptions.RequestException as e:
        raise e # Re-raise the exception for further handling if needed

# base_url = f"https://youtube.googleapis.com/youtube/v3/playlistItems?part=contentDetails&maxResults={maxResults}&playlistId=UUX6OQ3DkcsbYNE6H8uQQuVA&key={os.getenv('youtube_api_key')}"


# A esta funcion le pasamos el playlistId que obtuvimos de la funcion get_playlistId()
def get_video_ids(playlistId):
    
    video_ids = [] # Lista para almacenar los IDs de los videos
    pageToken = None # se pone none al inicio porque no hay token de pagina al principio
    base_url = f"https://youtube.googleapis.com/youtube/v3/playlistItems?part=contentDetails&maxResults={maxResults}&playlistId={playlistId}&key={os.getenv('youtube_api_key')}"
    
    try:
        while True:
            url = base_url

            if pageToken:
                url += f"&pageToken={pageToken}" # Agrega el token de pagina a la URL si existe, el &pageToken= es necesario para la paginacion en la API de YouTube
            
            response = requests.get(url)
            response.raise_for_status()  # Verifica si la solicitud fue exitosa
            data = response.json() # Convierte un objeto en un formato string de JSON

            for item in data.get("items", []): # Itera sobre los items en la respuesta JSON, el ["items"] puede no existir, por eso usamos get con un valor por defecto de lista vacia
                video_id = item["contentDetails"]["videoId"]
                video_ids.append(video_id) # Agrega el ID del video a la lista de video_ids 
            
            pageToken = data.get("nextPageToken") # Obtiene el token de la siguiente pagina, si existe  
            if not pageToken:
                break  # Si no hay token de siguiente pagina, sal del bucle

        return video_ids

    except requests.exceptions.RequestException as e:
        raise e

def extract_video_data(video_ids):
    extracted_data = []

    def batch_list(video_id_list, batch_size):
        for video_id in range(0, len(video_id_list), batch_size):
            yield video_id_list[video_id:video_id + batch_size] # Generador que devuelve lotes de IDs de videos
        # la funcion yield es similar a return, pero en lugar de devolver un valor y salir de la funcion, yield devuelve un valor y "pausa" la funcion, permitiendo que se reanude mas tarde desde donde se quedo
    "https://youtube.googleapis.com/youtube/v3/videos?part=contentDetails&part=snippet&part=statistics&id=0e3GPea1Tyg&key=[YOUR_API_KEY]"

    try: 
        for batch in batch_list(video_ids, maxResults):
            video_ids_str = ",".join(batch)  # Convierte la lista de IDs de videos en una cadena separada por comas
            url = f"https://youtube.googleapis.com/youtube/v3/videos?part=contentDetails&part=snippet&part=statistics&id={video_ids_str}&key={os.getenv('youtube_api_key')}"
            response = requests.get(url)
            response.raise_for_status()  # Verifica si la solicitud fue exitosa
            data = response.json() # Convierte un objeto en un formato string de JSON

            for item in data.get("items", []):
                video_id = item["id"]
                snippet = item["snippet"]
                contentDetails = item["contentDetails"]
                statistics = item["statistics"]
           
                video_data = { # diccionario con los datos extraidos del video
                    "video_id": video_id,
                    "title": snippet.get("title"),
                    "publishedAt": snippet.get("publishedAt"),
                    "duration": contentDetails.get("duration"),
                    "viewCount": statistics.get("viewCount", None),
                    "likeCount": statistics.get("likeCount", None),
                    "commentCount": statistics.get("commentCount", None)
                }
                extracted_data.append(video_data)
        
        return extracted_data

    except requests.exceptions.RequestException as e:
        raise e

def save_to_json(extracted_data):
    file_path = f"./data/YT_data_{date.today()}.json"

    with open(file_path, "w", encoding="utf-8") as json_outfile:
        json.dump(extracted_data, json_outfile, ensure_ascii=False, indent=4)
# .dump convierte un objeto de Python en una cadena JSON y la escribe en un archivo
# en esta funcion se guarda la data extraida en un archivo JSON, el nombre del archivo incluye la fecha actual
# en with se abre el archivo en modo escritura ("w") y con codificacion UTF-8
# with statement es un context manager que asegura que el archivo se cierre correctamente despues de usarlo, incluso si ocurre un error durante la escritura

if __name__ == "__main__":
    # print('get_playlistId() será ejecutado')
    playlistId = get_playlistId()
    video_ids = get_video_ids(playlistId)
    video_data = extract_video_data(video_ids)
    save_to_json(video_data)
# este if sirve para que el codigo dentro de el solo se ejecute cuando se corre este archivo directamente, y no cuando se importa como un modulo en otro archivo
# else:
  #  print('get_playlistId() no será ejecutado')