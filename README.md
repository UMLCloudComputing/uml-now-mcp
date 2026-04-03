# UML Now MCP Server

An MCP Server for interacting with the UML Now API

**By using this, you agree to the terms and conditions set forth in the [University of Massachusetts Lowell API Terms of Service](https://www.uml.edu/api/Static/tos.html).**

# Usage
The MCP server can be used locally by either
- Run as a host process: `uv run server.py`
  - Accessible at `localhost:8000/mcp`
- Run as a docker container: `./build_and_run.sh`
  - Accessible at `0.0.0.0:8000/mcp` or `localhost:8000/mcp` locally

> [!NOTE]
> If you're using the MCP Inspector tool for local development, uml-now-mcp uses the Streamable HTTP transport, not STDIO or server-sent events (SSE). 

For production deployments on kubernetes check the reference manifest, `k8s/kubernetes_prod.yaml`.

## Technologies
- Docker
- MCP

# 🛠️ Tool Calls (WIP)
<table>
    <tr>
        <th>Tool Name</th>
        <th>Description</th>
        <th>Function Signature</th>
        <th>Response Schema</th>
        <th>Misc.</th>
    </tr>
    <tr>
        <td><code>get_course_info_from_course_id</code></td>
        <td>Get course information from a provided course ID</td>
        <td>
            <pre><code>
                ... (course_id: str, 
                    course_name: bool = False, 
                    course_description: bool = False,
                    course_url: bool = False,
                    course_credits: bool = False,
                    course_requirements: bool = False)
            </code></pre>
        </td>
        <td>
            <pre><code>
            {
                name: str
                url: str
                id: str
                description: str
                credits: {
                    min: str
                    max: str
                }
                requirements-text: str
            }
            </code></pre>
        </td>
        <td>Identified as a Course dictionary object</td>
    </tr>
    <tr>
        <td><code>get_courses_by_subject_prefix</code></td>
        <td>Obtain a total list of classes from a subject at the University of Massachusetts Lowell</td>
        <td>
            <pre>
                <code>
                ... (subject_prefix: str)
                </code>
            </pre>
        </td>
        <td>
            <pre><code>
            {
                str: {
                    name: str 
                    url: str
                    id: str
                    description: str
                    credits: {
                        min: str
                        max: str
                    }
                    requirements-text: str
                }
                ...
            }
            </code></pre>
        </td>
        <td>Each object's key is the course ID. Each value is a Course dictionary object.</td>
    </tr>
</table>
