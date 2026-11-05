import axios from 'axios';

const client = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  timeout: 120000,
});

const mockPrediction = {
  prediction: 'Normal',
  predicted_class: 'Normal',
  confidence: 0.94,
  probabilities: { Normal: 0.94, 'Pancreatic Tumour': 0.06 },
  normal_probability: 0.94,
  pancreatic_tumour_probability: 0.06,
  model_name: 'ResNet50 + CBAM',
  device: 'mock',
};

const useMock = import.meta.env.VITE_USE_MOCK === 'true';

const request = async (promise, endpoint) => {
  try {
    const { data } = await promise;
    return data;
  } catch (error) {
    if (!error.response) {
      throw new Error(`Cannot reach the prediction service at ${client.defaults.baseURL}. Start the FastAPI backend on port 8003 and try again.`);
    }

    const detail = error.response.data?.detail || error.response.data?.message;
    if (error.response.status === 400) {
      throw new Error(detail || 'The selected file is not a supported image. Choose a JPG or PNG file.');
    }
    if (error.response.status === 503) {
      throw new Error(detail || 'The prediction model is not available. Check that the backend model is loaded.');
    }
    if (error.response.status >= 500) {
      throw new Error(detail || `The backend returned an error while processing ${endpoint}.`);
    }
    throw new Error(detail || `The request to ${endpoint} failed with HTTP ${error.response.status}.`);
  }
};

export const fetchHealth = () => (useMock
  ? Promise.resolve({ status: 'ok', model_loaded: true, model_available: true, device: 'mock', class_names: ['Normal', 'Pancreatic Tumour'] })
  : request(client.get('/health'), '/health'));

export const fetchModelInfo = () => (useMock
  ? Promise.resolve({ model_loaded: true, model_available: true, model_name: 'ResNet50 + CBAM', device: 'mock', input_size: 224, class_names: ['Normal', 'Pancreatic Tumour'] })
  : request(client.get('/model-info'), '/model-info'));

export const fetchMetrics = () => (useMock
  ? Promise.resolve({ status: 'not_available' })
  : request(client.get('/metrics'), '/metrics'));

export const analyzeImage = (file) => {
  if (useMock) return new Promise((resolve) => setTimeout(() => resolve(mockPrediction), 900));
  const body = new FormData();
  body.append('file', file);
  return request(client.post('/predict', body), '/predict');
};

export const generateGradCam = (file) => {
  if (useMock) return new Promise((resolve) => setTimeout(() => resolve(null), 700));
  const body = new FormData();
  body.append('file', file);
  return request(client.post('/gradcam', body), '/gradcam');
};
