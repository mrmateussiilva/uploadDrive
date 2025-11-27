import httpx

url = "https://bj-share.info/torrents.php?page=5&searchstr=privacy&tags_type=0&order_by=time&order_way=desc&action=basic&searchsubmit=1"

headers = {
    "Accept": "*/*",
    "Accept-Language": "pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:145.0) Gecko/20100101 Firefox/145.0",
    "Referer": "https://bj-share.info/torrents.php?searchstr=livros",
    "Origin": "https://bj-share.info",
}

cookies = {
    "__cfbbid": "7786758824",
    "session": "zwtcYlV753tnPOFB+95frymL5HOFZt2uhIbRXwbdkHZORmxS44GiTP93mDfdhI115VJQ23A0vxPT+r7b4CZEjKbxEc6yO0maKKbRwVYwADzud7U4Sg9mSDvf80qaXHPUxQTt1byucjFcDqKRYXet5Q=="
}

response = httpx.get(url, headers=headers, cookies=cookies)

print(response.status_code)

if response.status_code == 200:
    with open("response.html", "w+", encoding="utf8") as fp:
        fp.write(response.text)
