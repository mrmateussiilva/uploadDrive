import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# ============================================
# CONFIGURAÇÕES
# ============================================

PASTA_ROOT = "1TN-7mwxXRMxLezW8BZ8TlaoSORQRng85"  # ID da pasta raiz no Google Drive
SCOPES = ["https://www.googleapis.com/auth/drive"]
API_KEY = "AIzaSyCuCMYfPovTv9heHdvaAHVAJkns3dSefVk"  # <-- coloque sua API key aqui


# ============================================
# AUTENTICAÇÃO
# ============================================

def autenticar():
    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return creds


# ============================================
# PERMISSÃO: tornar o arquivo público
# ============================================

def tornar_publico(service, file_id):
    perm = {"type": "anyone", "role": "reader"}
    service.permissions().create(fileId=file_id, body=perm).execute()


# ============================================
# LISTAGEM RECURSIVA COM CAMINHO DE PASTA
# ============================================

def listar_recursivo(service, folder_id, lista, categoria_atual="Sem Categoria"):
    query = f"'{folder_id}' in parents and trashed = false"

    resultados = service.files().list(
        q=query,
        fields="files(id,name,mimeType)"
    ).execute()

    arquivos = resultados.get("files", [])

    for item in arquivos:
        mime = item["mimeType"]
        nome = item["name"]
        file_id = item["id"]

        # Se for pasta → recursão
        if mime == "application/vnd.google-apps.folder":
            nova_categoria = nome  # Nome da pasta vira categoria
            listar_recursivo(service, file_id, lista, nova_categoria)

        # Se for vídeo
        elif mime.startswith("video/"):
            lista.append({
                "id": file_id,
                "name": nome,
                "categoria": categoria_atual
            })


# ============================================
# GERAR PLAYLIST M3U
# ============================================

def gerar_m3u(lista_videos, filename="playlist.m3u"):
    conteudo = "#EXTM3U\n\n"

    for v in lista_videos:
        nome = v["name"]
        vid = v["id"]
        categoria = v["categoria"]

        # Link RAW do Google Drive via API (streaming 100% compatível)
        link = (
            f"https://www.googleapis.com/drive/v3/files/{vid}"
            f"?alt=media&key={API_KEY}"
        )

        conteudo += f'#EXTINF:-1 group-title="{categoria}",{nome}\n{link}\n\n'

    with open(filename, "w", encoding="utf-8") as f:
        f.write(conteudo)

    print(f"\n📺 Playlist gerada: {filename}")


# ============================================
# MAIN
# ============================================

if __name__ == "__main__":
    print("🔐 Autenticando...")
    creds = autenticar()
    service = build("drive", "v3", credentials=creds)

    print("🔍 Procurando vídeos no Drive (recursivo)...")
    lista_videos = []
    listar_recursivo(service, PASTA_ROOT, lista_videos)

    print(f"\n📦 {len(lista_videos)} vídeos encontrados.\n")

    print("🔓 Tornando vídeos públicos...")
    for v in lista_videos:
        print(f"- {v['name']} ({v['categoria']})")
        tornar_publico(service, v["id"])

    print("\n📄 Montando playlist M3U com categorias...")
    gerar_m3u(lista_videos)

    print("\n✨ Finalizado! Sua playlist está pronta para Smarters, TiviMate, VLC e MPV.")
