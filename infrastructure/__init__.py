from enums import StorageType
from .local_storage import LocalStorage
from .seafile_storage import SeafileStorage


def get_target_storage(storage_type: StorageType):
    match storage_type:
        case StorageType.local:
            return LocalStorage
        case StorageType.seafile:
            return SeafileStorage
        case _:
            raise ValueError(f'Неизвестный тип хранилища {storage_type}')
