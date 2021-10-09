from enum import Enum
import stringcase
from json import JSONEncoder

class ArtifactKind(Enum):
    OperatingSystem = 1
    Application = 2

def to_pascalcase_keyed_dict(obj):
    return { stringcase.pascalcase(k): v for k, v in obj.__dict__.items() }

class ArtifactInfoJSONEncoder(JSONEncoder):

    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.name
        else:
            return to_pascalcase_keyed_dict(obj)