from pydantic import BaseModel, ConfigDict


class Categories(BaseModel):
    id: int
    name: str
    slug: str
    model_config = ConfigDict(from_attributes=True)


class CategoriesResponse(Categories):
    pass

class CategoryCreate(BaseModel):
    name: str
    slug: str
