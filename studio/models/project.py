from dataclasses import asdict, dataclass


@dataclass
class Project:
    name: str
    description: str
    path: str
    version: str
    created_at: str
    last_opened: str
    status: str
    dataset: str | None = None

    @classmethod
    def from_dict(cls, data: dict, path: str) -> "Project":
        return cls(
            name=data.get("name", ""),
            description=data.get("description", ""),
            path=path,
            version=data.get("version", "1.0"),
            created_at=data.get("created_at", ""),
            last_opened=data.get("last_opened", ""),
            status=data.get("status", "created"),
            dataset=data.get("dataset"),
        )

    def to_metadata(self) -> dict:
        data = asdict(self)
        data.pop("path", None)
        return data
