from fastapi import FastAPI, Query
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.requests import Request
import yt_dlp
import re, os
from fastapi.staticfiles import StaticFiles


app = FastAPI()

# Directorio de plantillas HTML
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


# Ruta de descarga temporal
DOWNLOAD_PATH = "./downloads"
if not os.path.exists(DOWNLOAD_PATH):
    os.makedirs(DOWNLOAD_PATH)

# Ruta dinámica para diferentes secciones
@app.get("/{section_name}", response_class=HTMLResponse)
async def render_section(request: Request, section_name: str):
    # Mapeo de secciones a plantillas
    templates_map = {
        "save": "save.html",
        "remix": "remix.html",
        "settings": "settings.html",
        "donate": "donate.html",
        "updates": "updates.html",
        "about": "about.html",
    }
    template = templates_map.get(section_name, "404.html")
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
