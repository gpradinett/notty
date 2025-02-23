import yt_dlp
from abc  import ABC, abstractmethod
from urllib.parse import urlparse
import re
import os
from fastapi import HTTPException


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
        ydl_opts_info = {
            "noplaylist": True,
            "extractor_args": {"kick": {"impersonate": "chrome"}},
            "http_headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts_info) as ydl:
                info_dict = ydl.extract_info(self.url, download=False)
                if not info_dict:
                    raise Exception("No se pudo extraer la información del video.")

                video_filename = info_dict.get("title", "Kick Video")
                clean_video_title = self.sanitize_filename(video_filename)

            video_file_path = os.path.join(DOWNLOAD_PATH, f"{clean_video_title}.mp4")

            ydl_opts = {
                "format": "best",
                "outtmpl": "video.mp4",
                "extractor_args": {
                    "kick": {"impersonate": "chrome"}
                },
                "http_headers": {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, como Gecko) Chrome/120.0.0.0 Safari/537.36"
                }
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.url])

            if not os.path.exists(video_file_path):
                raise Exception("El archivo no fue descargado correctamente.")

            return video_file_path

        except yt_dlp.utils.DownloadError as e:
            raise Exception(f"Error al descargar el video: {e}")

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
        return kickDownloader().some_operation(url)
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
