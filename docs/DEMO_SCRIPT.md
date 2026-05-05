# Live Demo Script (7–10 minutes)

This is a precise, rehearsable script. Each step has a **what to type** and
**what to say while it runs**. Do not improvise — improvising kills demos.

---

## Pre-demo checklist (do this ~10 min before you present)

- [ ] Laptop plugged in, screen mirroring tested.
- [ ] Browser zoom set to 125% so the room can read the screen.
- [ ] Jenkins is already running: `docker compose up -d` was run earlier.
- [ ] You can open http://localhost:8081 and you are logged in.
- [ ] The pipeline job has at least **one previous successful build**
      (a "green" baseline makes the demo easier).
- [ ] The deliberately failing test in `app/tests/test_main.py` is currently
      **commented out** (we'll uncomment it live).
- [ ] Two terminals open side-by-side: one for `git`, one for `docker ps` /
      `curl`.
- [ ] No other apps using port 8080 or 8081: `lsof -i :8080`.

---

## The demo, step by step

### Part A — "Here is the working pipeline" (2 min)

| Time | Action | What to say |
|---|---|---|
| 0:00 | Show Jenkins dashboard, click **Build Now**. | "I'm triggering a build manually now — but later I'll show how a Git push triggers it automatically." |
| 0:30 | Show the **Stage View** as stages light up green. | "You can see the five stages we defined: Checkout, Build, Test, Package, Deploy. Each one runs only if the previous one succeeded." |
| 1:30 | Click into the **Test** stage logs. Show the pytest output. | "Six unit tests, all passing. If any test had failed, the pipeline would stop right here." |
| 1:50 | Switch to terminal: `curl http://localhost:8080/`. | "And here is the freshly deployed app, live on port 8080, served by the container Jenkins just built and started." |

### Part B — "Pipeline-as-code" (1 min)

| Time | Action | What to say |
|---|---|---|
| 2:00 | Open the `Jenkinsfile` in your editor on screen. | "This single file *is* our pipeline. It lives in Git, it's reviewed in pull requests, just like application code." |
| 2:30 | Highlight the `environment {}` block. | "Environment variables are defined once, used in every stage." |
| 2:45 | Highlight the `post { failure {} }` block. | "If any stage fails, this block fires — we automatically clean up so we never leave a half-broken container running." |

### Part C — The deliberate-failure demo (3 min) ⭐ STAR MOMENT

| Time | Action | What to say |
|---|---|---|
| 3:00 | Open `app/tests/test_main.py`. **Uncomment** the `test_intentional_failure_for_demo` block. | "Now I'll introduce a bug — this test asserts that 2+2 equals 5. Watch what happens when we push it." |
| 3:30 | `git add . && git commit -m "demo: break a test on purpose" && git push` | "The change is now on GitHub." |
| 4:00 | Switch to Jenkins. Either click **Build Now** or wait for SCM polling (2 min). For demo speed, click **Build Now**. | "Jenkins picks up the new commit and starts a fresh build." |
| 4:30 | Watch stages: Checkout ✅, Build ✅, **Test ❌**. | "Checkout passed. Build passed. And here — Test fails. Look at this: the Package and Deploy stages **never run**. The bad code is blocked." |
| 5:30 | Switch to terminal: `curl http://localhost:8080/` — **the OLD version is still running**. | "Critically, the previously deployed app is **still serving requests**. Production was never affected by the broken commit. This is the whole point of a CI/CD pipeline." |

### Part D — Recovery (1 min)

| Time | Action | What to say |
|---|---|---|
| 6:00 | Re-comment the failing test. `git commit -am "fix: remove demo failure" && git push` | "We push the fix..." |
| 6:30 | Click **Build Now**. All five stages go green. | "...and the pipeline goes all green again. New version deployed." |
| 7:00 | `curl http://localhost:8080/` → notice version number incremented (build number). | "Notice the version number incremented — that's the Jenkins build number we tagged the image with." |

### Part E — Wrap (30s)

| Time | Action | What to say |
|---|---|---|
| 7:30 | Go back to the slide deck, final slide. | "So in seven minutes we've shown a complete pipeline-as-code workflow with automatic failure handling, just like we'd run in production. Happy to take questions." |

---

## If something goes wrong on stage

| Symptom | Recovery (stay calm) |
|---|---|
| Jenkins build hangs | Click **Abort**, click **Build Now** again. Buy time: explain a slide while it runs. |
| `docker: permission denied` | You forgot `usermod -aG docker jenkins` step — restart the Jenkins container. |
| Port 8080 already in use | `docker stop $(docker ps -q --filter publish=8080)` — explain you're cleaning up an old container. |
| GitHub polling not picking up changes | Click **Build Now** manually and explain *"in production this would be a webhook; we're using polling for the demo."* |
| Internet down | You don't need it — Jenkins, GitHub (cloned locally), and Docker all run on localhost. |

The graders are watching how you handle problems too — calm troubleshooting is
itself worth marks under *"Ability to handle minor issues during demo."*
