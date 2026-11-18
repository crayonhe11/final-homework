# PySteps 使用说明 / User Guide
### 1. What is PySteps?

PySteps is Group 8's Python learning application. Read concepts, answer quizzes, explain your mistakes, try chapter coding tasks and review your progress. The curriculum contains conditionals, loops, and functions/returns: 15 concepts, 30 multiple-choice questions and six coding tasks.

The first visit uses English. Select **Switch language / 切换语言** at the top to change language. The choice is remembered; code, your input and exact expected return values are unchanged.

### 2. Before you start

Use Windows or macOS with **Python 3.10 or later** and a modern browser. Extract the whole project first and find `main.py` beside this document. Do not run it inside the ZIP.

Normal use requires no Node.js, npm, Docker or third-party Python packages. Keep the supplied `web/static/` folder. Lessons, quizzes, standard feedback, recommendations, coding and backups work without a model key.

### 3. Start on Windows or Mac

1. Open the extracted project folder.
2. On Windows, right-click inside it and choose “Open in Terminal”, if available. Otherwise open a terminal and use `cd` to enter that folder. On Mac, open Terminal, type `cd `, drag the project folder into Terminal and press Return.
3. Run the appropriate command:

| System | Command |
|---|---|
| Windows | `py main.py --port 8011 --open` |
| Mac | `python3 main.py --port 8011 --open` |
| A computer with the `python` command | `python main.py --port 8011 --open` |

4. A browser normally opens automatically. Otherwise open **http://127.0.0.1:8011/**. Always follow the address printed by your terminal.
5. **Keep Terminal running while learning.** Closing the webpage does not stop the server. Press `Control+C` in Terminal to stop, including on Mac.

The default port is **8011**. For `Address already in use`, check whether your existing server is already running. Alternatively change `8011` to `8012` in the command and use the new address. Repeatedly opening terminals does not resolve a port conflict.

If `py`, `python3` or `python` is unavailable, install/configure Python first. If `main.py` cannot be found, enter the correct project directory.

### 4. Complete your first learning session

1. On **Learning map**, select **Start the introduction** and read about variables, output and indentation.
2. Select **I understand. Open chapter one** to enter **Comparison boundaries**.
3. Read its explanation, code and output, then select **I understand. Try the questions**.
4. Choose an option and select **Submit answer**. An empty selection produces a reminder.
5. Read the feedback. The submit position becomes a continuation control. After a wrong answer, use **Add or revise your reasoning**; this edits the same attempt without increasing the count.
6. Select **Try a targeted question**, or **Coding in this chapter** to write code immediately.
7. Open **Learning progress** to see counts, accuracy, concept states and the chart. **Review mistakes** shows your saved reason and the explanation.

Course completion requires reading the concept and independently answering both distinct concept questions correctly, without hints. Free practice and hinted answers are recorded but do not establish course completion. Locked lessons can be previewed; course checks require their prerequisites.

### 5. Try a coding challenge

Select **Coding challenges**, a chapter, then a task. Each chapter has two tasks. You can start without completing quizzes.

1. Read the goal and input/output examples.
2. Complete the editor code, retain the required function name and use `return` as requested.
3. **Run examples** executes the first two cases and does not record task completion.
4. **Check answer** executes every case and records the result; all cases must pass for that submission to pass.
5. Inspect errors and line numbers, edit and check again. **Stop execution** terminates running code. **Restore starter code** asks for confirmation.

Drafts save automatically. Supported features include basic computation, conditions, loops, functions and selected collection operations. Imports, files and network operations are unavailable. Runtime loading has a 60-second threshold; execution stops after four seconds. Keep exact return strings, including Chinese strings required by some English task instructions.

### 6. Use GLM-4.7 and PiPo (optional)

**For a service already configured by your team:** obtain its **team AI access code** from the operator and enter it on the webpage. You do not need the provider API key.

After a wrong answer, add a reason and select **Analyze my reasoning**. GLM-4.7 attempts to provide a possible concept clue, explanation and hint grounded in your text. It cannot change the standard answer. One mistake is not proof of a misconception.

Open PiPo at the lower right, enter the same team code and try “I do not understand loops. Pick a loop question and open it.” PiPo can inspect progress, read lessons, select existing practice and open one activity. Expand its tool trace to see executed calls. It cannot generate new bank questions, change grades or complete the course for you.

The school may take about a minute. Timeouts preserve standard feedback. Avoid repeated retries: each new request may consume credits. **Stop turn** ends browser waiting and pending page actions; it cannot guarantee cancellation of a request already accepted by the school.

**Operator configuration:** if `config.local.json` does not exist, copy `config.example.json` and rename the copy. If it already exists, edit it without replacing existing credentials. Keep it beside `main.py`.

```json
{
  "OPENAI_API_KEY": "",
  "OPENAI_MODEL": "glm-4.7",
  "OPENAI_BASE_URL": "https://maas.eduhk.hk/api/v1",
  "AI_AGENT_MODE": "json",
  "TEAM_ACCESS_CODE": "",
  "PUBLIC_ORIGIN": ""
}
```

- `OPENAI_API_KEY`: the school's application **App Key**, without `Bearer `. This application endpoint previously rejected an Account Key; confirm the correct key/endpoint type with the school.
- `TEAM_ACCESS_CODE`: choose at least 12 characters. This is the value entered on the webpage.
- `OPENAI_MODEL`: the configured Z.ai model is `glm-4.7`, accessed via an OpenAI-compatible school gateway. Verify actual routing in the school application settings.
- `AI_AGENT_MODE`: use `json` for the school gateway; use `native` only for verified native tool-call support.
- `PUBLIC_ORIGIN`: leave empty for local use.

