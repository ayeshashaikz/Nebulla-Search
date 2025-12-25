from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from engine import search_query
import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")


class SearchHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        parsed_path = urlparse(self.path)

        # ================= HOME PAGE =================
        if parsed_path.path == "/" or parsed_path.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            with open("index.html", "rb") as f:
                self.wfile.write(f.read())

        # ================= SEARCH PAGE =================
        elif parsed_path.path == "/search":
            params = parse_qs(parsed_path.query)
            query = params.get("q", [""])[0]
            results = search_query(query)

            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()

            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>NebulaSearch • Results</title>
                <style>
                    body {{
                        font-family: "Segoe UI", Arial, sans-serif;
                        background: linear-gradient(135deg, #e8f0ff, #f7fbff);
                        margin: 0;
                        padding: 0;
                        color: #1f2937;
                    }}

                    header {{
                        background: rgba(255,255,255,0.85);
                        backdrop-filter: blur(10px);
                        padding: 24px 40px;
                        box-shadow: 0 10px 25px rgba(0,0,0,0.08);
                    }}

                    header h2 {{
                        margin: 0;
                        font-size: 32px;
                    }}

                    header a {{
                        display: inline-block;
                        margin-top: 8px;
                        text-decoration: none;
                        color: #2563eb;
                        font-weight: 600;
                    }}

                    .container {{
                        max-width: 960px;
                        margin: 50px auto;
                        padding: 0 20px;
                    }}

                    .card {{
                        background: rgba(255,255,255,0.9);
                        backdrop-filter: blur(10px);
                        border-radius: 16px;
                        padding: 26px;
                        margin-bottom: 22px;
                        cursor: pointer;
                        transition: transform 0.25s ease, box-shadow 0.25s ease;
                        box-shadow: 0 8px 20px rgba(0,0,0,0.08);
                    }}

                    .card:hover {{
                        transform: translateY(-6px);
                        box-shadow: 0 18px 40px rgba(0,0,0,0.15);
                    }}

                    .filename {{
                        font-size: 26px;
                        font-weight: 700;
                        margin-bottom: 8px;
                    }}

                    .score {{
                        color: #6b7280;
                        font-size: 15px;
                    }}
                </style>
            </head>

            <body>
                <header>
                    <h2>Results for “{query}”</h2>
                    <a href="/">← Back to Search</a>
                </header>

                <div class="container">
            """

            if not results:
                html += "<p>No results found.</p>"
            else:
                for fname, score in results:
                    html += f"""
                    <div class="card" onclick="location.href='/view/{fname}'">
                        <div class="filename">{fname}</div>
                        <div class="score">Relevance score: {score}</div>
                    </div>
                    """

            html += """
                </div>
            </body>
            </html>
            """

            self.wfile.write(html.encode("utf-8"))

        # ================= FILE VIEW PAGE =================
        elif parsed_path.path.startswith("/view/"):
            filename = parsed_path.path.replace("/view/", "")
            filepath = os.path.join(DATA_DIR, filename)

            if not os.path.exists(filepath):
                self.send_error(404, "File not found")
                return

            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()

            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>{filename} • NebulaSearch</title>
                <style>
                    body {{
                        font-family: "Segoe UI", Arial, sans-serif;
                        background: linear-gradient(135deg, #c7ddff, #eef6ff);
                        margin: 0;
                        padding: 0;
                        color: #1f2937;
                    }}

                    .container {{
                        max-width: 900px;
                        margin: 70px auto;
                        background: rgba(255,255,255,0.9);
                        backdrop-filter: blur(10px);
                        padding: 50px;
                        border-radius: 20px;
                        box-shadow: 0 20px 50px rgba(0,0,0,0.15);
                    }}

                    h2 {{
                        font-size: 36px;
                        margin-bottom: 25px;
                    }}

                    pre {{
                        font-size: 20px;
                        line-height: 1.8;
                        white-space: pre-wrap;
                        color: #1e293b;
                    }}

                    a {{
                        text-decoration: none;
                        color: #2563eb;
                        font-weight: 600;
                    }}

                    /* AI STYLES */
                    #ai-btn {{
                        position: fixed;
                        right: 26px;
                        bottom: 26px;
                        background: linear-gradient(135deg, #4f8cff, #2563eb);
                        color: white;
                        padding: 16px;
                        border-radius: 50%;
                        font-size: 24px;
                        cursor: pointer;
                        box-shadow: 0 12px 30px rgba(79,140,255,0.5);
                    }}

                    #ai-box {{
                        position: fixed;
                        right: 26px;
                        bottom: 96px;
                        width: 340px;
                        height: 460px;
                        background: rgba(255,255,255,0.95);
                        backdrop-filter: blur(12px);
                        display: none;
                        flex-direction: column;
                        border-radius: 18px;
                        box-shadow: 0 20px 50px rgba(0,0,0,.25);
                    }}

                    .ai-header {{
                        background: linear-gradient(135deg, #4f8cff, #2563eb);
                        color: white;
                        padding: 14px;
                        font-weight: 700;
                        display: flex;
                        justify-content: space-between;
                        border-radius: 18px 18px 0 0;
                    }}

                    #ai-messages {{
                        flex: 1;
                        padding: 14px;
                        overflow-y: auto;
                        font-size: 14px;
                    }}

                    .ai-input {{
                        display: flex;
                        gap: 8px;
                        padding: 14px;
                    }}

                    .ai-input input {{
                        flex: 1;
                        padding: 10px;
                        border-radius: 8px;
                        border: 1px solid #c7d2fe;
                    }}

                    .ai-input button {{
                        background: linear-gradient(135deg, #4f8cff, #2563eb);
                        color: white;
                        border: none;
                        padding: 10px 14px;
                        border-radius: 8px;
                        cursor: pointer;
                    }}
                </style>
            </head>

            <body>
                <div class="container">
                    <a href="javascript:history.back()">← Back to Results</a>
                    <h2>{filename}</h2>
                    <pre>{content}</pre>
                </div>

                <!-- AI ASSISTANT -->
                <div id="ai-btn" onclick="toggleAI()">🤖</div>

                <div id="ai-box">
                    <div class="ai-header">
                        Ask this document
                        <span onclick="toggleAI()">✖</span>
                    </div>

                    <div id="ai-messages">
                        <p>Ask questions about <b>{filename}</b></p>
                    </div>

                    <div class="ai-input">
                        <input id="ai-question" placeholder="Ask a question..." />
                        <button onclick="askAI()">Send</button>
                    </div>
                </div>

               <script>
function toggleAI() {{
    const box = document.getElementById("ai-box");
    box.style.display = box.style.display === "flex" ? "none" : "flex";
}}

async function askAI() {{
    const input = document.getElementById("ai-question");
    const q = input.value.trim();
    if (!q) return;

    const messages = document.getElementById("ai-messages");

    messages.innerHTML +=
        `<p><b>You:</b> ${{q}}</p>`;

    input.value = "";   // ✅ clears the input box after sending
    messages.innerHTML += `<p><i>AI is thinking...</i></p>`;
    messages.scrollTop = messages.scrollHeight; // ✅ auto scroll
    const res = await fetch(`/ask?q=${{encodeURIComponent(q)}}`);
    const data = await res.json();

    messages.innerHTML +=
        `<p><b>AI:</b> ${{data.answer}}</p>`;

    messages.scrollTop = messages.scrollHeight; // ✅ auto scroll
}}
</script>


            </body>
            </html>
            """

            self.wfile.write(html.encode("utf-8"))

        # ================= AI API =================
        elif parsed_path.path == "/ask":
            params = parse_qs(parsed_path.query)
            question = params.get("q", [""])[0]

            answer = search_query(question, mode="ai")

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"answer": answer}).encode())

        else:
            self.send_error(404)


if __name__ == "__main__":
    server = HTTPServer(("localhost", 8000), SearchHandler)
    print("Server running at http://localhost:8000")
    server.serve_forever()
