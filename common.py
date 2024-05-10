import os
from PySide6.QtCore import QStandardPaths

app_name = "Datacraft"

def tool_path() -> str:
    return data_path("tool")

def data_path(path: str = None) -> str:
    if path is None:
        return QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation)
    app_data_location = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation)
    app_data_path = os.path.join(app_data_location, app_name.lower(), path)
    if not os.path.exists(app_data_path):
        os.makedirs(app_data_path)
    return app_data_path
