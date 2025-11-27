def extract_facts_rules_conjecture(self, content, context_sentence_count=None):
    # Clean invisible characters
    content = (content or "").replace('\u200b', '').replace('\ufeff', '')

    prompt_marker = re.compile(
        r'Di bawah ini(?:\s+adalah(?:\s+yang\s+perlu\s+Anda\s+terjemahkan)?)?:?',
        re.IGNORECASE
    )
    m_prompt = prompt_marker.search(content)
    search_start_pos = m_prompt.end() if m_prompt else 0

    block_header = re.compile(r'\*{0,3}Bentuk Akhir\*{0,3}', re.IGNORECASE)
    m_block = block_header.search(content, pos=search_start_pos)

    if m_block:
        area = content[m_block.end():]
    else:
        area = content[search_start_pos:]

    # Define Patterns for possible headers
    # Include the "End Markers" as a header type.
    patterns = {
        "facts": re.compile(r'(?:Fakta|Facts)\s*[:\-]?\s*', re.IGNORECASE),
        "rules": re.compile(r'(?:Aturan|Rules)\s*[:\-]?\s*', re.IGNORECASE),
        "conj": re.compile(r'(?:Konjektur|Conjecture)\s*[:\-]?\s*', re.IGNORECASE),
        "stop": re.compile(r'(?:\*{0,3}\s*Akhir Blok\s*\*{0,3}|###|```|-{3,})', re.IGNORECASE)
    }

    def extract_section(target_key):
        start_match = patterns[target_key].search(area)
        if not start_match:
            return ""
        
        content_start_idx = start_match.end()
        
        # Find the next header
        next_indices = []
        for key, pat in patterns.items():
            m = pat.search(area, pos=content_start_idx)
            if m:
                next_indices.append(m.start())
        
        # If found upcoming headers, stop at the nearest one (min index).
        # If no headers found, go to end of string.
        if next_indices:
            cutoff_idx = min(next_indices)
            raw_text = area[content_start_idx:cutoff_idx]
        else:
            raw_text = area[content_start_idx:]
            
        return raw_text.strip()

    facts = extract_section("facts")
    rules = extract_section("rules")
    conjecture = extract_section("conj")

    return facts, rules, conjecture