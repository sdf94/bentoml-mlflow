from __future__ import annotations

import json
import os

import bentoml
import numpy as np
import pandas as pd
import pydantic
from bentoml.io import JSON
from pathlib import Path


class PreProcessor(bentoml.Runnable):
    SUPPORTED_RESOURCES = ()
    SUPPORTS_CPU_MULTI_THREADING = True

    def __init__(self):
        pass

    @bentoml.Runnable.method(batchable=True)
    def remove_na(self, df: pd.DataFrame):
        return df.dropna()

preprocessor_runner = bentoml.Runner(PreProcessor)
runner = bentoml.mlflow.get('sklearn_house_data').to_runner()
svc = bentoml.Service('sklearn_house_data', runners=[preprocessor_runner, runner])


class File(pydantic.BaseModel):
    path:str

file_input = JSON(
    pydantic_model=File,
    validate_json=True)

@svc.api(
    input=file_input,
    output=JSON(),
    route='v1/file/'
)
def predict(file_input: File) -> json:
    file_input = file_input.path
    houses = pd.read_csv(file_input)
    df = preprocessor_runner.remove_na.run(houses)
    ratings = runner.run(df).flatten()
    return {'ratings':ratings}
