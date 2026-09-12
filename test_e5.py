from sentence_transformers import SentenceTransformer
import sys

def test():
    try:
        m = SentenceTransformer('intfloat/multilingual-e5-base')
    except Exception as e:
        print(f"Failed to load model: {e}")
        return

    q = "query: When did we lock the hill station?"
    cands = [
        "passage: chalo manali fix h 14 ko nikalte h",
        "passage: aaj parking me garmi bahot h",
        "passage: CR cancel kar diya parking next week",
        "passage: khana kha liya kya",
        "passage: exam form bhar diya",
    ]

    qv = m.encode([q], normalize_embeddings=True)
    cv = m.encode(cands, normalize_embeddings=True)
    scores = (cv @ qv.T).ravel()

    for i, c in enumerate(cands):
        print(f"[{i}] {c:50} -> {scores[i]:.4f}")

if __name__ == '__main__':
    test()
