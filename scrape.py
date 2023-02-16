import re
from googletrans import Translator
import requests
from bs4 import BeautifulSoup
import os


def create_new_file(directory_path, soup):

    # Create a directory in the current project directory
    path = os.path.join(os.getcwd(), directory_path)
    path = path[:-1] if path[-1] == " " else path

    try:
        os.makedirs(path)
        print(f"Directory '{directory_path}' created.")
    except FileExistsError:
        print(f"Directory '{directory_path}' already exists.")
    except FileNotFoundError:
        print(f"Directory '{directory_path}' does not exists.")

    # Create an index.html file in the new directory
    index_file = os.path.join(path, "index.html")

    with open(index_file, "w", encoding="utf-8") as file:
        file.writelines(soup.prettify())


def translate_page(soup):

    # Initialize the translator
    translator = Translator()

    # Loop through each element on the page and translate its text content to Hindi
    for element in soup.find_all():
        if element.name == "script" or element.name == "style":
            continue
        if element.string:
            try:
                # Translate the text using Googletrans
                translation = translator.translate(element.string, dest='hi')
                # Replace the original text with the translated text
                element.string.replace_with(translation.text)
            except:
                print(element.string)


def scrape_page(url):

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0",
        "Cookie": "PHPSESSID=6vgoa12gmquf7ve6ipojkglme5; signup_prompt=1; news_banner=1; sessionId=63145f1de08768c7afd2d8190b"}

    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')

    scripts = soup.find_all('script')  # find all <script> elements
    for script in scripts:
        if 'r.p="/webpack/"' in script.text:
            pattern = re.compile(re.escape('r.p="/webpack/"'))
            script.string = pattern.sub(
                'r.p="https://www.classcentral.com/webpack/"', script.string)

    return soup


def web_scraping(base_url):

    soup = scrape_page(url=base_url)

    # Follow links to other pages
    links = soup.find_all('a', href=True)

    # new_links = [link.get('href') for link in links]

    # new_links = [link[1:] if link.startswith(
    #     "/") else link for link in new_links]
    # new_links = list(set(new_links))

    prefix_1 = "https://www.classcentral.com/"
    prefix_2 = "https://"
    prefix_3 = "http://"

    # # Find the reference of each page and scrape that page
    # # After scraping page, store in the specified directory.
    # for link in new_links:
    #     if link.startswith(prefix_1):
    #         link = os.path.relpath(link, prefix_1)
    #         link = link.replace("\\", "/")

    #     if link.startswith(prefix_2) or link.startswith(prefix_3):
    #         continue

    #     link_url = BASE_URL + link
    #     # print(f"Link: {link_url}, Page: {link}\n\n")
    #     inner_soup = scrape_page(url=link_url)
    #     create_new_file(directory_path=link, soup=inner_soup)

    # Change the href of each link in our home page (index.html)
    for link in links:
        if link.get('href').startswith(prefix_1):
            temp = os.path.relpath(link.get('href'), prefix_1)
            temp = temp.replace("\\", "/")
            link['href'] = "/" + temp

        if link['href'][-1] == " ":
            link['href'] = link['href'][:-1]

        if not link.get('href').startswith(prefix_2):
            link['href'] = '.' + link.get('href') + "/index.html"

    # Translate the text of index page
    translate_page(soup=soup)

    with open("index.html", "w", encoding="utf-8") as file:
        file.writelines(soup.prettify())


BASE_URL = 'https://www.classcentral.com/'

# Start scraping from the first page
web_scraping(base_url=BASE_URL)
