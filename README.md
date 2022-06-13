### 1. Write App (Flask)
- The code to build, train, and save the model is in the `Haarcascades` folder.
- Implement the app in `app.py`
### 2. Setup Google Cloud 
- Create new project
- Activate Cloud Run API and Cloud Build API

### 3. Install and init Google Cloud SDK
- https://cloud.google.com/sdk/docs/install

### 4. Dockerfile, requirements.txt, .dockerignore
- https://cloud.google.com/run/docs/quickstarts/build-and-deploy#containerizing

### 5. Cloud build & deploy
```
gcloud builds submit --tag gcr.io/video-segmentation-platform/index
gcloud run deploy --image gcr.io/video-segmentation-platform/index --platform managed
```

### Test
- Test the code with `test/test.py`

