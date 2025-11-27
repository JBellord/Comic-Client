#!/usr/bin/python3

from azcomix import (
    search,
    images_to_pdf,
    get_comic_info,
    get_comic_issue,
    upload_comics,
)
from raco import *
import sys
from rich.console import Console

console = Console()


def joint(input_1, input_2):
    images_to_pdf(input_1, input_2)
    upload_comics(input_2)


def main():
    name = input("Enter comic name:  ")
    results = search(name)
    print("\n")
    selected = input("Enter Comic ID:  ")
    selected_comic = results[int(selected) - 1]
    print("These are the Issues:\n")
    start = int(input("Start Issue:    "))
    end = int(input("End Issue:    "))
    issue_info = [x for x in get_comic_info(selected_comic["slug"])][::-1]
    x = 1
    for i in issue_info:
        print(f"({x}) {list(i.keys())[0]}")
        x += 1
    issue_no = int(input("\nEnter Issue ID:  "))
    selected_issue = issue_info[issue_no - 1]
    selected_issue_src = list(selected_issue.values())[0]
    filename = (
        str(selected_comic["slug"])
        + "-"
        + str(list(selected_issue.keys())[0]).lower().replace(" ", "-")
    )
    print("-----------------------------------------")
    print("|    Downloading, please wait")
    print("-----------------------------------------")
    images_to_pdf(get_comic_issue(selected_issue_src), filename)
    print("-----------------------------------------")
    print("|    Uploading, please wait")
    print("-----------------------------------------")
    upload_comics(filename=filename)
    print("|    Done!\n")


def get_issues():
    name = input("Enter comic name:  ")
    results = search_comics(name)
    x = 0
    for i in results:
        print(f"{x}", "--->", i.get("title"))
        x += 1
    print("\n")
    selected = input("Enter Comic ID:  ")
    selected_comic = results[int(selected)]
    issue_info = scrape_comic_page(selected_comic["link"])
    print(f"There are {len(issue_info)} issues for ", selected_comic.get("title"))
    start = int(input("\nStart Issue:    "))
    end = int(input("End Issue:     "))
    print("\n")

    selected_issues = issue_info[(start - 1) : (end)]
    with console.status("[bold green]Fetching Comic Book Issues...") as status:
        for selected_issue in selected_issues:
            selected_issue_src = selected_issue["link"]
            filename = (
                str(selected_issue["title"])
                .lower()
                .replace(" ", "-")
                .replace("(", "")
                .replace(")", "")
            )
            image_list = scrape_issue_page(selected_issue_src)
            joint(image_list, filename)
            console.log(f"[cyan]Uploaded: {filename}")
        console.log(f"[red]Done.")


if __name__ == "__main__":
    get_issues()
