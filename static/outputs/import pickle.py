import pickle

meta_path = "static/outputs/faiss_meta.pkl"

with open(meta_path, "rb") as f:
    meta = pickle.load(f)

print("Embedded files and topics:")
for entry in meta:
    print(f"File: {entry['file']} | Topic: {entry['topic']}")