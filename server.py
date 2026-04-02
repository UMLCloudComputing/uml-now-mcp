# server.py

import os
from typing import Optional
from fastmcp import FastMCP, Context
from fastmcp.server.lifespan import lifespan
from umlnow import Course, API
from umlnow import get_courses_by_subject_prefix as sub_prefix

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
async def get_course_info_from_course_id(course_id: str, ctx: Context, 
    course_name: bool = False, course_description: bool = False, 
    course_url: bool = False, course_credits: bool = False, 
    course_requirements: bool = False) -> dict:
  """ 
  Get course information from a provided course ID
  - course_id: Required course ID 
  - course_name: Optional boolean. Set to True to get this info
  - course_description: Optional boolean. Set to True to get this info
  - course_url: Optional boolean. Set to True to get this info
  - course_credits: Optional boolean. Set to True to get this info
  - course_requirements: Optional boolean. Set to True to get this info
  """
  await ctx.info("Called `get_course_info_from_course_id`")
  return Course(course_id.strip('\n'), name=course_name, url=course_url, description=course_description, credits=course_credits, requirements_text=course_requirements)

# DONE
@mcp_server.tool
async def get_all_courses_by_subject_prefix(subject_prefix: str, ctx: Context):
  """
  Obtain a total list of classes from a subject
  - subject_prefix: The subject prefix for the University of Massachusetts Lowell
  """
  await ctx.info("Called `get_courses_by_subject_prefix`")
  result = await sub_prefix(subject=subject_prefix, parse=True)
  return result

@mcp_server.tool
async def search_course_title(course_title: str):
  """
  Search for ID, name, and description using a course_title
  """
  pass

if __name__ == "__main__":
  mcp_server.run(transport="streamable-http", host=BROADCAST_ADDRESS, port=8000)


