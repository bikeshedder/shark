import datetime
import json
import os
import tempfile
from decimal import Decimal
from typing import TypedDict

from typst import compile

from shark.utils.json import DecimalEncoder


class TaskInfo(TypedDict):
    name: str
    hours: Decimal


class TaskDict(TaskInfo):
    subtasks: list[TaskInfo]


class DayEntry(TypedDict):
    date: datetime.date
    day_name: str
    tasks: list[TaskDict]


class TimesheetData(TypedDict):
    project_name: str
    employee_name: str
    hours_total: Decimal
    year: int
    month: int
    days: list[DayEntry]


def generate_timesheet(data: TimesheetData):
    current_dir = os.path.dirname(__file__)
    typst_file = f"{current_dir}/timesheet.typ"

    with tempfile.NamedTemporaryFile(delete_on_close=False) as file:
        file.write(json.dumps(data, cls=DecimalEncoder).encode())
        file.close()

        return compile(
            typst_file,
            # Typst can only read files that are within its execution context (cwd)
            # "/" is set as execution context so Typst can access files in /tmp
            root="/",
            sys_inputs={"JSON_DATA_PATH": file.name},
        )
