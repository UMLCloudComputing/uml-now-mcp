# server.py

import os
from typing import Optional, Annotated
from pydantic import Field
from fastmcp import FastMCP
from fastmcp.server.lifespan import lifespan
from fastmcp.dependencies import CurrentContext
from fastmcp.server.context import Context
from umlnow import Course, API, parse_catalog_courses_response, get_subject_prefix_mapping

# Configuration
BROADCAST_ADDRESS = os.getenv("BROADCAST_ADDRESS", "127.0.0.1")

@lifespan
async def app_lifespan(server):
  """ Initialization and destruction steps for server """
  print("Starting server...") 
  try:
    # Configure server persistent 
    yield 
  finally:
    print("Shutting down server...")
    

mcp_server = FastMCP("UML-NOW-MCP-Server", lifespan=app_lifespan)

# DONE
@mcp_server.tool
async def get_course_info_from_course_id(course_id: Annotated[str, "Required Course ID"], 
    ctx: Context = CurrentContext(),
    course_name: Annotated[bool, "Optional boolean. Set to True to get the course name in the response"] = False, 
    course_description: Annotated[bool, "Optional boolean. Set to True to get the course description in the response"] = False, 
    course_url: Annotated[bool, "Optional boolean. Set to True to get the course reference url in the response."]= False, 
    course_credits: Annotated[bool, "Optional boolean. Set to True to get the course credits information in the response"] = False, 
    course_requirements: Annotated[bool, "Optional boolean. Set to True to get the course requirements in the response"] = False) -> dict:
  """ 
  Get course information from a provided course ID. Leave all boolean arguments to False to obtain all information about the course in the response.
  """
  await ctx.info("Called `get_course_info_from_course_id`")
  return Course(course_id.strip('\n'), name=course_name, url=course_url, description=course_description, credits=course_credits, requirements_text=course_requirements)

# DONE
@mcp_server.tool
async def get_all_courses_by_subject_prefix(subject_prefix: Annotated[str, "The subject prefix. IE COMP for Computer Science. Use `get_all_subject_prefixes` for an exhaustive mapping of subject names to their prefixes."], 
  ctx: Context = CurrentContext()) -> dict:
  """
  Obtain a total list of classes from a subject. Use `get_all_subject_prefixes` for an exhaustive mapping of subject names to their names.
  """
  await ctx.info("Called `get_courses_by_subject_prefix`")
  url = f"https://www.uml.edu/Catalog/Advanced-Search.aspx?prefix={subject_prefix}&type=prefix" 
  result = await parse_catalog_courses_response(url=url, structured=True)
  return result

# DONE 
@mcp_server.tool
async def search_by_course_title(course_title: Annotated[str, "The course title to search. IE 'Computing I'"],
                                  ctx: Context = CurrentContext(),
                                  top_k: Annotated[int, 
                                          Field(
                                            description="The number of top relavent courses to receive in the response. Set to -1 to get all courses.", 
                                            ge=1, le=10)] 
                                         = 3) -> dict:
  """
  Search for course ID, name, url, description, credits, and requirements by the course title
  """
  await ctx.info("Called `search_by_course_title`")
  url = f"https://www.uml.edu/Catalog/Advanced-Search.aspx?title={course_title}&type=title" 
  result = await parse_catalog_courses_response(url=url, structured=True, top_k=top_k)
  return result

@mcp_server.tool
async def get_all_subject_prefixes(ctx: Context = CurrentContext()) -> dict:
  """ 
  Obtain the exhaustive mapping of subject names to their prefixes 
  """
  await ctx.info("Called `get_all_subject_prefixes`")
  return get_subject_prefix_mapping() 

if __name__ == "__main__":
  mcp_server.run(transport="streamable-http", host=BROADCAST_ADDRESS, port=8000)


