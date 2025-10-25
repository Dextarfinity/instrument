# Cloud Deployment Instructions

## Important: Include Your Trained Model

Before deploying to Railway, you MUST include your trained model file.

### Step 1: Copy Your Model File

Copy `best.pt` from the root directory into the `cloud_deployment` folder:

```cmd
copy ..\best.pt best.pt
```

Or manually copy the file:
- Source: `musical_instrument_dataset_yolo\best.pt`
- Destination: `musical_instrument_dataset_yolo\cloud_deployment\best.pt`

### Step 2: Verify Files

Make sure your `cloud_deployment` folder contains:
- `main.py`
- `requirements.txt`
- `Procfile`
- `railway.json`
- `best.pt` ⭐ **YOUR TRAINED MODEL**

### Step 3: Deploy to Railway

#### Option A: GitHub (Recommended)
1. Create a new GitHub repository
2. Upload the `cloud_deployment` folder contents (including `best.pt`)
3. Connect Railway to your GitHub repository
4. Railway will automatically deploy

#### Option B: Railway CLI
```bash
cd cloud_deployment
railway login
railway init
railway up
```

#### Option C: Direct Upload
1. Go to Railway dashboard
2. Create new project
3. Upload the `cloud_deployment` folder
4. Railway will detect and deploy automatically

### Step 4: Test Your Deployment

Once deployed, you'll get a URL like: `https://your-app.railway.app`

Test endpoints:
- Health: `https://your-app.railway.app/health`
- Docs: `https://your-app.railway.app/docs`

### Model Classes

Your model detects these 11 Filipino musical instruments:
- agung
- bangsi
- chimes
- dabakan
- dlesung
- gabbang
- gandang
- gangsa
- gimbal
- kalatong
- kulintang

## Important Notes

⚠️ **Model File Size**: The `best.pt` file may be large (50-100MB+). Make sure:
- GitHub: Files under 100MB are fine, use Git LFS for larger files
- Railway: Supports large files, no issue

⚠️ **Environment**: Railway will automatically:
- Install dependencies from `requirements.txt`
- Detect Python version
- Set PORT environment variable
- Build and deploy your app

## Troubleshooting

### Model not loading
- Ensure `best.pt` is in the cloud_deployment folder
- Check Railway logs for "Model loaded successfully"
- Verify file was uploaded correctly

### Deployment fails
- Check `requirements.txt` has correct versions
- Review Railway build logs
- Ensure all files are present

### API returns wrong classes
- If you see COCO classes (person, car, etc.), the model didn't load
- The API fell back to downloading a base YOLO model
- Solution: Ensure `best.pt` is in the deployment folder
