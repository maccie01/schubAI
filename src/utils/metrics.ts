import client from 'prom-client';
import logger from './logger';

// Create a Registry to register metrics
const register = new client.Registry();

// Add default metrics (CPU, memory, etc.)
client.collectDefaultMetrics({
  register,
  prefix: 'perplexica_',
});

// Custom metrics
const httpRequestDuration = new client.Histogram({
  name: 'perplexica_http_request_duration_seconds',
  help: 'Duration of HTTP requests in seconds',
  labelNames: ['method', 'route', 'status_code'],
  buckets: [0.1, 0.5, 1, 2, 5],
});

const httpRequestTotal = new client.Counter({
  name: 'perplexica_http_requests_total',
  help: 'Total number of HTTP requests',
  labelNames: ['method', 'route', 'status_code'],
});

const gpuUtilization = new client.Gauge({
  name: 'perplexica_gpu_utilization',
  help: 'GPU utilization percentage',
});

const modelInferenceTime = new client.Histogram({
  name: 'perplexica_model_inference_seconds',
  help: 'Model inference duration in seconds',
  labelNames: ['model_name'],
  buckets: [0.1, 0.5, 1, 2, 5, 10],
});

// Register custom metrics
register.registerMetric(httpRequestDuration);
register.registerMetric(httpRequestTotal);
register.registerMetric(gpuUtilization);
register.registerMetric(modelInferenceTime);

export interface MetricsMiddlewareOptions {
  route?: string;
}

// Middleware to track HTTP metrics
export const metricsMiddleware = (options: MetricsMiddlewareOptions = {}) => {
  return (req: any, res: any, next: any) => {
    const route = options.route || req.route?.path || 'unknown';
    const method = req.method;

    const endTimer = httpRequestDuration.startTimer();

    res.on('finish', () => {
      const duration = endTimer();
      const statusCode = res.statusCode.toString();

      httpRequestDuration.observe(
        { method, route, status_code: statusCode },
        duration
      );
      httpRequestTotal.inc({ method, route, status_code: statusCode });
    });

    next();
  };
};

// Track GPU utilization
export const updateGpuUtilization = (utilizationPercentage: number) => {
  gpuUtilization.set(utilizationPercentage);
};

// Track model inference time
export const trackModelInference = (modelName: string, durationSeconds: number) => {
  modelInferenceTime.observe({ model_name: modelName }, durationSeconds);
};

// Metrics endpoint handler
export const metricsHandler = async (_req: any, res: any) => {
  try {
    res.set('Content-Type', register.contentType);
    res.end(await register.metrics());
  } catch (error) {
    logger.error('Error generating metrics:', error);
    res.status(500).end();
  }
}; 