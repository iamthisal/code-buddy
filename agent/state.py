from pydantic import BaseModel, Field, ConfigDict
from typing import List


class File(BaseModel):
    path: str = Field(description="The path to the file to be created or modified")
    purpose: str = Field(description="The purpose of the file, e.g. 'main application logic', 'data processing module', etc.")




class Plan(BaseModel):

        name: str = Field(description="The name of app to be built")
        description: str = Field(
            description="A oneline description of the app to be built, e.g. 'A web application for managing personal finances'")
        techstack: str = Field(
            description="The tech stack to be used for the app, e.g. 'python', 'javascript', 'react', 'flask', etc.")
        features: list[str] = Field(
            description="A list of features that the app should have, e.g. 'user authentication', 'data visualization', etc.")
        files: list[File] = Field(description="A list of files to be created, each with a 'path' and 'purpose'")

class ImplementationTask(BaseModel):
    filepath: str = Field(description="The path to the file to be modified")
    task_description: str = Field(description="A description of the task to be executed")


class TaskPlan(BaseModel):
    implementation_steps : list[ImplementationTask] = Field(description="A list of steps to be executed")
    model_config = ConfigDict(extra="allow")  #support to add new attributes






