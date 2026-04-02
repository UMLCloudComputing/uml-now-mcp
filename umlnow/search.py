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

# Return a total list of classes from a subject
async def get_courses_by_subject_prefix(subject: str, parse=False, debug=False):
    """Return a total list of classes from a subject."""

    # Output
    OUTPUT = {
        'total': 0,
        'time': time.time(),
    }
    
    # Create the url
    url = f"https://www.uml.edu/Catalog/Advanced-Search.aspx?prefix={subject}&type=prefix"
   
    # Get the html response
    html = await get_html(url)
    soup = BeautifulSoup(html, "lxml")

    # Extract course elements from the rendered html page
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
        if parse:
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


# class Search(object):
#     """Search API. 
#     This object provides the CLI for the search command. This command is used to create a user friendly
#     abstraction for the both the UML Now API and the UML Catalog API."""
    
#     def __init__(self, **params):
#         self.params = params
#         self.debug = True if 'debug' in self.params else False
        
#     def courses(self):
#         """Return a list of classes that match the search criteria."""    
        
#         # Output
#         OUTPUT = {
#             'total': 0,
#             'time': time.time(),
#         }
        
#         # If the departments parameter is set, use it
#         if 'departments' in self.params:
            
#             # Is it a string or a tuple?
#             if isinstance(self.params['departments'], str):
#                 departments = [self.params['departments']]
#             else:
#                 departments = list(self.params['departments'])
            
#         # Otherwise, use the entire list of departments
#         else:
#             departments = DEPARTMENT_PREFIXES
                        
#         # For department in departments, get the courses
#         for department in departments:
#             if self.debug:
#                 print("- Starting search for department: " + department)
#             OUTPUT[department] = get_courses_by_department_prefix(department, parse=('parse' in self.params and self.params['parse']), debug=self.debug)
#             OUTPUT['total'] += OUTPUT[department]['total']
            
#         # Return the output
#         OUTPUT['time'] = time.time() - OUTPUT['time']
#         return OUTPUT
    
#     def professors(self):
#         """Search professors."""
#         return "Sorry, not implemented yet."
    
#     def majors(self):
#         """Search majors."""
#         return "Sorry, not implemented yet."
    
#     def minors(self):
#         """Search minors."""
#         return "Sorry, not implemented yet."
    
#     def degree_pathways(self):
#         """Search degree pathways."""
#         return "Sorry, not implemented yet."
