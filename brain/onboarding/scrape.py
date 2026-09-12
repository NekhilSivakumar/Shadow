import os

import requests
from bs4 import BeautifulSoup
from tavily import TavilyClient

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


def research_person(name_or_email: str):
    return tavily.search(query=name_or_email, max_results=5)


def scrape_page(url: str) -> str:
    html = requests.get(url, timeout=10).text
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text(separator=" ", strip=True)[:5000]
