# Deployment Guide

Target topology: **Frontend → Vercel**, **Backend → Render**, **Database → MongoDB Atlas**.

```
Vercel (React static build)  ──HTTPS──▶  Render (FastAPI + model)  ──▶  MongoDB Atlas
```

## Before You Start: the Model File Problem

`backend/ml_model/saved_model/plant_disease_model.keras` is gitignored (Step 2's `.gitignore`
excludes `*.keras` — it's typically tens of MB, too large for a normal git push). A deploy
platform building from your repo won't have it unless you do one of the following:

**Option A — Git LFS (recommended, no code changes)**
```bash
git lfs install
git lfs track "backend/ml_model/saved_model/*.keras"
git add .gitattributes backend/ml_model/saved_model/plant_disease_model.keras
git commit -m "Track trained model with Git LFS"
git push
```
Render pulls LFS objects automatically during its build step. Note GitHub's free tier caps LFS
bandwidth at 1GB/month — fine for occasional redeploys of one model file, but worth knowing.

**Option B — Host the model externally**
Upload the `.keras` file to object storage (S3, GCS, Hugging Face Hub, or even a Google Drive
direct-download link) and download it into `ml_model/saved_model/` as part of Render's build
command, e.g. `pip install -r requirements.txt && curl -L $MODEL_URL -o ml_model/saved_model/plant_disease_model.keras`.
This avoids Git LFS entirely but requires you to manage the external URL.

Either way, `class_names.json` and `disease_info.json` are small text files and are committed to
git normally — no special handling needed for those.

---

## 1. MongoDB Atlas (Production Database)

1. Create a free (M0) cluster at [mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas).
2. **Database Access** → add a database user with a strong password.
3. **Network Access** → add `0.0.0.0/0`. Render's free/starter plans use dynamic outbound IPs, so
   IP allow-listing a specific address isn't practical without a paid static-IP add-on. Restrict
   further only if you upgrade to Render's static outbound IP feature.
4. **Connect** → "Drivers" → copy the connection string. You'll set this as `MONGODB_URI` on
   Render — never commit it to the repo.

## 2. Backend → Render

**Using the included blueprint** (`backend/render.yaml`):
1. In the Render dashboard: New → Blueprint → connect your repo.
2. Render reads `backend/render.yaml` and provisions the service automatically.
3. Fill in the two `sync: false` secrets it prompts for:
   - `MONGODB_URI` — the Atlas connection string from step 1
   - `ALLOWED_ORIGINS` — your Vercel URL once it exists (step 3) — you can leave this blank on the
     first deploy and update it after, since backend and frontend URLs are circular dependencies

**Manual setup** (if you'd rather not use the blueprint):
- New Web Service → connect repo → **Root Directory**: `backend`
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Health Check Path: `/api/v1/health`
- Add the environment variables listed in `backend/.env.example`

Once deployed, verify:
```bash
curl https://<your-render-app>.onrender.com/api/v1/health
```

**Notes on Render's free tier**: the filesystem is ephemeral — anything written to `uploads/` is
lost on redeploy/restart. That's fine for this project (uploads are just referenced by filename in
history, not served back), but don't rely on them persisting. Free-tier services also spin down
after inactivity, so the first request after idle time will be slow (model reload).

## 3. Frontend → Vercel

1. New Project → import the repo → **Root Directory**: `frontend`.
2. Vercel auto-detects Vite; `frontend/vercel.json` is already configured with the build command,
   output directory, and a SPA rewrite rule (`/* → /index.html`) so React Router routes like
   `/upload` don't 404 on refresh or direct link.
3. Environment variable: `VITE_API_BASE_URL` = your Render backend URL
   (`https://<your-render-app>.onrender.com`).
4. Deploy.

## 4. Close the Loop: CORS

Go back to Render and set `ALLOWED_ORIGINS` to your real Vercel URL (e.g.
`https://plant-disease-detection.vercel.app`), then redeploy the backend. Until this is set
correctly, the deployed frontend's requests will fail CORS preflight even though the backend is
reachable — this is the most common "it works locally but not in production" issue for this setup.

## 5. Verify the Deployed App

1. Open the Vercel URL, confirm the Home/About pages render.
2. Go to `/upload`, submit an image, confirm you get either a real prediction (if the model is
   deployed) or a clean `503 Model file not found` message (if not) — not a blank error or crash.
   This mirrors exactly what was verified locally in Step 7.
3. Check browser dev tools' Network tab for the `/predict` request — confirm no CORS errors.

## Environment Variable Summary

| Where | Variable | Value |
|---|---|---|
| Render | `MONGODB_URI` | Atlas connection string |
| Render | `ALLOWED_ORIGINS` | Your Vercel URL |
| Vercel | `VITE_API_BASE_URL` | Your Render URL |
