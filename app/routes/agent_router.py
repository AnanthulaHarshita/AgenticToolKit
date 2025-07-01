# === File: app/routes/agent_router.py ===
# API endpoint to handle agent task requests

from flask import Blueprint, request, jsonify, send_file, Flask, render_template
import os
from app.services.seo_generator import run_seo_agent
import logging
from app.services.embedding_store import store_embedding, search_embeddings
import openai
from app.services.agentic_rag import agentic_rag

app = Flask(__name__, static_folder="static")

# Create a Blueprint for agent-related routes
agent_bp = Blueprint("agent", __name__)

@agent_bp.route("/run-agent", methods=["GET", "POST"])
def run_agent():
    """
    Endpoint to run the SEO agent.
    - GET: Returns a readiness message.
    - POST: Expects a JSON payload and runs the SEO agent.
    """
    try:
        if request.method == "POST":
            # Try to parse JSON payload from the request
            payload = request.get_json()
            if payload is None:
                # If no JSON payload, return an error
                return jsonify({"error": "Missing or invalid JSON payload"}), 400
            # Run the SEO agent with the provided payload
            result = run_seo_agent(payload)
            # Initialize file_content as empty string
            file_content = ""
            # If the result contains a filename, try to read the file content
            if "filename" in result:
                try:
                    # Open the generated file and read its content
                    with open(result["filename"], "r", encoding="utf-8") as f:
                        file_content = f.read()
                except Exception as file_err:
                    # If there's an error reading the file, store the error message
                    file_content = f"Could not read file: {file_err}"
            # Return the result along with the file content in the response
            return jsonify({
                **result,
                "file_content": file_content  # Add the file content to the response
            }), 200
        else:  # GET request
            # For GET requests, return a simple readiness message
            return jsonify({"message": "Agent is ready. Send a POST request with JSON payload to run."}), 200
    except Exception as e:
        # Catch any exceptions and return as a 500 error
        return jsonify({"error": str(e)}), 500

@agent_bp.route("/download/<filename>", methods=["GET"])
def download_file(filename):
    """
    Endpoint to download the generated .txt file.
    """
    logging.warning(f"Download requested for filename: {filename}")

    # Build the file path dynamically based on the filename argument
    file_path = os.path.join("static", "outputs", filename)
    logging.warning(f"Resolved file path (download): {file_path}")
    logging.warning(f"Absolute file path (download): {os.path.abspath(file_path)}")  # <-- Add this

    # Check if file exists
    if os.path.exists(file_path):
        logging.warning(f"File exists: {file_path}")
        # If the file exists, send it as an attachment for download
        return send_file(file_path, as_attachment=True)
    else:
        logging.error(f"File NOT found: {file_path}")
        # If the file does not exist, return a 404 error as JSON
        return jsonify({"error": f"File not found: {file_path}"}), 404
    
@agent_bp.route("/store-embedding", methods=["POST"])
def store_embedding_endpoint():
    """
    Endpoint to store content as vector embeddings for RAG.
    Expects JSON: { "topic": "topic to fetch latest file for" }
    """
    data = request.get_json()
    if not data or "topic" not in data:
        return jsonify({"error": "Missing 'topic' in request"}), 400

    topic = data["topic"]
    try:
        result = store_embedding(topic)
        return jsonify({"message": "Embedding stored successfully", "result": result}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@agent_bp.route("/rag", methods=["POST"])
def rag_endpoint():
    """
    RAG endpoint: Given a query, retrieve relevant docs and generate an answer.
    Expects JSON: { "query": "your question" }
    """
    data = request.get_json(silent=True)
    query = (data or {}).get("query") if data else request.form.get("rag_query")
    if not query:
        return jsonify({"error": "Missing query"}), 400

    answer = agentic_rag(query)
    return jsonify({
        "answer": answer
    })

@app.route("/rag", methods=["POST"])
def rag_form():
    query = request.form.get("rag_query")
    results = search_embeddings(query, top_k=3)
    if "error" in results:
        rag_answer = results["error"]
        retrieved_files = []
    else:
        # ...build context and call LLM as in your agent_router.py...
        # (copy the context and prompt logic from your blueprint)
        context = ""
        for res in results:
            with open(res["file"], "r", encoding="utf-8") as f:
                context += f"\n---\n" + f.read()
        prompt = f"""Use the following context to answer the user's question.

Context:
{context}

Question: {query}
Answer:"""
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        rag_answer = response.choices[0].message.content
        retrieved_files = [r["file"] for r in results]
    return render_template(
        "index.html",
        rag_answer=rag_answer,
        retrieved_files=retrieved_files
        # ...plus any other variables your template needs...
    )
