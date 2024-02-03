import logging
from datetime import datetime
from pathlib import Path
from typing import List

import psycopg2
from skye_comlib.utils.file import File

from src.models.calendar import Owner


class OwnTracks:
    logging.info("Loading OwnTracks")
    credentials = File.read_json(Path("src/credentials/own_tracks.json"))

    @classmethod
    def get_records(cls, start: datetime, end: datetime, owner: Owner) -> List[tuple]:
        user_id = {Owner.carrie: 3, Owner.larry: 2}[owner]
        conditions = "WHERE " + " AND ".join(
            [
                f'time > \'{start.strftime("%Y-%m-%d %H:%M:%S")}\'',
                f'time < \'{end.strftime("%Y-%m-%d %H:%M:%S")}\'',
                f"user_id = {user_id}",
            ],
        )
        query = f"SELECT * FROM public.positions {conditions}"  # noqa: S608

        conn = psycopg2.connect(**cls.credentials)
        cur = conn.cursor()
        cur.execute(query)
        records = cur.fetchall()
        conn.close()
        return records  # noqa: R504
