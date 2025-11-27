import os.path
import json
from typing import List, Dict, Any, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# -----------------------------------------------------------
# CONFIGURAÇÃO
# -----------------------------------------------------------

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

FOLDERS_DRIVE = {
    "torrents": "1ngUdq4htQhyrBVs7e5Bma3AIXYl-919Q",
    "videos": "1TN-7mwxXRMxLezW8BZ8TlaoSORQRng85",
}

_service = None  # cache global


# -----------------------------------------------------------
# AUTENTICAÇÃO GOOGLE
# -----------------------------------------------------------

def autenticar():
    creds = None

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json',
                SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return creds


def get_service():
    global _service
    if _service is None:
        creds = autenticar()
        _service = build('drive', 'v3', credentials=creds)
    return _service


# -----------------------------------------------------------
# LISTAGEM / ÁRVORE
# -----------------------------------------------------------

def walk_drive(pasta_id: str, service=None) -> List[Dict[str, Any]]:
    """
    Percorre pasta recursivamente (tipo os.walk)
    """
    if service is None:
        service = get_service()

    estrutura: List[Dict[str, Any]] = []
    page_token: Optional[str] = None

    while True:
        resp = service.files().list(
            q=f"'{pasta_id}' in parents and trashed = false",
            spaces="drive",
            fields="nextPageToken, files(id, name, mimeType)",
            pageSize=1000,
            pageToken=page_token
        ).execute()

        itens = resp.get("files", [])

        for item in itens:
            node = {
                "id": item["id"],
                "name": item["name"],
                "mimeType": item["mimeType"],
                "children": []
            }

            # se for pasta → recursão
            if item["mimeType"] == "application/vnd.google-apps.folder":
                node["children"] = walk_drive(item["id"], service)

            estrutura.append(node)

        page_token = resp.get("nextPageToken")
        if not page_token:
            break

    return estrutura


def print_tree(estrutura: List[Dict[str, Any]], nivel: int = 0):
    """
    Imprime árvore no terminal (igual comando 'tree')
    """
    prefix = "   " * nivel
    for item in estrutura:
        icon = "📁" if item["mimeType"] == "application/vnd.google-apps.folder" else "📄"
        print(f"{prefix}{icon} {item['name']}")
        if item["children"]:
            print_tree(item["children"], nivel + 1)


# -----------------------------------------------------------
# FILTRAR VÍDEOS
# -----------------------------------------------------------

def collect_videos(tree: List[Dict[str, Any]], acumulador=None):
    """
    Coleta todos os arquivos de vídeo da árvore inteira.
    """
    if acumulador is None:
        acumulador = []

    for item in tree:
        if item["mimeType"].startswith("video/"):
            acumulador.append({
                "id": item["id"],
                "name": item["name"],
                "mimeType": item["mimeType"]
            })

        if item["children"]:
            collect_videos(item["children"], acumulador)

    return acumulador


# -----------------------------------------------------------
# SALVAR JSON COM A ESTRUTURA DO DRIVE
# -----------------------------------------------------------

def save_index_json(tree: List[Dict[str, Any]], filename: str = "drive_index.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(tree, f, ensure_ascii=False, indent=2)
    print(f"✅ Index salvo em {filename}")


# -----------------------------------------------------------
# MAIN
# -----------------------------------------------------------

if __name__ == '__main__':
    print("🔍 Lendo Drive, isso pode levar alguns segundos...\n")

    service = get_service()

    # 1. Monta a árvore completa da pasta "videos"
    tree = walk_drive(FOLDERS_DRIVE["videos"], service)

    # 2. Mostra no terminal
    print("📂 ESTRUTURA DA PASTA:\n")
    print_tree(tree)

    # 3. Coleta todos os vídeos
    videos = collect_videos(tree)
    print("\n🎬 VÍDEOS ENCONTRADOS:")
    for v in videos:
        print(f"- {v['name']} ({v['id']})")

    # 4. Salvar index completo
    save_index_json(tree, "drive_index.json")

    print("\n✔ Finalizado.")
