import yt_dlp
from abc  import ABC, abstractmethod
from urllib.parse import urlparse
import re
import os
from fastapi import HTTPException


DOWNLOAD_PATH = "./downloads"
if not os.path.exists(DOWNLOAD_PATH):
    os.makedirs(DOWNLOAD_PATH)



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

    def operation(self) -> str:
        return self.download_video()


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
        return "facebook"
    elif "instagram" in dominio:
        return "instagram"
    else:
        raise ValueError(f"Dominio no soportado: {dominio}")
