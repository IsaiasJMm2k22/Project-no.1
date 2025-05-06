import base64
import requests
from os import getenv
from pathlib import Path
from dotenv import load_dotenv


def upload_files(
        token: str, 
        repo_owner: str, 
        repo_name: str, 
        archives: str, 
        mensaje_commit: str="Subida automática de archives", 
        branch: str="main"
        ):

    base_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    results = []
    errors = []
    
    for archive in archives:
        try:
            path = archive['path']
            content = archive['content']
            encoding = archive.get('encoding', 'utf-8')
            
            # Codificar contenido según especificación
            if encoding.lower() == 'base64':
                encoded_content = content  # Asume que ya viene en base64
            else:
                encoded_content = base64.b64encode(content.encode(encoding)).decode('utf-8')
            
            data = {
                "message": mensaje_commit,
                "content": encoded_content,
                "branch": branch
            }
            
            # Verificar si el archive existe para actualizar (necesita sha)
            check_url = base_url + path
            response = requests.get(check_url, headers=headers)
            
            if response.status_code == 200:
                data["sha"] = response.json()["sha"]
            
            # Subir/actualizar archive
            upload_url = base_url + path
            response = requests.put(upload_url, headers=headers, json=data)
            
            if response.status_code in [200, 201]:
                results.append({
                    "path": path,
                    "status": "success",
                    "response": response.json()
                })
            else:
                errors.append({
                    "path": path,
                    "status": "error",
                    "error": response.json(),
                    "status_code": response.status_code
                })
                
        except Exception as e:
            errors.append({
                "path": archive.get('path', 'desconocido'),
                "status": "exception",
                "error": str(e)
            })
    
    return {
        "success": len(errors) == 0,
        "results": results,
        "errors": errors,
        "total_subidos": len(results),
        "total_errores": len(errors)
    }


# Función auxiliar para preparar archives desde el sistema de archives
def get_files(local_directory, directorio_remoto=""):
    archives = []
    local_directory = Path(local_directory)
    
    for item in local_directory.rglob('*'):
        if item.is_file():
            # Calcular ruta relativa
            rel_path = item.relative_to(local_directory)
            remote_path = str(Path(directorio_remoto) / rel_path) if directorio_remoto else str(rel_path)
            
            # Leer contenido
            with open(item, 'r', encoding='utf-8') as f:
                content = f.read()
            
            archives.append({
                'path': remote_path.replace('\\', '/'),  # Usar / para GitHub
                'content': content,
                'encoding': 'utf-8'
            })
    
    return archives


# Ejemplo de uso
if __name__ == "__main__":
    load_dotenv(".env")
    # Configuración
    TOKEN = getenv("GITHUB_TOKEN")
    print(f"Token: {TOKEN}")
    REPO_OWNER = "IsaiasJMm2k22"
    REPO_NAME = "Project-no.1"
    
    # Opción 2: Subir archives desde un directorio local
    local_files = get_files("mcp", "mcp")
    resultado = upload_files(TOKEN, REPO_OWNER, REPO_NAME, local_files)
    print(resultado)