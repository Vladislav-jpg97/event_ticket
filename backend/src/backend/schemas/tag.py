from pydantic import BaseModel


class Tags(BaseModel):
    id: int
    name: str
    slug: str

class TagsResponse(Tags):
    pass