from pydantic import BaseModel

class UserDataBase(BaseModel):
    rut: str
    digito_verificador: int
    nombre: str
    apellido: str
    email: str

class UserDataCreate(UserDataBase):
    pass

class UserData(UserDataBase):
    class Config:
        orm_mode = True