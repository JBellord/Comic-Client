#!/usr/bin/env python3

from bs4 import BeautifulSoup as bs
from PIL import Image
from dotenv import load_dotenv
from io import BytesIO
import requests as rq
import dropbox
import os, sys
import mimetypes

search_url = "https://azcomix.me/ajax/search?q="
url = "https://azcomix.net/comic/"


def search(query: str):
    search_query = search_url + query
    response = rq.get(search_query)
    if response.status_code == 200:
        uuid = 1
        results = response.json()["data"]
        if len(results) > 0:
            print(f"\n{len(results)} Available Titles:")
            for i in results:
                print(f"({uuid}) Title: {i['title']}")
                uuid += 1
            return results
        else:
            print(f"Couldn't find '{query}'")
            sys.exit()
    else:
        return response.status_code


def get_comic_info(slug: str):
    response = rq.get(url + slug)
    if response.status_code == 200:
        soup = bs(response.content, "html.parser")
        name = soup.find("h2").text
        chapters = soup.find("ul", class_="chapter-list")
        srcs = chapters.find_all("a")
        for src in srcs:
            yield {src.text: src["href"]}
    else:
        return response.status_code


def get_comic_issue(url: str):
    slug_url = url + "/all"
    response = rq.get(slug_url)
    if response.status_code == 200:
        soup = bs(response.content, "html.parser")
        chapter = soup.find("div", class_="page-chapter")
        images = chapter.find_all("img")
        for i in images:
            yield i["src"]
    else:
        return response.status_code


def images_to_pdf(src_list, name):
    image_list = []
    i = 0
    for src in src_list:
        img_res = rq.get(src, stream=True)
        img_res.raise_for_status()
        img = Image.open(BytesIO(img_res.content)).convert("RGB")
        image_list.append(img)

    image_list[0].save(
        f"./{name}.pdf",
        "PDF",
        resolution=100.0,
        save_all=True,
        append_images=image_list[1:],
    )


def upload_comics(filename: str):
    load_dotenv()
    dbx = dropbox.Dropbox(
        app_key=os.environ.get("DROPBOX_KEY"),
        app_secret=os.environ.get("DROPBOX_SECRET"),
        oauth2_refresh_token=os.environ.get("DROPBOX_REFRESH_TOKEN"),
        timeout=None,
    )
    with open(f"./{filename}.pdf", "rb") as f:
        dbx.files_upload(
            f.read(),
            f"/comics/{filename}.pdf",
            mode=dropbox.files.WriteMode("overwrite"),
        )


def delete_comic(location: str):
    try:
        if os.path.exists(f"./{location}.pdf"):
            os.remove(f"./{location}.pdf")
        else:
            print("No such file")
    except:
        sys.exit()


if __name__ == "__main__":
    search("sandman overture")