Save, stop the server, restart with your original command and refresh. “Waiting for server configuration” means the server has not loaded a key and a valid team code. A configured flag does not prove provider connectivity. Check the exact `OPENAI_API_KEY` name and environment overrides. `.env` is not loaded automatically.

Keep credentials in local configuration or server environment variables; never distribute them or include them in submissions. The provider receives the required question/reason, or PiPo goal, bounded history and selected learning observations. Refreshing clears the page's team code and PiPo conversation.

### 7. Save, back up and change devices

The project saves learning data to `runtime/learning.sqlite3`. The saved indicator reflects this server. Reuse the same browser and address; changing browser, port or device can produce a different learning space.

In **Learning progress**, select **Export learning records** to download `pysteps-backup-date.json`. On another device, select **Import backup**, choose that file, review the dialog and select **Confirm import**. **Import replaces the current space; export it first if needed.** Cancel preserves it. Imported quiz answers are regraded and AI feedback is replaced by standard explanations.

There is no account login or automatic device synchronisation. For a save conflict, export before refreshing and reconciling changes. Retain `runtime/` after stopping the application to preserve server data.

### 8. Troubleshooting

| Symptom | Action |
|---|---|
| Address does not open | Keep Terminal running and follow its printed port; local use needs no VPN. |
| `Address already in use` | Use the existing server, stop it, or choose another port. |
| Missing browser distribution | Extract the whole project and keep `web/static/`; normal users need no build step. |
| Waiting for server configuration | Check local field names, code length and environment overrides; restart and refresh. |
| App Key / Account Key error | Obtain the key required by this endpoint or ask the administrator for the account-key endpoint. |
| AI timeout or rejected output | Use the standard feedback; retry manually later. New requests may consume credits. |
| Python runtime does not load | Keep the complete project/local Pyodide files and refresh. |
| Save conflict | Export before refreshing; avoid editing the same space in two tabs. |
| Old interface after source edits | Developers rebuild; ordinary users refresh the supplied latest distribution. |

Another computer cannot access your server through its own `127.0.0.1`. Remote teamwork needs a reachable server. For LAN demos, the operator sets `PUBLIC_ORIGIN` to the exact origin and starts with `--host 0.0.0.0`; a local launch is not a public deployment.

### 9. Development, tests and submission

Run:

```bash
python -m unittest discover -s tests -t . -v
```

Use `python3` on Mac or `py` on Windows if appropriate. Tests use temporary databases and simulated models, without paid school requests. `test_http.py` checks principal endpoints; `test_core.py` checks rules/data; `test_agent.py` checks PiPo tools; `test_language.py` checks translation/prompt handling; `test_main.py` checks the real entry point. The local suite ran **85 automated tests**. Look for `Ran 85 tests` and `OK` at the end of the output. Coverage includes progress saves and conflicts, grading feedback, review scheduling and recommendations, PiPo input validation, and diagnosis fallback. Check GitHub **Actions** for the run associated with your commit.

Only frontend developers need Node.js 22 and npm:

```bash
cd web
npm ci
npm run check
npm run build
```

`main.py` is the entry point, `backend/` implements Python behaviour, `data/` supplies curriculum, `web/` contains source and bundled UI, and `tests/` contains verification. `SPEC.md` defines reconstruction contracts and embeds the exact content data in its normative appendix. Run `python scripts/package_rebuild.py` to create the source-free `dist/group8_rebuild_inputs.zip` and validate the embedded data. Validate against its inputs and expected outcomes.

Package Group 8's submission with:

```bash
python scripts/package_submission.py --group 8
```

This produces `dist/group8_project.zip`, excluding local credentials, databases, Git history and development dependencies. The adjacent old-version backup is a private recovery copy that includes local configuration: **do not submit it**. The actual video, individual reports and genuine human review records still need completion/confirmation by members under course requirements.

Course alignment: Lecture03 functions/classes/collections/sorting inform the engine; Lecture04 prompt elements inform diagnosis and human-facing documentation; Lecture05 model/tool loops inform PiPo; Lecture06 FR/NFR and matching verification inform SPEC/tests. SPEC records exact slides, traceability and independent reconstruction steps. Upstream licences are in `licenses/`; React, Lucide and Pyodide are external components, not original reimplementations.


The [bilingual code review record](submission/code_review/Code_Review_EN_ZH.md) includes real screenshots and is included in the project ZIP.

### 10. Automated checks and delivery (CI/CD)

Pushes, PR updates and manual Actions runs trigger: three OSes × two Python versions; fresh browser build; main.py plus eight black-box HTTP contracts against that build; archive/privacy checks; then temporary Docker staging and eight HTTP contracts again. Failures retain reports and stop dependent stages. Staging explicitly disables provider credentials, avoiding school-model charges.

In an Actions run, download tests-*, integration-reports and container-reports for evidence. group8-delivery contains both ZIPs and SHA256SUMS. Reports remain seven days; delivery artifacts remain14days. After every gate passes on main, a versioned GitHub prerelease is published for longer-term downloads. PRs produce tests/artifacts but do not publish main releases.

This provides CI, temporary staging deployment and deployable release delivery. A production server is not configured; a GitHub release is not a running learning website. To deploy an extracted verified project with Docker:

```bash
docker build -t pysteps:group8 .
docker run -d --name pysteps -p 8011:8000 -v pysteps-data:/data -e PUBLIC_ORIGIN=http://127.0.0.1:8011 pysteps:group8
```

Openhttp://127.0.0.1:8011/. On a team server, use its reachable origin and supply model secrets through server variables, never an image. Lecture09 slides5–9 map to objectives/design/execution/assertion analysis;11/13/16to workflow/environments;19–20to actualPR checks. Verify results for the exact commitSHA in Actions.
