"""
Search CLI

This module contains the CLI for the search command. This command is used to create a user friendly
abstraction for the both the UML Now API and the UML Catalog API.
"""

from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import requests 
import time
import asyncio

from .data import DEPARTMENT_PREFIXES
from .course import Course


# Return html from a rendered webpage
async def get_html(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(url, wait_until="networkidle")
        html = await page.content()
        await browser.close()
    return html

# Magic is in the URL
async def parse_catalog_courses_response(url: str, structured: bool, 
                                          debug: bool = False, top_k: int = -1):
    """ Parse catalog query response from a provided url """
    # Output
    OUTPUT = {
        'total': 0,
        'time': time.time(),
    }
   
    # Get the html response
    html = await get_html(url)
    soup = BeautifulSoup(html, "lxml")

    # Extract course elements from the rendered html page
    if top_k > 0:
      elements = soup.select(".cxpccT", limit=top_k)
    else:
      elements = soup.select(".cxpccT")
      
    print(f"- Found {len(elements)} course elements") if debug else None

    # For each element, extract the course number, name, and description
    for element in elements:
        
        # Get the span elements. Helps identify the position of the data
        spans = element.find_all('span')
        course_prefix = spans[1].text
        
        # If the debug flag is set, print the course prefix
        print(f'    - Starting: {course_prefix}') if debug else None
        
        # Increment the total number of results
        OUTPUT["total"] += 1
                
        # If the parsed flag is set, return a parsed course object
        if structured:
            OUTPUT[course_prefix] = Course(course_prefix)
            
        # Otherwise, return avalible data without parsing
        else:
            OUTPUT[course_prefix] = {
                "number": spans[1].text,
                "name": spans[2].text,
                "id": spans[5].text,
            }
            if spans[7].text == "Credits Min:":
              OUTPUT[course_prefix]["credits_min"] = spans[8].text
              OUTPUT[course_prefix]["credits_max"] = spans[11].text
            elif spans[7].text == "Credits:":
              OUTPUT[course_prefix]["credits"] = spans[8].text
            
    # Return the output
    OUTPUT['time'] = time.time() - OUTPUT['time']
    return OUTPUT
