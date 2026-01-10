from pathlib import Path
import sqlite3
from typing import List, Optional

from models import Game, Image


class Database:
    def __init__(self, path: Path):
        self.path = path

    def get_images(self) -> List[Image]:
        cursor = self.connection.execute(
            """
        SELECT 
            Z_PK as pk, 
            Z_ENT as ent, 
            Z_OPT as opt, 
            ZFORMAT as format, 
            ZBOX as box, 
            ZHEIGHT as height, 
            ZWIDTH as width, 
            ZRELATIVEPATH as relative_path
        FROM ZIMAGE
        """
        )
        data = cursor.fetchall()
        return [Image(**d) for d in data]

    def get_games(self, no_cover_art_only=False):
        cursor = self.connection.execute(
            f"""
        SELECT 
            Z_PK as pk, 
            Z_ENT as ent, 
            Z_OPT as opt, 
            ZRATING as rating, 
            ZBOXIMAGE as box_image, 
            ZSYSTEM as system, 
            ZNAME as name, 
            ZGAMETITLE as game_title,
            ZSTATUS as status
        FROM ZGAME
        {'WHERE box_image is null' if no_cover_art_only else ''}
        """
        )
        data = cursor.fetchall()
        return [Game(**d) for d in data]

    def __enter__(self) -> Optional[sqlite3.Connection]:
        """
        Connect to the OpenEmu SQLite database
        """
        if not self.path.exists():
            raise FileNotFoundError(f"Database path ({self.path}) not found.")

        self.connection = sqlite3.connect(str(self.path))
        self.connection.row_factory = sqlite3.Row
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.connection:
            self.connection.close()
