# 🚀 Deployment Guide

## Option 1: Render (Recommended - Easiest)

### Steps:

1. **Sign up at [Render](https://render.com)**
   - Use your GitHub account

2. **Create a New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository: `SrijanG07/Route-Optimizer`
   - Render will auto-detect the `render.yaml` configuration

3. **Configure Environment Variables**
   - Add `GEMINI_API_KEY` in the Render dashboard
   - Get your free API key at: https://makersuite.google.com/app/apikey

4. **Deploy**
   - Click "Create Web Service"
   - Render will automatically build and deploy
   - Your app will be live at: `https://route-optimizer-xxxx.onrender.com`

**Free Tier:**
- ✅ Free SSL certificate
- ✅ Auto-deploy on git push
- ⚠️ Sleeps after 15 min inactivity (wakes in 30s on request)

---

## Option 2: Railway

### Steps:

1. **Sign up at [Railway](https://railway.app)**

2. **Deploy from GitHub**
   - Click "New Project" → "Deploy from GitHub"
   - Select your repository
   - Railway auto-detects Python

3. **Configure**
   - Add environment variable: `GEMINI_API_KEY`
   - Railway will use the `Procfile` automatically

4. **Generate Domain**
   - Go to Settings → Generate Domain
   - Your app will be live at: `https://your-app.railway.app`

**Free Tier:**
- ✅ $5 credit/month
- ✅ No sleeping
- ✅ Better performance than Render free

---

## Option 3: Fly.io

### Steps:

1. **Install Fly CLI**
   ```powershell
   iwr https://fly.io/install.ps1 -useb | iex
   ```

2. **Login and Launch**
   ```powershell
   fly auth login
   fly launch
   ```

3. **Set Environment Variable**
   ```powershell
   fly secrets set GEMINI_API_KEY=your_api_key_here
   ```

4. **Deploy**
   ```powershell
   fly deploy
   ```

**Free Tier:**
- ✅ 3 shared VMs free
- ✅ Always on (no sleeping)
- ✅ Global edge network

---

## Option 4: Vercel (Frontend + Serverless API)

### Steps:

1. **Install Vercel CLI**
   ```powershell
   npm install -g vercel
   ```

2. **Create `vercel.json`** (already included)

3. **Deploy**
   ```powershell
   vercel --prod
   ```

4. **Add Environment Variable**
   - Add `GEMINI_API_KEY` in Vercel dashboard

**Free Tier:**
- ✅ Serverless functions (limited to 10s execution)
- ✅ Best for static sites
- ⚠️ May need to optimize for serverless limits

---

## Post-Deployment Checklist

- [ ] Test all API endpoints at `/docs`
- [ ] Verify frontend loads correctly
- [ ] Test route optimization with sample cities
- [ ] Check AI summary generation works
- [ ] Monitor performance and logs

---

## Troubleshooting

### App not starting?
- Check environment variables are set correctly
- Verify `requirements.txt` has all dependencies
- Check logs in your platform's dashboard

### Slow cold starts?
- Render free tier sleeps after inactivity
- Consider upgrading or using Railway/Fly.io

### API errors?
- Verify `GEMINI_API_KEY` is set correctly
- Check API quota hasn't been exceeded

---

## Custom Domain (Optional)

All platforms support custom domains:
1. Buy domain from Namecheap/GoDaddy
2. Add CNAME record pointing to your app
3. Configure in platform dashboard

---

## Monitoring

- **Render:** Built-in logs and metrics
- **Railway:** Real-time logs in dashboard
- **Fly.io:** `fly logs` command
- **Vercel:** Analytics in dashboard
