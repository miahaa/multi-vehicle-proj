from pydantic import BaseModel, conint

class VehicleReq(BaseModel):
    # Any positive integer length is allowed (no multiple-of-10 check)
    length: conint(strict=True, gt=0)
    quantity: conint(strict=True, gt=0)
