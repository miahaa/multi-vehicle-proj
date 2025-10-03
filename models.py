from pydantic import BaseModel, conint, field_validator

class VehicleReq(BaseModel):
    length: conint(strict=True, gt=0)
    quantity: conint(strict=True, gt=0)

    # Lengths are multiples of 10 by spec; enforce to catch bad inputs early.
    @field_validator("length")
    @classmethod
    def multiple_of_10(cls, v: int) -> int:
        if v % 10 != 0:
            raise ValueError("Vehicle length must be a multiple of 10")
        return v
