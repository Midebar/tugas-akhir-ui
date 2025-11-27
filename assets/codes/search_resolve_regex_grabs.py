def post_process_logic_solver(self, response_d):
    content = response_d
    marker_pattern = r'(.*?)Dibawah ini tugas yang perlu Anda lakukan(.*?)'
    marker_match = re.search(marker_pattern, content, flags=re.IGNORECASE)
    search_area = content[marker_match.end():] if marker_match else content

    final_block_pattern = (
        r'\*{0,3}(?:Bentuk Akhir)\*{0,3}\s*'
        r'(.*?)'
        r'(?=(\*{0,3}(?:Akhir Blok)\*{0,3})|'
        r'$)' # or end of string
    )

    final_block_match = re.search(final_block_pattern, search_area, flags=re.DOTALL | re.IGNORECASE)

    if not final_block_match:
        return [], None

    block = final_block_match.group(1)

    block_clean = block.strip()
    print(f"\n\nCHOSEN BLOCK:\n\n{block_clean}\n")
    print("END OF CHOSEN BLOCK\n\n")

    clause_pos = re.search(r'Clause\s*Baru', block_clean, flags=re.IGNORECASE)
    clause_after = block_clean[clause_pos.end():]
    m_new = re.search(r'\{(.*?)\}', clause_after, flags=re.DOTALL)

    if not m_new:
        raise ValueError(f"'Clause Baru:' with '{{...}}' not found in expected form.")

    new_clause = m_new.group(1).strip()

    label_pos = re.search(r'Label\s*Cukup', block_clean, flags=re.IGNORECASE)
    label_after = block_clean[label_pos.end():]
    m_label = re.search(r'\[(.*?)\]', label_after, flags=re.DOTALL)
    if not m_label:
        raise ValueError(f"'Label Cukup' with '[...]' not found in expected form [True|False].")

    sufficiency_label = m_label.group(1).strip()
    
    return {
        "new_clause": new_clause,
        "sufficiency_label": sufficiency_label,
    }