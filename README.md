# SE4206 — Jenkins Multi-Stage CI/CD Pipeline

**Course:** Software Development and Operations (SE4206) — Umm Al-Qura University
**Project:** DevOps Project Idea #2 — *Multi-Stage Pipeline with Deployment*

---

## 1. What this project demonstrates

A single push to GitHub triggers a Jenkins pipeline that automatically:

1. Pulls the source code
2. Installs dependencies in an isolated virtualenv
3. Runs unit tests (and **stops the pipeline if any test fails**)
4. Packages the app as a versioned Docker image
5. Deploys the new image as a running container, then performs a smoke test

The whole thing is defined as code in a single `Jenkinsfile` — the modern
DevOps pattern. No clicking through Jenkins GUI menus.

---

## 2. Architecture

```
┌────────────┐   git push   ┌──────────────┐   webhook/poll   ┌───────────────┐
│ Developer  │─────────────▶│   GitHub     │─────────────────▶│   Jenkins     │
└────────────┘              └──────────────┘                  │  (in Docker)  │
                                                              └───────┬───────┘
                                                                      │ executes
                                                                      ▼
                                              ┌─────────────────────────────────────┐
                                              │   Pipeline stages (Jenkinsfile)     │
                                              │                                     │
                                              │  Checkout → Build → Test → Package  │
                                              │             → Deploy                │
                                              └────────────┬────────────────────────┘
                                                           │ docker build / docker run
                                                           ▼
                                                  ┌──────────────────┐
                                                  │ Host Docker daemon│
                                                  │ runs Flask app on │
                                                  │ localhost:8080    │
                                                  └──────────────────┘
```

**Key design choice — Jenkins runs inside a container, but uses the host's
Docker daemon** (we mount `/var/run/docker.sock`). This means:

- Setup is one command on any laptop with Docker (no native install).
- When Jenkins runs `docker build`, the image is built on the host.
- When Jenkins runs `docker run -p 8080:5000`, the container is reachable on
  the host's `localhost:8080`. Your grader can `curl` it directly.

---

## 3. Technology stack & justification

| Layer | Choice | Why (real-world relevance) |
|---|---|---|
| **App language** | Python 3.11 + Flask | Smallest possible *meaningful* web app. Fast container startup, tiny image, readable for a 7-min demo. Every backend microservice tutorial in industry uses something like this. |
| **Test framework** | pytest + pytest-flask | Industry standard for Python. Produces JUnit XML that Jenkins natively understands. |
| **Container** | Multi-stage Dockerfile, non-root user, HEALTHCHECK | Real production patterns — *not* a "single-FROM" toy Dockerfile. Smaller, more secure. |
| **CI/CD** | Jenkins LTS in Docker, declarative `Jenkinsfile` | Jenkins is the most widely deployed CI server in enterprise. Declarative pipeline is the recommended modern syntax. |
| **Pipeline-as-code** | `Jenkinsfile` checked into Git | The whole pipeline is versioned alongside the app. Anyone cloning the repo gets the same pipeline. This is exactly what the rubric asks for: *"Learn pipeline-as-code, not just GUI jobs."* |
| **Deploy target** | Docker container on the same host | The brief says "deploy locally". A full Kubernetes deploy would distract from the *pipeline* learning objective. |

---

## 4. Repository layout

```
se4206-jenkins-cicd/
├── app/
│   ├── main.py                 ← Flask app (4 endpoints)
│   └── tests/
│       └── test_main.py        ← pytest unit tests
├── Dockerfile                  ← Multi-stage build for the Flask app
├── Dockerfile.jenkins          ← Custom Jenkins image (adds Docker CLI + Python)
├── docker-compose.yml          ← One-command Jenkins setup
├── Jenkinsfile                 ← The pipeline (5 stages + post actions)
├── requirements.txt            ← Pinned Python deps
├── .gitignore
├── README.md                   ← This file
└── docs/
    ├── PRESENTATION_OUTLINE.md ← Slide-by-slide outline (5–7 min)
    ├── DEMO_SCRIPT.md          ← Minute-by-minute live demo script
    └── TROUBLESHOOTING.md      ← Errors you will hit + how to fix them
```

