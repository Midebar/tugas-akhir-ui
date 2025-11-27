def post_process_decompose(self, content, rules_count=None):

    content = (content or "").replace('\u200b', '').replace('\ufeff', '')

    marker_pattern = r'Di bawah ini adalah yang perlu Anda konversikan menggunakan normalisasi.'
    marker_match = re.search(marker_pattern, content, flags=re.IGNORECASE)

    block_header = re.compile(r'\*{0,3}Bentuk Akhir\*{0,3}', re.IGNORECASE)
    m_block = block_header.search(content, pos=marker_match.end())

    area = content[m_block.end():]

    cnf_label_re = re.compile(
        r'(?:Aturan dalam CNF|Aturan CNF|Aturan|Rules)\s*[:\-]?\s*', 
        flags=re.IGNORECASE
    )
    skolem_label_re = re.compile(
        r'(?:Aturan dalam Skolem|Skolemisasi|Skolem|Bentuk Akhir Setelah Skolemisasi|Skolemization)\s*[:\-]?\s*', 
        flags=re.IGNORECASE
    )

    # Construct the pattern string explicitly to avoid parentheses nesting errors.
    boundary_pattern = (
        r'(?:'                                                     # Start outer group
            r'\r?\n\s*'                                            # Newline + whitespace
            r'(?:'                                                 # Start inner grouping for headers
                r'(?:Aturan dalam CNF|Aturan CNF|Aturan \(CNF\)|Aturan|Rules)|'  # CNF headers
                r'(?:Skolemisasi|Skolem|Bentuk Akhir)|'            # Skolem headers
                r'(?:\*{0,3}\s*Akhir Blok\s*\*{0,3}|Final Form|###)' # End markers
            r')'                                                   # End inner grouping
        r')'                                                       # End outer group
        r'|$'                                                      # OR End of String
    )

    boundary_re = re.compile(boundary_pattern, flags=re.IGNORECASE)

    def extract_after_label(label_re):
        """Finds label, returns text until next boundary."""
        lab_match = label_re.search(area)
        if not lab_match:
            return None
        start = lab_match.end()
        bound = boundary_re.search(area, pos=start)
        end = bound.start() if bound else len(area)
        return area[start:end].strip()

    cnf_raw = extract_after_label(cnf_label_re)
    skolem_raw = extract_after_label(skolem_label_re)

    def to_lines(raw):
        if not raw: 
            return []
        return [ln.strip() for ln in raw.splitlines() if ln.strip()]

    cnf_lines = to_lines(cnf_raw)
    skolem_lines = to_lines(skolem_raw) if skolem_raw else None

    print(f"CNF Raw: {cnf_lines}")
    print(f"Skolem Raw: {skolem_lines}")

    return cnf_lines, skolem_lines