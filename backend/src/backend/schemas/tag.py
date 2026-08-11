from pydantic import BaseModel, ConfigDict


class Tags(BaseModel):
    id: int
    name: str
    model_config = ConfigDict(from_attributes=True)

class TagsResponse(Tags):
    pass


class TagCreate(BaseModel):
    name: str

