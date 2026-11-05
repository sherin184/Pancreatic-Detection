import { useState } from 'react';
import { adaptPrediction } from '../services/adapters';
import { analyzeImage, generateGradCam } from '../services/api';

export function usePrediction() {
  const [state, setState] = useState({ loading: false, prediction: null, gradCam: null, error: '', warning: '' });

  const predict = async (file) => {
    setState({ loading: true, prediction: null, gradCam: null, error: '', warning: '' });
    try {
      const raw = await analyzeImage(file);
      const prediction = adaptPrediction(raw);
      let gradCam = null;
      let warning = '';
      try {
        gradCam = await generateGradCam(file);
      } catch (gradCamError) {
        warning = `Prediction completed, but the attention map is unavailable: ${gradCamError.message}`;
      }
      setState({ loading: false, prediction, gradCam, error: '', warning });
      return { prediction, gradCam, warning };
    } catch (error) {
      const next = { loading: false, prediction: null, gradCam: null, error: error.message, warning: '' };
      setState(next);
      return null;
    }
  };

  return { ...state, predict, reset: () => setState({ loading: false, prediction: null, gradCam: null, error: '', warning: '' }) };
}
