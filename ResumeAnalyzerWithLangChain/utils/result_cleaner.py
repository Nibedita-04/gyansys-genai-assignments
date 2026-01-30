def remove_empty_fields(skill_dict: dict) -> dict:
    cleaned = {}

    if "name" in skill_dict and skill_dict["name"]:
        cleaned["name"] = skill_dict["name"]

    for key, value in skill_dict.items():
        if isinstance(value, list) and len(value) > 0:
            cleaned[key] = value

    return cleaned