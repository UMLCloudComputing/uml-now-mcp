# server.py

import os
import time
from typing import Optional, Annotated
from pydantic import Field

import functools
import inspect

from fastmcp import FastMCP
from fastmcp.server.lifespan import lifespan
from fastmcp.dependencies import CurrentContext
from fastmcp.server.context import Context

from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, Counter, Histogram

from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from umlnow import (
    Course,
    API,
    parse_catalog_courses_response,
    get_subject_prefix_mapping,
)

# Configuration
BROADCAST_ADDRESS = os.getenv("BROADCAST_ADDRESS", "127.0.0.1")


# Prometheus metrics
TOOL_CALLS_TOTAL = Counter(
    "uml_now_mcp_tool_calls_total",
    "Total number of MCP tool calls for uml-now-mcp",
    labelnames=["tool_name", "status"],
)
TOOL_EXECUTION_TIME = Histogram(
    "uml_now_mcp_tool_execution_seconds",
    "Time spent executing an MCP tool in seconds for uml-now-mcp",
    labelnames=["tool_name", "status"],
    buckets=(0.01, 0.05, 0.1, 0.5, 1.0, 2.5, 5.0, 10.0, float("inf")),
)


# Custom decorator for Prometheus
def monitor_tool(func):
    """
    A decorator to measure tool execution times and log metrics to Proemtheus.
    Supports both standard sync and async functions automatically.
    """
    tool_name = func.__name__

    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        status = "success"
        try:
            return await func(*args, **kwargs)
        except Exception:
            status = "failure"
            raise
        finally:
            duration = time.perf_counter() - start_time
            TOOL_EXECUTION_TIME.labels(tool_name=tool_name, status=status).observe(
                duration
            )
            TOOL_CALLS_TOTAL.labels(tool_name=tool_name, status=status).inc()

    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        status = "success"
        try:
            return func(*args, **kwargs)
        except Exception:
            status = "failure"
            raise
        finally:
            duration = time.perf_counter() - start_time
            TOOL_EXECUTION_TIME.labels(tool_name=tool_name, status=status).observe(
                duration
            )
            TOOL_CALLS_TOTAL.labels(tool_name=tool_name, status=status).inc()

    return async_wrapper if inspect.iscoroutinefunction(func) else sync_wrapper


@lifespan
async def app_lifespan(server):
    """Initialization and destruction steps for server"""
    print("Starting server...")
    try:
        # Configure server persistent
        yield
    finally:
        print("Shutting down server...")


mcp_server = FastMCP("UML-NOW-MCP-Server", lifespan=app_lifespan)


@mcp_server.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> JSONResponse:
    # Add pre-flight checks here, none at the moment
    return JSONResponse({"status": "ok", "service": "uml-now-mcp"}, status_code=200)


@mcp_server.custom_route("/metrics", methods=["GET"])
async def metrics(request: Request) -> Response:
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


# DONE
@mcp_server.tool
@monitor_tool
async def get_course_info_from_course_id(
    course_id: Annotated[str, "Required Course ID"],
    ctx: Context = CurrentContext(),
    course_name: Annotated[
        bool, "Optional boolean. Set to True to get the course name in the response"
    ] = False,
    course_description: Annotated[
        bool,
        "Optional boolean. Set to True to get the course description in the response",
    ] = False,
    course_url: Annotated[
        bool,
        "Optional boolean. Set to True to get the course reference url in the response.",
    ] = False,
    course_credits: Annotated[
        bool,
        "Optional boolean. Set to True to get the course credits information in the response",
    ] = False,
    course_requirements: Annotated[
        bool,
        "Optional boolean. Set to True to get the course requirements in the response",
    ] = False,
) -> dict:
    """
    Get course information from a provided course ID. Leave all boolean arguments to False to obtain all information about the course in the response.
    """
    await ctx.info("Called `get_course_info_from_course_id`")
    return Course(
        course_id.strip("\n"),
        name=course_name,
        url=course_url,
        description=course_description,
        credits=course_credits,
        requirements_text=course_requirements,
    )


# DONE
@mcp_server.tool
@monitor_tool
async def get_all_courses_by_subject_prefix(
    subject_prefix: Annotated[
        str,
        "The subject prefix. IE COMP for Computer Science. Use `get_all_subject_prefixes` for an exhaustive mapping of subject names to their prefixes.",
    ],
    ctx: Context = CurrentContext(),
) -> dict:
    """
    Obtain a total list of classes from a subject. Use `get_all_subject_prefixes` for an exhaustive mapping of subject names to their names.
    """
    await ctx.info("Called `get_courses_by_subject_prefix`")
    url = f"https://www.uml.edu/Catalog/Advanced-Search.aspx?prefix={subject_prefix}&type=prefix"
    result = await parse_catalog_courses_response(url=url, structured=True)
    return result


# DONE
@mcp_server.tool
@monitor_tool
async def search_by_course_title(
    course_title: Annotated[str, "The course title to search. IE 'Computing I'"],
    ctx: Context = CurrentContext(),
    top_k: Annotated[
        int,
        Field(
            description="The number of top relavent courses to receive in the response. Set to -1 to get all courses. The maximum allowed value is 10.",
            ge=-1,
            le=10,
        ),
    ] = 3,
) -> dict:
    """
    Search for course ID, name, url, description, credits, and requirements by the course title
    """
    await ctx.info("Called `search_by_course_title`")
    url = f"https://www.uml.edu/Catalog/Advanced-Search.aspx?title={course_title}&type=title"
    result = await parse_catalog_courses_response(url=url, structured=True, top_k=top_k)
    return result


@mcp_server.tool
@monitor_tool
async def get_all_subject_prefixes(ctx: Context = CurrentContext()) -> dict:
    """
    Obtain the exhaustive mapping of subject names to their prefixes
    """
    await ctx.info("Called `get_all_subject_prefixes`")
    return get_subject_prefix_mapping()


if __name__ == "__main__":
    PORT = 8000
    mcp_server.run(transport="streamable-http", host=BROADCAST_ADDRESS, port=PORT)
