from pydantic import BaseModel, ConfigDict, Field


def _to_camel(name: str) -> str:
    first, *rest = name.split("_")
    return first + "".join(map(str.capitalize, rest))


class BaseSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)


class CamelSchema(BaseSchema):
    model_config = ConfigDict(alias_generator=_to_camel)


class Dummy(BaseSchema):
    """
    DTO для модели Dummy.
    """

    id: int = Field(title="ID", examples=[1])
    name: str = Field(title="Name", examples=["Test"])


class DummyCreate(BaseSchema):
    """
    DTO создания модели Dummy.
    """

    name: str = Field(title="Name of dummy model", examples=["Test"])
