from pydantic import BaseModel

class TestModel(BaseModel):
    name: str

print("Pydantic import and model definition successful")
