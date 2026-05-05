# Troubleshooting & Reflection

Every issue listed here is something you will likely hit while building the
project. Pick the **two most interesting ones** and discuss them on slide 8 —
this is where the *Problem-Solving & Reflection* marks come from.

---

## 1. `docker: permission denied while trying to connect to the Docker daemon socket`

**When it happens:** First time the `Package` stage runs.

**Why:** The `jenkins` user inside the Jenkins container does not have
permission to read `/var/run/docker.sock`.

**Fix (already in `Dockerfile.jenkins`):**
```dockerfile
RUN groupadd -f -g 999 docker && usermod -aG docker jenkins
```

**Caveat:** GID `999` matches the Docker group on Ubuntu/Debian hosts. On
some macOS/Windows setups using Docker Desktop the socket is owned
differently and this fix isn't needed (the socket has open permissions in the
VM). If you still get permission denied, run
`docker exec jenkins-server ls -l /var/run/docker.sock` to see the
owner GID, then update the Dockerfile.

**Why this matters in the real world:** Mounting the host Docker socket is
sometimes called "Docker outside of Docker" (DooD). It's powerful but
**security-sensitive** — anything inside the Jenkins container effectively
has root on the host. In production you'd use Kubernetes-native runners
(Kaniko, Buildah) instead.

---

## 2. `Cannot connect to the Docker daemon`

**When it happens:** You forgot to mount the socket, or you started Jenkins
without Docker Desktop running.

**Fix:** Confirm Docker Desktop / `dockerd` is running, then check
`docker-compose.yml` has the line:
```yaml
- /var/run/docker.sock:/var/run/docker.sock
```
Restart: `docker compose down && docker compose up -d`.

---

## 3. Port `8081` or `8080` already in use

**When it happens:** Another local service is bound to the same port.

**Fix:** Either kill the other process or change the host-side mapping:
```yaml
ports:
  - "8082:8080"   # Jenkins UI -> http://localhost:8082
```
And in `Jenkinsfile`, change `APP_PORT = '8090'` if `8080` is taken.

---

## 4. Pipeline can't find `python3`

**When it happens:** Build stage fails with `python3: command not found`.

**Why:** The default Jenkins image has no Python.

**Fix (already in `Dockerfile.jenkins`):** We install `python3`,
`python3-pip`, and `python3-venv`. If you change Jenkins images, redo this.

---

## 5. Jenkins can't see the new commit on GitHub

**When it happens:** You pushed a change but Jenkins doesn't notice.

**Why:** You set up SCM polling but the schedule hasn't fired yet, OR you
set up a webhook and your laptop's `localhost` is not reachable from
github.com (it isn't — that's normal).

**Two fixes for the demo:**
- **Polling:** under *Build Triggers*, tick *Poll SCM* and use `H/2 * * * *`
  (every two minutes). Slow, but reliable on any network.
- **Manual trigger during demo:** just click *Build Now*. Mention this is
  for demo speed and that webhooks would be used in production with a
  publicly reachable Jenkins URL (e.g. behind a reverse proxy or hosted on
  a cloud VM).

---

## 6. Pytest can't import `app.main`

**When it happens:** Test stage logs show `ModuleNotFoundError: No module named 'app'`.

**Why:** Python only treats a folder as a package if it contains
`__init__.py`. The folder also needs to be in `PYTHONPATH` when pytest runs.

**Fix:** We ship empty `app/__init__.py` and `app/tests/__init__.py` files.
Pytest is run from the project root, so `app.main` resolves correctly.

---

## 7. Old container keeps running on port 8080 between builds

**When it happens:** Deploy stage fails with `port already allocated`.

**Why:** Previous build's container is still bound to port 8080.

**Fix (already in `Jenkinsfile`):**
```bash
docker stop ${CONTAINER_NAME} 2>/dev/null || true
docker rm   ${CONTAINER_NAME} 2>/dev/null || true
```
The `|| true` is critical: on the very first build there's nothing to stop,
and we don't want that case to fail the build.

---

## 8. Smoke test in Deploy stage fires before app is ready

**When it happens:** `curl: (7) Failed to connect to localhost port 8080`.

**Why:** Flask takes ~2 seconds to start. The container is *running* but not
yet *listening*.

**Fix (already in `Jenkinsfile`):**
- A `sleep 5` between `docker run` and `curl`.
- A Docker `HEALTHCHECK` directive in the Dockerfile (so orchestrators can
  rely on a real readiness signal in production).

**Real-world note:** A 5-second sleep is a code smell. In production you'd
poll `/health` in a loop with a timeout, or use Kubernetes readiness probes.
For a 7-minute demo, the sleep is pragmatic.

---

## 9. Jenkins forgets everything after `docker compose down`

**When it happens:** You restart your laptop, lose all jobs and history.

**Why:** You ran `docker compose down -v` (the `-v` deletes the named volume
`jenkins_home`).

**Fix:** Use plain `docker compose down` (without `-v`) for normal
shutdowns. The named volume preserves all Jenkins config across restarts.

---

## 10. The `cleanWs()` step at the end deletes your venv every build

**Yes, that's intentional.** Each build starts fresh — that's a CI virtue,
not a bug. It guarantees the build is reproducible from a clean state, the
way it would run on a brand-new agent.

If you want to *cache* dependencies for speed in real production, you'd
move to a Docker-based build agent that pre-bakes the dependencies, or use
a `pip` cache directory mounted as a volume.

---

## Reflection: what would we do differently in production?

These are excellent talking points if a grader asks you a question:

1. **Don't mount the host Docker socket.** Use Kaniko or Buildah inside the
   pipeline to build images without granting host root.
2. **Push images to a registry** (Docker Hub, ECR, GHCR) instead of using
   them only locally. This separates *build* from *deploy* properly.
3. **Deploy to Kubernetes**, not a single `docker run`. The pipeline would
   `kubectl apply` a manifest, and K8s handles rollouts and rollbacks.
4. **Add a security scan** (Trivy or Snyk) as a sixth stage between
   *Package* and *Deploy*. Fail the build if any HIGH or CRITICAL CVE is
   found in the image.
5. **Replace SCM polling with webhooks** behind a public URL.
6. **Run Jenkins behind HTTPS**, with proper auth (LDAP / GitHub OAuth /
   SAML), not the default local admin.

Mentioning even one or two of these on slide 8 demonstrates you understand
the *limits* of the tutorial setup — strong evidence of critical thinking.
