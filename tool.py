import os
from enum import Enum

from PySide6.QtGui import QIcon

from common import tool_path


class DataType(Enum):
    OBJECT = "object"
    BINARY = "binary"
    FILE = "file"

class Result:
    def __init__(self, result_dict: dict, value):
        self.value = value
        self.data_type: DataType = DataType(result_dict.get("data_type"))
        self.class_name: str | None = result_dict.get("class", None)
        self.description: str = result_dict.get("description")
        self.mime_type: str = result_dict.get("mime_type")
        if "*" in self.mime_type or len(self.mime_type) == 0:
            raise ValueError("Invalid mime type")

    def __str__(self):
        return "Result(\ndata_type={},\nclass_name={},\ndescription={},\nmime_type={})".format(
            self.data_type, self.class_name, self.description, self.mime_type
        )

    def __repr__(self):
        return self.__str__()

class Arg:
    def __init__(self, arg_dict: dict):
        self.data_type: DataType = DataType(arg_dict.get("data_type"))
        self.class_name: str | None = arg_dict.get("class", None)
        self.description: str = arg_dict.get("description")
        self.mime_types: list[str] = arg_dict.get("mime_type")

    def __str__(self):
        return "Arg(\ndata_type={},\nclass_name={},\ndescription={},\nmime_types={})".format(
            self.data_type, self.class_name, self.description, self.mime_types
        )

    def __repr__(self):
        return self.__str__()

    def is_match(self, mime_type: str) -> bool:
        for mime in self.mime_types:
            if mime == mime_type:
                return True
            if mime.endswith("/*") and mime_type.startswith(mime[:-2]):
                return True
            if mime.startswith("*/") and mime_type.endswith(mime[2:]):
                return True
            if mime == "*/*":
                return True
        return False

    def is_match_result(self, result: Result) -> bool:
        return self.is_match(result.mime_type)

class Input:
    def __init__(self, input_dict: dict):
        self.name: str = input_dict.get("name")
        self.function_name: str = input_dict.get("function_name")
        self.description: str = input_dict.get("description")
        self.keys: list[str] = input_dict.get("keys", [])
        self.args: list[Arg] = [Arg(arg) for arg in input_dict.get("args")]

    def __str__(self):
        return "Input(\nname={},\nfunction_name={},\ndescription={},\nargs={})".format(
            self.name, self.function_name, self.description, self.args
        )

    def __repr__(self):
        return self.__str__()

    def is_match(self, string: str) -> bool:
        if string in self.name:
            return True
        for key in self.keys:
            if string in key:
                return True
        return False


class Tool:
    def __init__(self, file_name, manifest: dict):
        self.file_name = file_name
        self.name = manifest.get("name")
        self.version = manifest.get("version")
        self.manifest_version = manifest.get("manifest_version")
        icon_path: str | None = manifest.get("icon", None)
        if icon_path is not None:
            self.icon: QIcon | None = QIcon(icon_path)
        else:
            self.icon: QIcon | None = None
        self.description = manifest.get("description", "")
        self.author = manifest.get("author", "")
        self.inputs = [Input(item) for item in manifest.get("input", [])]

    def __str__(self):
        return "Tool(name={},\nversion={},\nmanifest_version={},\ndescription={},\nauthor={},\ninput={})".format(
            self.name, self.version, self.manifest_version, self.description, self.author, self.inputs
        )


def load_tool_list() -> list[Tool]:
    tool_list = []
    path = tool_path()
    for item in os.listdir(path):
        file_path = os.path.join(path, item)
        if os.path.isfile(file_path):
            with open(file_path, "r") as f:
                global_namespace = {}
                try:
                    exec(f.read(), global_namespace)
                    manifest = global_namespace.get("manifest")
                    if manifest is None:
                        continue
                    tool = Tool(item, manifest())
                    tool_list.append(tool)
                except Exception as e:
                    print(e)
                    continue
    return tool_list
