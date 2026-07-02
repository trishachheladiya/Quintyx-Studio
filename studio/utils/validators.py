INVALID_PROJECT_CHARS = set('<>:"/\\|?*')
MAX_PROJECT_NAME_LENGTH = 100


class ValidationError(ValueError):
    pass


def normalize_project_name(name: str) -> str:
    return " ".join(name.strip().split())


def validate_project_name(name: str) -> str:
    normalized = normalize_project_name(name)

    if not normalized:
        raise ValidationError("Project name is required.")
    if len(normalized) > MAX_PROJECT_NAME_LENGTH:
        raise ValidationError("Project name must be 100 characters or fewer.")
    if any(character in INVALID_PROJECT_CHARS for character in normalized):
        raise ValidationError("Project name contains invalid characters.")
    if normalized in {".", ".."}:
        raise ValidationError("Project name is not valid.")

    return normalized

