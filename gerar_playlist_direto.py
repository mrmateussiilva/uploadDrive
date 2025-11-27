import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


# ID DA PASTA PRINCIPAL NO GOOGLE DRIVE
PASTA_ROOT = "1TN-7mwxXRMxLezW8BZ8TlaoSORQRng85"  # SUBSTITUA AQUI

# Permissões completas, precisamos alterar permissões
SCOPES = ["https://www.googleapis.com/auth/drive"]


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


def tornar_publico(service, file_id):
    """Dá permissão pública (qualquer pessoa pode acessar o vídeo)."""
    perm = {"type": "anyone", "role": "reader"}

    service.permissions().create(
        fileId=file_id,
        body=perm
    ).execute()


def listar_recursivo(service, folder_id, lista_videos):
    """Lista todos os arquivos dentro da pasta (e subpastas) recursivamente."""
    query = f"'{folder_id}' in parents and trashed = false"

    resultados = service.files().list(
        q=query,
        fields="files(id,name,mimeType)"
    ).execute()

    arquivos = resultados.get("files", [])

    for item in arquivos:
        mime = item["mimeType"]

        # Se for pasta → recursão
        if mime == "application/vnd.google-apps.folder":
            listar_recursivo(service, item["id"], lista_videos)

        # Se for vídeo
        elif mime.startswith("video/"):
            lista_videos.append(item)


def gerar_m3u(lista_videos, filename="playlist.m3u"):
    conteudo = "#EXTM3U\n\n"

    for v in lista_videos:
        nome = v["name"]
        vid = v["id"]

        link = f"https://drive.google.com/uc?export=download&id={vid}"

        conteudo += f"#EXTINF:-1,{nome}\n{link}\n\n"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(conteudo)

    print(f"\n📺 Playlist gerada: {filename}")


if __name__ == "__main__":
    print("🔐 Autenticando...")
    creds = autenticar()
    service = build("drive", "v3", credentials=creds)

    print("🔍 Procurando vídeos no Drive (recursivo)...")
    lista_videos = []
    listar_recursivo(service, PASTA_ROOT, lista_videos)

    print(f"📦 {len(lista_videos)} vídeos encontrados.\n")

    print("🔓 Tornando vídeos públicos...")
    for v in lista_videos:
        print(f"- {v['name']}")
        tornar_publico(service, v["id"])

    print("\n📄 Montando playlist M3U...")
    gerar_m3u(lista_videos)

    print("\n✨ Finalizado! Envie o arquivo playlist.m3u para seu sócio testar.")
