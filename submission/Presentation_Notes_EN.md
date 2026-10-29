# Group 8 — Video presentation · 14:30

## 1. PySteps: Python learning with PiPo

**0:00–0:45**

Introduce Group 8 and the learner problem. Say: “PySteps connects a wrong answer with an explanation, a related exercise and a coding activity. PiPo can inspect our learning records and select a next step.” State that the video includes live use of the application.

## 2. The learner problem

**0:45–1:45**

Use one learner throughout the demonstration: a beginner confuses > with >=, practises a comparison, then applies it in gate_status. Explain practical settings: an individual studying independently, a tutor working with a small group, and classroom practice. Each needs concrete feedback, a next task and saved records. These are use scenarios, not reported study outcomes.

## 3. Method: one continuous learning workflow

**1:45–3:15**

Explain the method before switching to live use. Python compares answers to the question bank; course completion requires reading and two independent unhinted answers. Recommendation stays in the current chapter and excludes the question just answered. Optional GLM-4.7 diagnosis analyses reasons; PiPo uses a separate repeated model/tool/observation loop. SQLite connects the activities through a learning state. Explain simple usability: a local launch command, a visible language switch, saved drafts and meaningful errors.

## 4. Live demonstration: mistake feedback

**3:15–5:30**

SWITCH TO THE RUNNING APPLICATION for this full segment; do not remain on this slide. Open Free practice and select boundary_1 (the first conditionals question). Enter “I thought greater than includes equality”, choose B: True, submit and show the fixed incorrect result. Point to the standard explanation and available hints. With the prechecked configured model, request analysis and show the quoted reason; explain that it does not change the answer key. Revise the reason to “I now distinguish > from >=; equality makes this expression false”, reanalyse and show that the attempt count has not increased. Briefly show the language switch and clear labels. Narrate the expected result only after it is visible.

## 5. Live demonstration: PiPo chooses practice

**5:30–8:00**

STAY IN THE APPLICATION. Open PiPo, enter the team access code without showing the provider key, and send the displayed goal. Wait for the real completed response. Expand the visible tool trace and explain the actual calls rather than reading a predetermined sequence. Confirm that the opened question is a valid inspected item in the relevant chapter and not boundary_1. Ask a short follow-up: “Explain why equality matters here without giving me the answer.” Point out tool decisions and the distinction between model-selected tools and Python-executed actions. If the account model cannot complete the turn, show the actual error and explain the observed state; arrange a functioning account before the final recording. Do not substitute simulated test output for this live segment.

## 6. Live demonstration: Python coding

**8:00–10:30**

STAY IN THE APPLICATION. Open Coding challenges → Spaceport Entry Pass. Explain the rule: energy below 20 returns the required recharge string; otherwise a badge permits entry. First run the starter pass body to show useful failing case results, then paste the prepared reference function from the recording guide. Run examples (first two cases), then Check answer (all seven cases for this task). Highlight the 19/20 boundary, all visible passing results and the saved submission. Briefly introduce a syntax error and show its location, then restore the correct source. Explain that the Worker executes browser Python, while the backend stores progress.

## 7. Live demonstration: returning to saved learning

**10:30–11:30**

STAY IN THE APPLICATION. Open Review mistakes and identify the comparison attempt and revised reason. Open Learning progress and show the coding completion/attempt counts. Refresh and confirm records remain in the same browser space. Export a JSON backup and explain that import is a confirmed replacement. These actions establish practical continuity for self-study and tutor-led sessions. Do not clear cookies or import a backup into a real learner space during the recording.

## 8. Engineering method and verification

**11:30–13:30**

Return to the slides. Show domain.py, agent.py and storage.py briefly using prepared windows. Explain functions/classes/collections (Lecture03), prompt contracts and SRS (Lecture04), model plus harness (Lecture05), and requirement/test matching (Lecture06). Show the current saved regression result dated 29 October 2026: 38 passed, including 10 PiPo methods. Explain that model responses in the automated tests are simulated; the live application segment is a separate demonstration. Show one requirement in SPEC and the named test. Describe the review record fields—reviewer, code location, finding, resolution and recheck—and show actual completed records if available. Identify CI as a configured multi-platform pipeline, not an invented successful run. State that AI assisted implementation, tests and documentation.

## 9. Conclusion: feedback connected to a next step

**13:30–14:30**

Summarise only what the audience has just seen: incorrect answer and explanation, revised reason, PiPo-selected practice, task cases and persistent records. State the practical contribution without asserting measured learning gains. Thank the audience. Finish by 14:30, leaving 30 seconds before the 15-minute cap for transitions or variable model latency.


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
