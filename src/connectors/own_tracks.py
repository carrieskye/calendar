import logging
from datetime import datetime
from pathlib import Path

import psycopg2

from src.enums import Owner
from src.utils import File

logger = logging.getLogger(__name__)


class OwnTracks:
    logger.info("Loading OwnTracks")
    credentials = File.read_json(Path("src/credentials/own_tracks.json"))

    @classmethod
    def get_records(cls, start: datetime, end: datetime, owner: Owner) -> list[tuple]:
        user_id = {Owner.USER: 3, Owner.PARTNER: 2}[owner]
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
