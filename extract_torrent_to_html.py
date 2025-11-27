import time
from bs4 import BeautifulSoup
import httpx
import re
import os

with open("response.html", "r", encoding="utf-8") as fp:
    data = fp.read()

headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3",
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://bj-share.info/torrents.php?searchstr=livros",
}

cookies = {
    "__cfbbid": "7786758824",
    "session": "zwtcYlV753tnPOFB+95frymL5HOFZt2uhIbRXwbdkHZORmxS44GiTP93mDfdhI115VJQ23A0vxPT+r7b4CZEjKbxEc6yO0maKKbRwVYwADzud7U4Sg9mSDvf80qaXHPUxQTt1byucjFcDqKRYXet5Q=="
}

url_base = "https://bj-share.info/"
soup = BeautifulSoup(data, "html.parser")

links = soup.find_all("a", title="Baixar")

# Pasta para salvar torrents
os.makedirs("torrents", exist_ok=True)

with httpx.Client(headers=headers, cookies=cookies, follow_redirects=True) as client:
    for a in links:
        url = f"{url_base}{a['href']}"
        print("Baixando:", url)

        response = client.get(url)

        if response.status_code != 200:
            print("Erro:", response.status_code)
            continue

        # ----- PEGAR NOME DO ARQUIVO -----
        cd = response.headers.get("Content-Disposition", "")

        match = re.search(r'filename="(.+)"', cd)
        if match:
            filename = match.group(1)
        else:
            # fallback se não vier header
            torrent_id = a['href'].split("id=")[-1]
            filename = f"{torrent_id}.torrent"

        filepath = f"torrents/{filename}"

        # ----- SALVAR O ARQUIVO -----
        with open(filepath, "wb") as f:
            f.write(response.content)

        print("Salvo:", filepath)
        time.sleep(20)
