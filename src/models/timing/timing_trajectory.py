from pydantic import BaseModel


class TimingTrajectory(BaseModel):
    origin: str
    destination: str
