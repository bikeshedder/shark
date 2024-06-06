#let data = json(sys.inputs.JSON_DATA_PATH)

#set table(
  inset: (0.5em),
)

#show table.cell: it => {
  if it.x == 0 {
    strong(it)
  } else {
    it
  }
}

#let format_tasks(tasks) = {
    if tasks.len() == 0 {
        return ([], [])
    }


    let text_arr = for task in tasks {
        let subtask_descriptions = for subtask in task.subtasks {
            (emph(subtask.name),)
        }

        (((text(weight: "bold")[#task.name]), ..subtask_descriptions).join("\n"),)
    }

    let hours_arr = for task in tasks {
        let subtask_hours = for subtask in task.subtasks {
            (emph(subtask.hours),)
        }

        (((text(weight: "bold")[#task.hours]), ..subtask_hours).join("\n"),)
    }

    (text_arr.join("\n\n"), hours_arr.join("\n\n"))
}

= Timesheet - #data.project_name
#align(end)[#text(weight: "bold", data.employee_name)]

#table(
  columns: (auto, auto, 1fr, auto),
  table.header(
    [*Date*], [*Day*], [*Task*], [*Hours*],
  ),

  ..for row in data.days {
    (
        [#row.date],
        [#row.day_name],
        ..format_tasks(row.tasks)
    )
  }
)

#align(end)[#text(weight: "bold", data.hours_total)]
