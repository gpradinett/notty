from fastapi import FastAPI, Query
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.requests import Request
import yt_dlp
import re, os
from fastapi.staticfiles import StaticFiles
import requests
from bs4 import BeautifulSoup


app = FastAPI()

# Directorio de plantillas HTML
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


# Ruta de descarga temporal
DOWNLOAD_PATH = "./downloads"
if not os.path.exists(DOWNLOAD_PATH):
    os.makedirs(DOWNLOAD_PATH)

# Ruta dinámica para diferentes secciones
@app.get("/v1/{section_name}", response_class=HTMLResponse)
async def render_section(request: Request, section_name: str):
    templates_map = {
        "save": "save.html",
        "remix": "remix.html",
        "settings": "settings.html",
        "donate": "donate.html",
        "updates": "updates.html",
        "about": "about.html",
    }
    template = templates_map.get(section_name, "404.html")
    print(f"Requested section: {section_name}, Template: {template}")
    return templates.TemplateResponse(template, {"request": request, "section": {"title": section_name}})



@app.get("/info")
async def page(request: Request, url: str = Query(None)):
    print("Accediendo a la ruta /descarga")
    clean_video_title = None
    thumbnail_url = None
    mp4_formats = None

    if url:
        try:
            # Identificar la plataforma
            platform = get_platform_from_url(url)
            
            if platform == "unknown":
                return templates.TemplateResponse(
                    "index.html", {"request": request, "error": "Unsupported platform."}
                )

            # Obtener información del video
            with yt_dlp.YoutubeDL({"noplaylist": True}) as ydl:
                info_dict = ydl.extract_info(url, download=False)
                thumbnail_url = info_dict.get("thumbnail")
                video_title = info_dict.get("title", "TikTok Video")
                clean_video_title = clean_title(video_title)
                all_formats = info_dict.get("formats")
                
                
                # Filtrar los formatos MP4
                mp4_formats = formats(all_formats)

        except Exception as e:
            return templates.TemplateResponse("index.html", {"request": request, "error": str(e)})

    return templates.TemplateResponse("index.html", {
        "request": request,
        "clean_video_title": clean_video_title,
        "thumbnail_url": thumbnail_url,
        "Url": url,
        "mp4_formats": mp4_formats if mp4_formats else None,
    })


@app.get("/tiktok")
async def tiktok(url: str = Query(...)):
    try:
        print (f"Url Obtenida: {url}")
        with yt_dlp.YoutubeDL({"noplaylist": True}) as ydl:
            
            info_dict = ydl.extract_info(url, download=False)
            thumbnail_url = info_dict.get("thumbnail")
            video_title = info_dict.get("title", "TikTok Video")
            clean_video_title = clean_title(video_title)
            all_formats = info_dict.get("formats")
            
            mp4_formats = formats(all_formats)

        return {"clean_video_title" : clean_video_title,
                "thumbnail_url" : thumbnail_url,
                "Url" : url,
                "mp4_formats": mp4_formats,
                }
    
    except Exception as e:
        raise (e)


@app.get("/download")
async def download(url: str = Query(...), clean_video_title: str = Query):
    try:
        # Ruta para el archivo descargado
        video_file_path = f"{DOWNLOAD_PATH}/{clean_video_title}.mp4"
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
            "outtmpl": video_file_path,
            "geo_bypass": True,
        }

        # Descargar el video
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            
    except Exception as e:
        raise(e)


def clean_title(title):
    # Limitar el título a 100 caracteres para evitar errores de longitud
    title = title[:100]
    # Reemplazar "#" por "_"
    title = title.replace("#", "_")
    # Eliminar emojis y caracteres especiales adicionalesu
    title = re.sub(r"[^\w\s-]", "", title)
    # Reemplazar espacios y guiones múltiples por "_"
    return re.sub(r"[\s-]+", "_", title)


def formats(formats):
    # Filtrar los formatos que sean MP4 y tengan un tamaño válido
        mp4_formats = [
            {
                "format_id": fmt["format_id"],
                "ext": fmt["ext"],
                "format_note": fmt.get("format_note", ""),
                "filesize": fmt.get("filesize"),
                "quality": fmt.get("height", fmt.get("format_note", "Video")),
            }
            for fmt in formats
            if fmt["ext"] == "mp4"
            and fmt.get("vcodec") != "none"
            and fmt.get("filesize")
        ]

        # Eliminar duplicados basados en la resolución (mayor tamaño primero)
        unique_formats = {}
        for fmt in mp4_formats:
            quality = fmt["quality"]
            if (
                quality not in unique_formats
                or fmt["filesize"] > unique_formats[quality]["filesize"]
            ):
                unique_formats[quality] = fmt
                    
        mp4_formats = list(unique_formats.values())
            
        return mp4_formats


