from pydantic import BaseModel,ConfigDict , HttpUrl

class ApiClientResponse(BaseModel):
    user_id:str
    api_key:str
    webhook_url:HttpUrl | None = None

    model_config=ConfigDict(from_attributes=True)
    