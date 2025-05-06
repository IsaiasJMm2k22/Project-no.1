import requests
import json
from dotenv import load_dotenv
from os import getenv



def crear_repositorio_github(nombre_repo, descripcion="", privado=False, 
                            token_acceso="", usuario=""):
    """
    Crea un nuevo repositorio en GitHub
    
    Parámetros:
    - nombre_repo: Nombre del repositorio a crear
    - descripcion: Descripción del repositorio (opcional)
    - privado: Si es True, crea un repositorio privado (por defecto es público)
    - token_acceso: Token de acceso personal de GitHub (necesario)
    - usuario: Nombre de usuario de GitHub (opcional, se usa para organizaciones)
    
    Retorna:
    - Diccionario con la respuesta de la API o mensaje de error
    """
    
    if not token_acceso:
        return {"error": "Se requiere un token de acceso personal de GitHub"}
    
    url = "https://api.github.com/user/repos"
    if usuario:
        url = f"https://api.github.com/orgs/{usuario}/repos"
    
    headers = {
        "Authorization": f"token {token_acceso}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    data = {
        "name": nombre_repo,
        "description": descripcion,
        "private": privado,
        "auto_init": True  # Inicializa con un README
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response_data = response.json()
        
        if response.status_code == 201:
            return {
                "success": True,
                "message": "Repositorio creado exitosamente",
                "data": response_data
            }
        else:
            return {
                "success": False,
                "message": f"Error al crear repositorio: {response_data.get('message', 'Error desconocido')}",
                "status_code": response.status_code,
                "data": response_data
            }
    except Exception as e:
        return {
            "success": False,
            "message": f"Excepción al intentar crear el repositorio: {str(e)}"
        }


# Ejemplo de uso
if __name__ == "__main__":
    # Configura tus credenciales aquí
    load_dotenv(".env")
    TOKEN = getenv("GITHUB_TOKEN")
    print(TOKEN)
    USUARIO = ""  # Déjalo vacío para tu usuario, o pon el nombre de una organización
    
    # Crear un repositorio público
    resultado = crear_repositorio_github(
        nombre_repo="Project no.1",
        descripcion="Repositorio creado con la API de GitHub",
        privado=False,
        token_acceso=TOKEN,
        usuario=USUARIO
    )
    
    print(resultado)