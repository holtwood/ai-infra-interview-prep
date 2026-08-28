def page_aligned_decode_alloc_lens(
    reqs,
    *,
    reserve: int,
    page_size: int,
):
    """Whole-page decode alloc lens: nxt rounds committed up to page so allocated
    == recorded (unaligned tails leak at ps>1)."""
    cur_kv_lens = [0] * len(reqs)
    nxt_kv_lens = [0] * len(reqs)
    num_needed_tokens = 0
    for i, r in enumerate(reqs):
        cur = r.kv.kv_allocated_len
        nxt = max(
            cur,
            (r.kv_committed_len + reserve + page_size - 1) // page_size * page_size,
        )
        cur_kv_lens[i] = cur
        nxt_kv_lens[i] = nxt
        num_needed_tokens += nxt - cur
    return cur_kv_lens, nxt_kv_lens, num_needed_tokens


