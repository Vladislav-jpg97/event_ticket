from pydantic import BaseModel


class Categories(BaseModel):
    id: int
    name: str
    slug: str


class CategoriesResponse(Categories):
    pass