import base64
import requests
from os import getenv
from pathlib import Path
import asyncio
from dotenv import load_dotenv


async def upload_files_to_github(
        token: str, 
        repo_owner: str, 
        repo_name: str, 
        files: list, 
        commit_message: str="Automatic file upload", 
        branch: str="main"
        ) -> dict:
    """
    Uploads files to a GitHub repository
    
    Args:
        token (str): GitHub personal access token
        repo_owner (str): Repository owner username or organization
        repo_name (str): Repository name
        files (list): List of files to upload
        commit_message (str): Commit message
        branch (str): Target branch
    
    Returns:
        dict: Operation results with statistics
    """
    base_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    results = []
    errors = []
    
    for file in files:
        try:
            path = file['path']
            content = file['content']
            encoding = file.get('encoding', 'utf-8')
            
            # Encode content according to specification
            if encoding.lower() == 'base64':
                encoded_content = content  # Assume already base64 encoded
            else:
                encoded_content = base64.b64encode(content.encode(encoding)).decode('utf-8')
            
            data = {
                "message": commit_message,
                "content": encoded_content,
                "branch": branch
            }
            
            # Check if file exists to update (requires sha)
            check_url = base_url + path
            response = requests.get(check_url, headers=headers)
            
            if response.status_code == 200:
                data["sha"] = response.json()["sha"]
            
            # Upload/update file
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
                "path": file.get('path', 'unknown'),
                "status": "exception",
                "error": str(e)
            })
    
    return {
        "success": len(errors) == 0,
        "results": results,
        "errors": errors,
        "uploaded_count": len(results),
        "error_count": len(errors)
    }


async def prepare_files_from_directory(
        local_directory: str, 
        remote_directory: str=""
        ) -> list:
    """
    Prepares files from a local directory for GitHub upload
    
    Args:
        local_directory (str): Path to local directory
        remote_directory (str): Base remote path (optional)
    
    Returns:
        list: List of files prepared for upload
    """
    files = []
    base_path = Path(local_directory)
    
    for item in base_path.rglob('*'):
        if item.is_file():
            # Calculate relative path
            rel_path = item.relative_to(base_path)
            remote_path = str(Path(remote_directory) / rel_path) if remote_directory else str(rel_path)
            
            # Read content
            with open(item, 'r', encoding='utf-8') as f:
                content = f.read()
            
            files.append({
                'path': remote_path.replace('\\', '/'),  # Use forward slashes for GitHub
                'content': content,
                'encoding': 'utf-8'
            })
    
    return files


async def initialize_github_upload(
        token: str,
        owner: str,
        repository_name: str,
        directory_name: str
):
    local_files = await prepare_files_from_directory(
        local_directory=directory_name, 
        remote_directory=directory_name
        )
    
    upload_result = await upload_files_to_github(
        token=token, 
        repo_owner=owner, 
        repo_name=repository_name, 
        files=local_files, 
        commit_message="Initial commit"
        )
    
    return upload_result

if __name__ == "__main__":
    load_dotenv(".env")
    
    # Configuration
    TOKEN = getenv("GITHUB_TOKEN")
    OWNER = "IsaiasJMm2k22"
    REPO = "Project-no.1"
    
    response = asyncio.run(initialize_github_upload(TOKEN, OWNER, REPO, "mcp"))