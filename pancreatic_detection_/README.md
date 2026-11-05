# Pancreatic-Malignancy-Detection

This project is a research prototype for computer-aided pancreatic tumour classification using deep learning. The project keeps the dataset split strict, trains a ResNet50 baseline, supports CBAM-based model variants, and exposes a small FastAPI + React interface for single-image analysis.

## Project purpose

- Build a robust binary image-classification workflow for pancreatic tumour classification.
- Keep the labels internally fixed as:
  - 0 = Normal
  - 1 = Pancreatic Tumour
- Avoid leakage by holding out the testing set until the final evaluation stage.
- Support image upload, model prediction, and Grad-CAM style attention visualization in a simple web app.
- Keep all outputs tied to actual model predictions rather than hardcoded metrics.

## Dataset structure

The project expects the dataset at the project root in the following structure:

```text
dataset/
├── Training/
│   ├── Normal/
│   └── Pancreatic Tumour/
└── Testing/
    ├── Normal/
    └── Pancreatic Cancer/
```

Important notes:

- Do not rename or move the original dataset folders.
- The code treats the positive class as Pancreatic Tumour internally, even if the folder name in the file system is Pancreatic Cancer.
- If the dataset does not include patient identifiers, patient-level separation cannot be guaranteed.
- In this workspace, the dataset folders are currently empty until the real dataset is placed inside them.

## Environment setup on Windows 11

From the project root:

```powershell
cd "C:\Users\Sherin\OneDrive\Pictures\Desktop\pancreatic detection"
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Python and GPU verification

Run:

```powershell
python test_gpu.py
```

This prints:

- PyTorch version
- CUDA availability
- CUDA version
- GPU name
- GPU memory information when available

If CUDA is not available, the code falls back to CPU automatically.

## Dataset analysis

The notebook is designed to inspect the dataset and create summary plots without modifying the original folders:

```powershell
jupyter notebook notebooks\01_dataset_analysis.ipynb
```

It reports:

- Number of images in each class
- Training class distribution
- Testing class distribution
- Image dimensions
- Image formats
- Corrupted or unreadable images
- Minimum and maximum image size
- Average dimensions where practical

Figures are saved to:

```text
results\figures\
```

## Training

Train the model from the project root:

```powershell
python src\train.py
```

The script:

- Verifies the dataset structure
- Creates a stratified training/validation split from the Training folder
- Applies augmentation only to training samples
- Uses class-weighted cross-entropy for the imbalanced training set
- Saves the best model to `models\best_resnet50.pth`
- Saves the app-ready copy to `models\best_model.pth`
- Saves training curves to `results\figures\training_curves.png`

If the dataset is absent or empty, the training code exits with a clear message rather than producing fake results.

## Evaluation

Run evaluation separately without retraining:

```powershell
python src\evaluate.py
```

This script:

- Loads the saved checkpoint
- Loads the untouched test set
- Runs inference on the test split
- Calculates accuracy, precision, recall, sensitivity, specificity, F1-score, and ROC-AUC
- Creates confusion matrix and ROC figures
- Saves evaluation outputs in `results\metrics\`

## Backend startup

From the project root:

```powershell
run_backend.bat
```

The backend runs on:

```text
http://localhost:8003/
```

## Frontend startup

From the project root:

```powershell
run_frontend.bat
```

Or start both together:

```powershell
start.bat
```

The React app runs on:

```text
http://localhost:5173/
```

## Upload and test the app

1. Start the backend and frontend.
2. Open the frontend in the browser.
3. Upload a JPG or PNG image.
4. Click Analyze Image.
5. Review the predicted class, confidence, class probabilities, and attention overlay.

The app returns a prediction label and probability values only when the model has been trained and saved.

## Model location

The trained model checkpoint is saved to:

```text
models\best_model.pth
```

The Stage 1 script also saves a duplicate at:

```text
models\best_resnet50.pth
```

## Output files

Figures:

```text
results\figures\
├── training_curves.png
├── confusion_matrix.png
└── roc_curve.png
```

Metrics and predictions:

```text
results\metrics\
├── test_metrics.json
├── test_predictions.csv
├── confusion_matrix.csv
└── model_summary.json
```

## Important limitations

- This is a research prototype for computer-aided image analysis, not a clinical diagnostic system.
- The model output should be described as a model prediction, not a patient diagnosis.
- The dataset and labels determine what the model can learn.
- The test set must remain untouched until the final evaluation stage.
- No augmentation should be applied to validation or test images.
- If the model is absent, the API clearly returns: "Trained model not available. Train the model first."
- No random predictions or fabricated results are generated.

## Medical disclaimer

This project is intended for research and educational use only. Model outputs should be interpreted as computer-aided analysis and must be reviewed by qualified medical professionals before any clinical use.
