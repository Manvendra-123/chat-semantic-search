from sentence_transformers import SentenceTransformer
m = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
q = "When did we lock the hill station?"
cands = [
  "chalo manali fix h 14 ko nikalte h",
  "aaj parking me garmi bahot h",
  "CR cancel kar diya parking next week",
  "khana kha liya kya",
  "exam form bhar diya",
]
qv = m.encode([q], normalize_embeddings=True)
cv = m.encode(cands, normalize_embeddings=True)
print((cv @ qv.T).ravel())
