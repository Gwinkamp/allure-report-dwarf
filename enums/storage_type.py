from .strenum import StrEnum, auto


class StorageType(StrEnum):
    """Перечисление типов хранилищ"""
    local = auto()
    seafile = auto()
    minio = auto()
