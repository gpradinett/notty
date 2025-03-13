import yt_dlp
from abc  import ABC, abstractmethod
from urllib.parse import urlparse
import re
import os
from fastapi import HTTPException
import subprocess
import cloudscraper

DOWNLOAD_PATH = "./downloads"
if not os.path.exists(DOWNLOAD_PATH):
    os.makedirs(DOWNLOAD_PATH)

cookies_file = os.path.join(os.getcwd(), "static", "cookies.txt")
print ("coookis", cookies_file)


class Downloader(ABC):
    """
    Clase abstracta que define la interfaz de los descargadores.
    """
    @abstractmethod
    def factory_method(self):
        """
        Método abstracto que descarga el contenido.
        """
        pass
    
    def some_operation(self, url: str) -> str:
        """
        Método común a todos los descargadores.
        """
        print("Operación común a todos los descargadores")
        product = self.factory_method(url)
        result = product.operation()
        return result
    
    
    def sanitize_filename(self, filename: str) -> str:
        """
        Método para sanitizar el nombre del archivo, reemplazando caracteres no válidos.
        """
        filename = filename[:100]
        #print(f"Nombre 0.1 del archivo original: {filename}")
        filename = filename.replace('#', '_')
        filename = re.sub(r"[^\w\s-]", "", filename)
        #print(f"Nombre 0 del archivo sanitizado: {filename}")
        ulti =  re.sub(r"[\s-]+", "_", filename)
        #print(f"Nombre 1 del archivo sanitizado: {ulti}")
        return ulti

class Product(ABC):
    """
    Clase abstracta que define la interfaz de los productos.
    """
    @abstractmethod
    def operation(self):
        """
        Método abstracto que realiza una operación sobre el producto.
        """
        pass


class TikTokDownloader(Downloader):
    """
    Descargador concreto que descarga videos de TikTok.
    """
    def factory_method(self, url: str) -> Product:
        print(f"Descargando video de TikTok desde la URL: {url}")
        return TikTokProduct(url)

