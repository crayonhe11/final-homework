# Group 8 — Classroom technical presentation · 4:45

## 1. Python architecture for learning decisions

**0:00–0:35**

Introduce the purpose in one sentence, then focus on architecture. Python owns learning decisions and persistence; React handles interaction; Pyodide runs student code in a browser Worker. Name the module boundaries. Lecture03: functions, classes and modularity.

## 2. Learning rules as testable Python functions

**0:35–1:35**

Use boundary_1 to illustrate deterministic grading: 5 > 5 is False. Explain how dictionaries store questions, sets express prerequisites and passed concepts, and a tuple key ranks candidates. A wrong answer schedules ten minutes; independent due-time success advances stage. Connect each rule to a named LearningTests test. This is technical explanation, not a long product tour.

## 3. PiPo model/tool/observation loop

**1:35–2:40**

Explain one concrete goal: “Review my mistake and open related practice.” The model receives tools, selects one, sees Python’s observation and chooses its next step. Highlight that this differs from keyword routing. Python rejects unknown tools, uninspected IDs and locked lessons. State the per-turn limits: up to five model requests, eight tool executions and one opening. Refer to the multi-round and rejected-action-recovery tests. A brief prepared tool trace may be shown within this timing, but do not spend the slot waiting for a network request.

## 4. Reliable records and controlled code execution

**2:40–3:40**

Explain the two-tab stale-revision example and why atomic writes avoid silent replacement. Distinguish backend learning Python from browser learner Python. A Worker can be terminated without executing student source in the web server. Explain diagnosis evidence checks and shared 60/hour allowance. Match the claims to SQLite/HTTP/AST/AI tests. These are implemented engineering choices, not claims of production security certification.

## 5. Requirements, tests and review evidence

**3:40–4:45**

Show the source of the test count and one SPEC-to-test mapping. Explain that automated model tests are simulated and live teaching quality is a separate evaluation. State how AI assisted implementation, tests and documentation. Describe code review evidence using reviewer, code location, finding, resolution and recheck; show actual records if completed. Conclude that the technical contribution is an inspectable Python learning engine plus a bounded tool-using Agent. Finish at 4:45, preserving 15 seconds within the five-minute slot for transitions. Answer instructor/classmate questions afterwards as directed.
