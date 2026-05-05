# Presentation Outline (5–7 minutes)

> Total: **8 slides**, ~45 sec each. Leaves buffer time for transitions.
> Rubric reminder: *"all members participate"* — speaker map below.

| # | Slide title | Speaker | Time | Key points to say (NOT to read) |
|---|---|---|---|---|
| 1 | **Title slide** | Member 4 | 20s | Course code, project title, group members. Set the scene: "We built a fully automated CI/CD pipeline using Jenkins." |
| 2 | **What problem does CI/CD solve?** | Member 4 | 45s | Manual builds are slow & error-prone. One bad commit can ship to production. CI/CD = automated guardrails between *commit* and *deploy*. |
| 3 | **Architecture diagram** | Member 3 | 60s | Walk left → right: Developer → GitHub → Jenkins → Docker host. Mention Jenkins runs in Docker but uses the host's Docker daemon via the mounted socket. |
| 4 | **The 5 pipeline stages** | Member 3 | 60s | Checkout → Build → Test → Package → Deploy. Stress that each stage is a *gate*: failure stops everything that follows. |
| 5 | **Pipeline-as-code (`Jenkinsfile`)** | Member 1 | 60s | Show the actual file. Highlight: `environment {}` block, `post { failure {} }` block, why we use declarative pipeline syntax. |
| 6 | **The application & containerization** | Member 2 | 60s | Tiny Flask app — picked deliberately so the *pipeline* is the star. Multi-stage Dockerfile, non-root user, HEALTHCHECK = production-grade. |
| 7 | **Failure handling demo (preview)** | Member 1 | 30s | Tease the live demo: "We'll deliberately break a test and watch the pipeline protect production." |
| 8 | **What we learned & challenges** | Member 2 | 45s | Pick 2 real challenges from `TROUBLESHOOTING.md` (e.g., Docker socket permissions, port conflict). Say what we tried, what worked. This slide is where the "Problem-Solving & Reflection" marks are won. |

---

## Slide design tips (helps "Presentation & Communication" mark)

- **One idea per slide.** No 8-bullet walls of text.
- **Use visuals**: the architecture diagram from `README.md` section 2,
  screenshots of a green Jenkins build, a `docker ps` output.
- **Code on slides** = monospace font, max 8 lines, syntax-highlighted.
- **Keep your colour palette to 2–3 colours** — UQU green works well.
- **Slide footer**: SE4206 / group name / slide N of 8.

---

## Things to rehearse (twice, before demo day)

1. The transitions between speakers — a clean handoff line: *"Now Ahmad
   will show you the actual Jenkinsfile."*
2. Time each slide with a stopwatch. If any single slide goes >75s, cut content.
3. Practise the live demo once **with the network unplugged** — forces you
   to demonstrate Jenkins polling locally, and ensures you have a fallback if
   the WiFi in the room is bad.