class TikTokProduct(Product):
    """
    Producto concreto que representa un video de TikTok.
    """
    def __init__(self, url: str):
        self.url = url
        
    def operation(self) -> str:
        return self.download_video()

    def download_video(self) -> str:
        with yt_dlp.YoutubeDL({"noplaylist": True}) as ydl:
            info_dict = ydl.extract_info(self.url, download=False)
            video_filename = info_dict.get("title", "TikTok Video")
            clean_video_title = TikTokDownloader().sanitize_filename(video_filename)

        video_file_path = os.path.join(DOWNLOAD_PATH, f"{clean_video_title}.mp4")

        ydl_opts = {"format": "best", "outtmpl": video_file_path, "geo_bypass": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([self.url])

        if not os.path.exists(video_file_path):
            raise DownloadError("El archivo no fue descargado correctamente.")
        return video_file_path

class InstagramDownloader(Downloader):
    """
    Descargador concreto que descarga videos de Instagram.
    """
    def factory_method(self, url: str) -> Product:
        print(f"Descargando video de Instagram desde la URL: {url}")
        return InstagramProduct(url)

class InstagramProduct(Product):
    """
    Producto concreto que representa un video de Instagram.
    """
    def __init__(self, url: str):
        self.url = url
        
    def operation(self) -> str:
        return self.download_video()

    def download_video(self) -> str:
        with yt_dlp.YoutubeDL({"noplaylist": True}) as ydl:
            info_dict = ydl.extract_info(self.url, download=False)
            video_filename = info_dict.get("title", "Instagram Video")
            clean_video_title = InstagramDownloader().sanitize_filename(video_filename)

        video_file_path = os.path.join(DOWNLOAD_PATH, f"{clean_video_title}.mp4")

        ydl_opts = {"format": "best", "outtmpl": video_file_path, "geo_bypass": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([self.url])

        if not os.path.exists(video_file_path):
            raise DownloadError("El archivo no fue descargado correctamente.")
        return video_file_path    


class FacebookDownloader(Downloader):
    """
    Descargador concreto que descarga videos de Facebook.
    """
    def factory_method(self, url: str) -> Product:
        print(f"Descargando video de Facebook desde la URL: {url}")
        return FacebookProduct(url)

class FacebookProduct(Product):
    """
    Producto concreto que representa un video de Facebook.
    """
    def __init__(self, url: str):
        self.url = url
        
    def operation(self) -> str:
        return self.download_video()

    def download_video(self) -> str:
        with yt_dlp.YoutubeDL({"noplaylist": True}) as ydl:
            info_dict = ydl.extract_info(self.url, download=False)
            video_filename = info_dict.get("title", "Facebook Video")
            clean_video_title = FacebookDownloader().sanitize_filename(video_filename)

        video_file_path = os.path.join(DOWNLOAD_PATH, f"{clean_video_title}.mp4")

        ydl_opts = {"format": "best", "outtmpl": video_file_path, "geo_bypass": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([self.url])

        if not os.path.exists(video_file_path):
            raise DownloadError("El archivo no fue descargado correctamente.")
        return video_file_path


class YouTubeDownloader(Downloader):
    """
    Descargador concreto que descarga videos de YouTube.
    """
    def factory_method(self, url: str) -> Product:
        print(f"Descargando video de YouTube desde la URL: {url}")
        return YouTubeProduct(url)

class YouTubeProduct(Product):
    """
    Producto concreto que representa un video de YouTube.
    """
    def __init__(self, url: str):
        self.url = url
        
    def operation(self) -> str:
        return self.download_video()

    def download_video(self) -> str:
        with yt_dlp.YoutubeDL({"noplaylist": True}) as ydl:
            info_dict = ydl.extract_info(self.url, download=False)
            video_filename = info_dict.get("title", "YouTube Video")
            clean_video_title = YouTubeDownloader().sanitize_filename(video_filename)

        video_file_path = os.path.join(DOWNLOAD_PATH, f"{clean_video_title}.mp4")

        ydl_opts = {
            "format": "best",
            "outtmpl": os.path.join(DOWNLOAD_PATH, "%(title)s.%(ext)s"),
            "geo_bypass": True,
            "cookiefile": cookies_file,  # Pasar el archivo de cookies
            "limit_rate": "50K",         # Limitar velocidad de descarga a 50 KB/s
            "sleep_requests": 2,         # Esperar 2 segundos entre solicitudes
            "sleep_interval": 5          # Esperar 5 segundos entre descargas
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([self.url])

        if not os.path.exists(video_file_path):
            raise DownloadError("El archivo no fue descargado correctamente.")
        return video_file_path


class XvideosDownloader(Downloader):
    """
    Descargador concreto que descarga videos de Xvideos.
    """
    def factory_method(self, url: str) -> Product:
        print(f"Descargando video de Xvideos desde la URL: {url}")
        return XvideosProduct(url)

class XvideosProduct(Product):
    """
    Producto concreto que representa un video de Xvideos.
    """
    def __init__(self, url: str):
        self.url = url
        
    def operation(self) -> str:
        return self.download_video()

    def download_video(self) -> str:
        with yt_dlp.YoutubeDL({"noplaylist": True}) as ydl:
            info_dict = ydl.extract_info(self.url, download=False)
            video_filename = info_dict.get("title", "Xvideos Video")
            clean_video_title = XvideosDownloader().sanitize_filename(video_filename)

        video_file_path = os.path.join(DOWNLOAD_PATH, f"{clean_video_title}.mp4")

        ydl_opts = {"format": "best", "outtmpl": video_file_path, "geo_bypass": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([self.url])

        if not os.path.exists(video_file_path):
            raise DownloadError("El archivo no fue descargado correctamente.")
        return video_file_path

class kickDownloader(Downloader):
    """
    Descargador concreto que descarga videos de kick.
    """
    def factory_method(self, url: str) -> Product:
        print(f"Descargando video de kick desde la URL: {url}")
        return kickProduct(url)

class kickProduct(Product):
    """
    Producto concreto que representa un video de kick.
    """
    def __init__(self, url: str):
        self.url = url
        
    def operation(self) -> str:
        return self.download_video()

    def download_video(self) -> str:
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        video_title = "Kick_Video"
        clean_video_title = video_title
        video_file_path = os.path.join(DOWNLOAD_PATH, f"{clean_video_title}.mp4")
        
        command = [
            "streamlink",
            "--http-header", f"User-Agent={user_agent}",
            self.url, "best",
            "--output", video_file_path
        ]

        try:
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode != 0:
                raise Exception(f"Error al descargar el video: {result.stderr}")

            if not os.path.exists(video_file_path):
                raise Exception("El archivo no fue descargado correctamente.")

            return video_file_path
        except Exception as e:
            raise Exception(f"Fallo en la descarga: {e}")

class kickClipDownloader(Downloader):
    """
    Descargador para clips de Kick.
    """
    def factory_method(self, url: str) -> Product:
        print(f"Descargando clip de kick desde la URL: {url}")
        return kickClipProduct(url)

def get_kick_clip_m3u8(url: str) -> str:
    """
    Extrae la URL del archivo M3U8 de un clip de Kick.
    """
    scraper = cloudscraper.create_scraper()
    response = scraper.get(url)

    match = re.search(r'(https://clips\.kick\.com/.+?/thumbnail\.webp)\\",\\"privacy\\":\\"(.*?)\\",\\"likes\\":(\d+),\\"liked\\":(true|false),\\"views\\":(\d+),\\"duration\\":(\d+),\\"started_at\\":\\"(.*?)\\",\\"created_at\\":\\"(.*?)\\",\\"vod_starts_at\\":(\d+),\\"is_mature\\":(true|false),\\"video_url\\":\\"(https://clips\.kick\.com/.+?/playlist\.m3u8)', response.text)

    print("match", match)
    if match:
    # Crear un diccionario con los datos extraídos
        data = {

            "privacy": match.group(2),
            "likes": int(match.group(3)),
            "liked": match.group(4) == "true",
            "views": int(match.group(5)),
            "duration": int(match.group(6)),
            "started_at": match.group(7),
            "created_at": match.group(8),
            "vod_starts_at": int(match.group(9)),
            "is_mature": match.group(10) == "true",
            "video_url": match.group(11).replace('\"video_url\":\"', '').rstrip('\"')
        }
        return data["video_url"]
    else:
        raise Exception("No se encontró la URL del archivo M3U8 del clip.")

class kickClipProduct(Product):
    """
    Producto concreto que representa un clip de kick.
    """
    def __init__(self, url: str):
        self.url = url

    def operation(self) -> str:
        return self.download_clip()
    
    def download_clip(self) -> str:
        print(f"Obteniendo URL M3U8 del clip: {self.url}")
        m3u8_url = get_kick_clip_m3u8(self.url)  # Extrae el link .m3u8
        print(f"URL M3U8 encontrada: {m3u8_url}")

        clip_title = "Kick_Clip"
        clean_clip_title = clip_title
        clip_file_path = os.path.join(DOWNLOAD_PATH, f"{clean_clip_title}.mp4")

        command = [
            "streamlink",
            "--http-header", "User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            m3u8_url, "best",
            "--output", clip_file_path
        ]

        try:
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode != 0:
                raise Exception(f"Error al descargar el clip con streamlink: {result.stderr}")

            if not os.path.exists(clip_file_path):
                raise Exception("El archivo del clip no fue descargado correctamente.")

            return clip_file_path
        except Exception as e:
            raise Exception(f"Fallo en la descarga del clip: {e}")


class DownloadError(HTTPException):
    def __init__(self, message: str):
        super().__init__(status_code=500, detail=message)


def get_downloader(url: str):
    """
    Método de fábrica que devuelve la función adecuada de descarga
    según el dominio de la URL.
    """
    dominio = urlparse(url).netloc
    dominio = dominio.replace("www.", "")
    
    if "tiktok" in dominio:
        # Retornar la URL de descarga
        return TikTokDownloader().some_operation(url)
    elif "facebook" in dominio:
        return FacebookDownloader().some_operation(url)
    elif "instagram" in dominio:
        return InstagramDownloader().some_operation(url)
    elif "youtube" in dominio:
        return YouTubeDownloader().some_operation(url)
    elif "youtu" in dominio:
        return TikTokDownloader().some_operation(url)
    elif "xvideos" in dominio:
        return XvideosDownloader().some_operation(url)
    elif "kick" in dominio:
        if "/videos/" in url:
            return kickDownloader().some_operation(url)
        elif "/clips/" in url:
            return kickClipDownloader().some_operation(url)
    elif "platzi" in dominio:
        return TikTokDownloader().some_operation(url)
    elif "pornhub" in dominio:
        return TikTokDownloader().some_operation(url)
    elif "peladas69" in dominio:
        return TikTokDownloader().some_operation(url)
    elif "es.xhamster" in dominio:
        return TikTokDownloader().some_operation(url)
    elif "twitter" in dominio:
        return TikTokDownloader().some_operation(url)
    elif "linkedin" in dominio:
        return TikTokDownloader().some_operation(url)
    elif "vimeo" in dominio:
        return TikTokDownloader().some_operation(url)
    elif "threads" in dominio:
        return TikTokDownloader().some_operation(url)
    elif "pornotube" in dominio:
        return TikTokDownloader().some_operation(url)
    else:
        raise ValueError(f"Dominio no soportado: {dominio}")