def get_platform_from_url(url: str):
    """
    Determina la plataforma de la URL proporcionada.
    :param url: URL a analizar
    :return: Nombre de la plataforma (facebook, tiktok, instagram, youtube, etc.) o 'unknown' si no se identifica.
    """
    if "facebook.com" in url or "fb.watch" in url:
        return "facebook"
    elif "tiktok.com" in url:
        return "tiktok"
    elif "instagram.com" in url:
        return "instagram"
    elif "youtube.com" in url or "youtu.be" in url:
        return "youtube"
    else:
        return "unknown"


from fastapi.responses import JSONResponse

@app.get("/movies")
async def get_movies(url: str = Query(...)):
    """
    Obtiene la información de las películas desde la URL especificada y retorna los datos en formato JSON.
    :param url: URL a scrapear
    :return: Información de las películas en formato JSON
    """
    print(f"Obteniendo películas desde: {url}")
    try:
        # Encabezados para simular un navegador web
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        # Realizar la solicitud HTTP
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Lanza una excepción si ocurre un error
        
        # Parsear el contenido HTML
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Buscar los elementos de las películas
        elementos = soup.find_all("a", href=True)
        peliculas = []

        for elemento in elementos:
            # Verificar si contiene un <h2> con clase Title
            titulo_tag = elemento.find("h2", class_="Title")
            if not titulo_tag:
                continue  # Saltar este elemento si no tiene título

            titulo = titulo_tag.text.strip()
            enlace = elemento["href"]
            
            # Obtener el año
            year_tag = elemento.find("span", class_="Year")
            year = year_tag.text.strip() if year_tag else "No especificado"
            
            # Obtener la URL de la imagen
            img_tag = elemento.find("img")
            img_url = img_tag["data-src"] if img_tag and "data-src" in img_tag.attrs else "No disponible"
            
            # Agregar la película a la lista
            peliculas.append({
                "titulo": titulo,
                "enlace": enlace,
                "año": year,
                "imagen": img_url
            })

        return JSONResponse(content=peliculas)

    except requests.RequestException as e:
        return JSONResponse(content={"error": f"Error al realizar la solicitud: {str(e)}"})
    except Exception as e:
        return JSONResponse(content={"error": f"Error al procesar los datos: {str(e)}"})


from pydantic import BaseModel

# Modelo para recibir la URL
class MovieURL(BaseModel):
    url: str

@app.post("/scrape-movie")
async def scrape_movie(movie: MovieURL):
    url = movie.url
    print(f"Obteniendo información de la película desde: {url}")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        article = soup.find("article", class_="TPost inlist movtv-info cont")

        if article:
            img = article.find("img", {"itemprop": "image"})
            img_url = img["src"] if img else "No disponible"

            title_tag = article.find("h1", class_="Title")
            title = title_tag.text.strip() if title_tag else "No disponible"

            votes_tag = article.find("div", {"id": "TPVotes"})
            votes = votes_tag["data-percent"] if votes_tag else "No disponible"

            meta_tags = article.find("p", class_="meta")
            meta_info = [span.text for span in meta_tags.find_all("span")] if meta_tags else []
            duration = meta_info[0] if len(meta_info) > 0 else "No disponible"
            year = meta_info[1] if len(meta_info) > 1 else "No disponible"
            quality = meta_info[2] if len(meta_info) > 2 else "No disponible"

            description_tag = article.find("div", class_="Description")
            description = description_tag.find("p").text.strip() if description_tag else "No disponible"

            genre_tag = article.find("li", class_="AAIco-adjust")
            genre = genre_tag.find("a").text.strip() if genre_tag else "No disponible"

            # Buscar el div con la clase TPlayerTb Current y extraer el iframe
            player_div = soup.find("div", class_="TPlayerTb Current")
        
            if player_div:
                iframe = player_div.find("iframe")
                iframe_src = iframe["src"] if iframe else "No disponible"
                data_src = iframe["data-src"] if iframe and "data-src" in iframe.attrs else "No disponible"
                                # Imprimir resultados
                print(f"Título: {title}")
                print(f"URL de la imagen: {img_url}")
                print(f"Puntaje: {votes}")
                print(f"Duración: {duration}")
                print(f"Año: {year}")
                print(f"Calidad: {quality}")
                print(f"Género: {genre}")
                print(f"Descripción: {description}")
                print(f"src: {data_src}")
                print(f"data-src: {data_src}")
                
                return {
                    "title": title,
                    "image_url": img_url,
                    "rating": votes,
                    "duration": duration,
                    "year": year,
                    "quality": quality,
                    "genre": genre,
                    "description": description,
                    "source_url": data_src,
                }
            else:
                return {"error": "No se encontró el artículo con la clase especificada."}
        else:
            return {"error": f"Error al acceder a la página. Código de estado: {response.status_code}"}