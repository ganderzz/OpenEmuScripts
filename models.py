from enum import Enum
from attr import dataclass


# NSBitmapImageRep.FileType
class Format(Enum):
    TIFF = 0
    BMP = 1
    GIF = 2
    JPEG = 3
    PNG = 4


@dataclass
class Base:
    pk: int
    ent: int
    opt: int


@dataclass
class Image(Base):
    format: Format
    box: int
    height: int
    width: int
    relative_path: str


@dataclass
class Game(Base):
    game_title: str  # What user changed name to
    name: str  # Orig name
    system: str
    rating: int
    status: int
    box_image: int  # Key
