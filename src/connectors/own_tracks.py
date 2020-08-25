from datetime import datetime
from typing import List

import psycopg2

from src.models.calendar import Owner
from src.utils.file import File
from src.utils.logger import Logger


class OwnTracks:
    Logger.sub_sub_title('Loading OwnTracks')
    credentials = File.read_json('src/credentials/own_tracks.json')

    @classmethod
    def get_records(cls, start: datetime, end: datetime, owner: Owner) -> List[tuple]:
        user_id = {Owner.carrie: 3, Owner.larry: 2}[owner]
        conditions = 'WHERE ' + ' AND '.join([
            f'time > \'{start.strftime("%Y-%m-%d %H:%M:%S")}\'',
            f'time < \'{end.strftime("%Y-%m-%d %H:%M:%S")}\'',
            f'user_id = {user_id}'
        ])
        query = f'SELECT * FROM public.positions {conditions}'

        conn = psycopg2.connect(**cls.credentials)
        cur = conn.cursor()
        cur.execute(query)
        records = cur.fetchall()
        conn.close()
        return records
