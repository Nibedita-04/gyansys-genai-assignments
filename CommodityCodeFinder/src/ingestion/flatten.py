import os
import json


def flatten_chapters(folder_path: str):
    records = []

    for file in os.listdir(folder_path):
        if not file.endswith(".json"):
            continue

        file_path = os.path.join(folder_path, file)

        with open(file_path, "r", encoding="utf-8") as f:
            chapter_data = json.load(f)

        chapter_code = chapter_data.get("chapter")
        chapter_title = chapter_data.get("chapter_name", "")

        tree = chapter_data.get("hsn_tree", [])

        for heading in tree:  # 4-digit
            heading_code = heading.get("hsn_code")
            heading_desc = heading.get("description", "")

            for sub in heading.get("children", []):  # 6-digit
                sub_code = sub.get("hsn_code")
                sub_desc = sub.get("description", "")

                if not sub_code or len(sub_code) != 6:
                    continue

                full_text = f"""
                Chapter {chapter_code}: {chapter_title}
                Heading {heading_code}: {heading_desc}
                Subheading {sub_code}: {sub_desc}
                """.strip()

                records.append({
                    "id": sub_code,
                    "text": full_text,
                    "metadata": {
                        "chapter_code": chapter_code,
                        "heading_code": heading_code,
                        "subheading_code": sub_code,
                        "hsn_6_digit": sub_code,
                        "chapter_title": chapter_title,
                        "heading_title": heading_desc,
                        "subheading_title": sub_desc
                    }
                })

    return records
