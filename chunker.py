import re

def chunk_text(text):

    sections = re.split(r"SECTION \d+:", text)

    chunks = []

    for section in sections:

        section = section.strip()

        if len(section) > 50:
            chunks.append(section)

    return chunks