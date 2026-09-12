import sys

with open("chatsearch/retrieve.py", "r") as f:
    content = f.read()

content = content.replace('def search(index: ChatIndex, query: str, k: int = 8) -> tuple[ParsedQuery, list[Hit]]:',
                          'def search(index: ChatIndex, query: str, k: int = 8, mode: str = "hybrid") -> tuple[ParsedQuery, list[Hit]]:')

content = content.replace("""    word_s = _sparse_scores(index.X_word, qv["word"])
    char_s = _sparse_scores(index.X_char, qv["char"])
    lsi_s = cosine_similarity(qv["lsi"], index.X_lsi).ravel()""",
"""    word_s = _sparse_scores(index.X_word, qv["word"])
    char_s = _sparse_scores(index.X_char, qv["char"])
    lsi_s = cosine_similarity(qv["lsi"], index.X_lsi).ravel()
    dense_s = cosine_similarity(qv["dense"], index.X_dense).ravel()""")

content = content.replace("""    fused *= person_boost * time_boost * decision_boost

    word_top = _top_ids(word_s * person_boost * time_boost * concept_boost, 80)
    lsi_top = _top_ids(lsi_s * person_boost * time_boost * concept_boost, 80)
    fused_top = _top_ids(fused, 80)
    rrf = _rrf([word_top, lsi_top, fused_top])
    ranked = _top_ids(fused, len(fused))""",
"""    fused *= person_boost * time_boost * decision_boost

    word_top = _top_ids(word_s * person_boost * time_boost * concept_boost, 80)
    lsi_top = _top_ids(lsi_s * person_boost * time_boost * concept_boost, 80)
    dense_top = _top_ids(dense_s * person_boost * time_boost * concept_boost, 80)
    fused_top = _top_ids(fused, 80)

    if mode == "keyword":
        kw_fused = 0.7 * _z(word_s) + 0.3 * _z(char_s)
        ranked = _top_ids(kw_fused, len(kw_fused))
    else:
        rrf = _rrf([word_top, lsi_top, dense_top, fused_top])
        # Ranked by RRF score!
        rrf_scores = np.zeros(len(fused))
        for pid, score in rrf.items():
            rrf_scores[pid] = score
        ranked = _top_ids(rrf_scores, len(rrf_scores))""")

with open("chatsearch/retrieve.py", "w") as f:
    f.write(content)