---

## 5. Quick start (do this once, well before demo day)

### Prerequisites
- Docker Desktop (Windows/macOS) **or** Docker Engine (Linux) — that's it.
- A free GitHub account.
- ~2 GB free disk space.

### Step 1 — Push this project to GitHub
```bash
cd se4206-jenkins-cicd
git init
git add .
git commit -m "Initial pipeline project"
git branch -M main
git remote add origin https://github.com/<YOUR-USER>/se4206-jenkins-cicd.git
git push -u origin main
```

### Step 2 — Start Jenkins
```bash
docker compose up -d --build
```
Wait ~60 seconds, then open **http://localhost:8081**.

Get the initial admin password:
```bash
docker exec jenkins-server cat /var/jenkins_home/secrets/initialAdminPassword
```
Paste it, then **Install suggested plugins** → create an admin user.

### Step 3 — Create the pipeline job
1. *New Item* → name it `se4206-pipeline` → choose **Pipeline** → OK.
2. Scroll to **Pipeline** section:
   - **Definition:** *Pipeline script from SCM*
   - **SCM:** *Git*
   - **Repository URL:** your GitHub URL
   - **Branch:** `*/main`
   - **Script Path:** `Jenkinsfile` (default)
3. (Optional) under **Build Triggers** tick *Poll SCM* and put `H/2 * * * *`
   so Jenkins polls every two minutes — perfect for the demo without
   needing a public webhook URL.
4. **Save** → click **Build Now**.

If the first run is green, you've earned the "Technical Implementation" marks.

### Step 4 — Verify the deployed app
```bash
curl http://localhost:8080/
curl http://localhost:8080/health
curl http://localhost:8080/api/sum/10/20
```

---

## 6. How each pipeline stage maps to the rubric

| Rubric criterion (3 marks each) | What earns the mark | Where in the project |
|---|---|---|
| **Technical Implementation** | All 5 stages run green; env vars used; post actions present; failure handling rolls back. | `Jenkinsfile`, end-to-end green build. |
| **Understanding & Explanation** | Team can articulate *why* each stage exists and *how* the pieces fit. | This README + `docs/PRESENTATION_OUTLINE.md`. |
| **Demo Quality** | Smooth live run, including the **deliberate-failure scenario** (uncomment the failing test, push, watch pipeline stop at *Test*). | `docs/DEMO_SCRIPT.md`. |
| **Problem-Solving & Reflection** | Honest discussion of issues hit (Docker socket permissions, port clashes, etc.) and how they were resolved. | `docs/TROUBLESHOOTING.md`. |
| **Presentation & Communication** | Clear slides, all four members speak, on time. | `docs/PRESENTATION_OUTLINE.md` includes a speaker map. |

---

## 7. Suggested division of labour (4 students)

| Member | Role | Owns |
|---|---|---|
| **1. App Engineer** | Application & tests | `app/main.py`, `app/tests/`, `requirements.txt` |
| **2. Container Engineer** | Docker images | `Dockerfile`, `Dockerfile.jenkins`, `docker-compose.yml` |
| **3. CI/CD Engineer** | Jenkins & pipeline | `Jenkinsfile`, GitHub webhook/polling, Jenkins job config |
| **4. Lead Presenter** | Slides, demo flow, timing | `docs/` folder, slide deck, runs the demo on screen |

Everyone presents their own section. The rubric explicitly checks
*"all members participate."*

---

## 8. The "wow" moment for your demo

Halfway through the live demo, **uncomment the failing test** in
`app/tests/test_main.py`, push to GitHub, and watch:

1. Jenkins picks up the change automatically.
2. The pipeline runs Checkout → Build → **Test (FAILS)**.
3. The Package and Deploy stages **never execute**.
4. The previously deployed container **keeps serving traffic** (no broken deploy).
5. The `post { failure { … } }` block fires the rollback message.

This single demo step proves you understand:
- pipeline-as-code
- automatic failure handling
- *why* CI/CD prevents bad code reaching production

That is your strongest argument for full marks on
**Technical Implementation**, **Demo Quality**, and **Problem-Solving**.
