from typing import Literal, Any
from pydantic import BaseModel, Field, model_validator, field_validator
from pydantic.types import NonNegativeInt


class MazeConfig(BaseModel):
    # aliases to tell the model "In Python code this variable is called width,
    # but search a key called WIDTH in the raw data dictionary "config_parsed"
    width: int = Field(alias="WIDTH", ge=2, le=100)
    height: int = Field(alias="HEIGHT", ge=2, le=100)
    entry_coord: tuple[NonNegativeInt, NonNegativeInt] = Field(alias="ENTRY")
    exit_coord: tuple[NonNegativeInt, NonNegativeInt] = Field(alias="EXIT")
    output_file: str = Field(alias="OUTPUT_FILE")
    perfect: bool = Field(default=True, alias="PERFECT")
    seed: int | None = Field(default=None, alias="SEED")
    display_mode: Literal['ascii', 'arcade'] | None = Field(
        default='ascii',
        alias="DISPLAY_MODE"
    )

    # The mode="before" processes a_value BEFORE returning it to Pydantic
    @field_validator('entry_coord', 'exit_coord', mode='before')
    @classmethod
    def parse_coordinates(cls, value: Any) -> tuple[int, int] | Any:
        """ Convert a string 'x,y' to a tuple (int(x),int(y))
        before validation """
        if isinstance(value, tuple):
            return value

        if isinstance(value, str):
            try:
                # will raise explicit error if conversion fails
                x, y = value.split(',')
                # strip() removes spaces and int() casts values
                return (int(x.strip()), int(y.strip()))
            except ValueError:
                raise ValueError("Coordinates must be 'x,y' and integers")

        # if it's something else, let's go... Pydantic will handle the error
        return value

    # `Literal` is strictly case-sensitive -> convert display_mode to lowercase
    @field_validator('display_mode', mode='before')
    @classmethod
    def lowercase_display_mode(cls, value: Any) -> Any:
        """ Set display_mode to lowercase """
        if isinstance(value, str):
            return value.lower()
        return value

    # 'after' = default mode, but "Explicit is better than implicit" :)
    @field_validator('output_file', mode='after')
    @classmethod
    def check_extension(cls, value: str) -> str:
        """ Check file extension is `txt` """
        # handle case sensitivity with lowercase
        if not value.lower().endswith('.txt'):
            raise ValueError("Output file extension must be '.txt'")
        return value

    # @model_validator requires a mode, else Pydantic will raise an error
    @model_validator(mode='after')
    def validate_config_rules(self) -> 'MazeConfig':
        """Applies specific rules for maze config

        Returns
            Self: an instance of the object itself
        """

        # list of all validation errors, to be completed
        errors = []

        if not 0 <= self.entry_coord[0] < self.width:
            errors.append("entry abcisse must be >= 0 and < maze width")

        if not 0 <= self.exit_coord[0] < self.width:
            errors.append("exit abcisse must be >= 0 and < maze width")

        if not 0 <= self.entry_coord[1] < self.height:
            errors.append("entry ordinate must be >= 0 and < maze height")

        if not 0 <= self.exit_coord[1] < self.height:
            errors.append("exit ordinate must be >= 0 and < maze height")

        if self.entry_coord == self.exit_coord:
            errors.append("entry and exit coordinates must be different")

        if errors:
            raise ValueError("\n- " + "\n- ".join(errors))

        return self
