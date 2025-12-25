import os
import subprocess

# ---------------- TOKENIZER ----------------
def tokenize(text):
    text = text.lower()
    words = []
    current = ""

    for ch in text:
        if ch.isalnum():
            current += ch
        else:
            if current:
                words.append(current)
                current = ""

    if current:
        words.append(current)

    return words


# ---------------- BUILD INDEX ----------------
def build_index(folder):
    index = {}

    for filename in os.listdir(folder):
        if not filename.endswith(".txt"):
            continue

        filepath = os.path.join(folder, filename)

        with open(filepath, "r", encoding="utf-8") as file:
            text = file.read()

        tokens = tokenize(text)

        for word in tokens:
            if word not in index:
                index[word] = {}

            if filename not in index[word]:
                index[word][filename] = 0

            index[word][filename] += 1

    return index


# ---------------- KEYWORD SEARCH ----------------
def ranked_search(index, query):
    scores = {}
    query_words = tokenize(query)

    for word in query_words:
        if word in index:
            for filename, count in index[word].items():
                scores[filename] = scores.get(filename, 0) + count

    return sorted(scores.items(), key=lambda x: x[1], reverse=True)


# ---------------- AI ANSWER (OLLAMA) ----------------
def ai_answer(question, filename="data_science.txt"):
    """
    Uses Ollama (llama3) to answer strictly from the document.
    """

    data_file = os.path.join("data", filename)

    if not os.path.exists(data_file):
        return "Document not found."

    with open(data_file, "r", encoding="utf-8") as f:
        context = f.read()

    prompt = f"""
You are an AI assistant.

First, try to answer the question using the context below.
If the context does not contain enough information, you may use your general knowledge.

When you use information outside the context, clearly mention:
"Based on general AI knowledge:"

Context:
{context}

Question:
{question}

"""

    try:
        result = subprocess.run(
            ["ollama", "run", "llama3"],
            input=prompt,
            text=True,
            capture_output=True,
            timeout=120
        )

        if result.stderr:
            return result.stderr.strip()

        return result.stdout.strip()

    except Exception as e:
        return f"AI error: {str(e)}"


# ---------------- SERVER ENTRY POINT ----------------
def search_query(query, mode="search"):
    index = build_index("data")

    if mode == "ai":
        return ai_answer(query)

    return ranked_search(index, query)
