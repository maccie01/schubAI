import { exec } from 'child_process';
import { promisify } from 'util';
import fs from 'fs/promises';
import path from 'path';
import logger from './logger';
import { updateGpuUtilization } from './metrics';

const execAsync = promisify(exec);

interface DockerMetrics {
  timestamp: string;
  service: string;
  cpuUsage: string;
  memoryUsage: string;
  gpuUtilization?: string;
}

interface BuildIssue {
  date: string;
  service: string;
  error: string;
  resolution?: string;
}

const METRICS_DIR = path.join(process.cwd(), 'data', 'metrics');
const BUILD_ISSUES_FILE = path.join(METRICS_DIR, 'build-issues.json');
const METRICS_FILE = path.join(METRICS_DIR, 'docker-metrics.json');

export async function initializeMetricsTracking() {
  try {
    await fs.mkdir(METRICS_DIR, { recursive: true });
    
    // Initialize files if they don't exist
    for (const file of [BUILD_ISSUES_FILE, METRICS_FILE]) {
      try {
        await fs.access(file);
      } catch {
        await fs.writeFile(file, '[]');
      }
    }
  } catch (error) {
    logger.error('Failed to initialize metrics tracking:', error);
  }
}

export async function trackDockerMetrics() {
  try {
    const services = ['perplexica-backend', 'perplexica-frontend', 'qdrant'];
    const metrics: DockerMetrics[] = [];

    for (const service of services) {
      const { stdout: stats } = await execAsync(
        `docker stats --no-stream --format "{{.CPUPerc}}\t{{.MemUsage}}" ${service}`
      );
      const [cpuUsage, memoryUsage] = stats.trim().split('\t');

      let gpuUtilization;
      if (service === 'perplexica-backend') {
        // Get GPU stats for M2 Pro using Metal framework
        try {
          const { stdout: gpuStats } = await execAsync(`
            ioreg -l | grep "IOGPUMetalStatistics" | \
            awk -F'"' '{print $4}' | \
            grep "Device Utilization %" | \
            awk '{print $NF}'
          `);
          gpuUtilization = gpuStats.trim();
          
          // Update Prometheus metric
          const utilizationValue = parseFloat(gpuUtilization);
          if (!isNaN(utilizationValue)) {
            updateGpuUtilization(utilizationValue);
          }
        } catch (error) {
          logger.warn('Failed to get Metal GPU metrics:', error);
          // Fallback to CPU metrics
          const { stdout: cpuLoad } = await execAsync('ps -A -o %cpu | awk \'{s+=$1} END {print s}\'');
          logger.info('System running on CPU, current load:', cpuLoad.trim());
        }
      }

      metrics.push({
        timestamp: new Date().toISOString(),
        service,
        cpuUsage,
        memoryUsage,
        gpuUtilization,
      });
    }

    // Read existing metrics
    const existingMetrics = JSON.parse(await fs.readFile(METRICS_FILE, 'utf-8'));
    existingMetrics.push(...metrics);

    // Keep only last 1000 entries
    const trimmedMetrics = existingMetrics.slice(-1000);
    await fs.writeFile(METRICS_FILE, JSON.stringify(trimmedMetrics, null, 2));

  } catch (error) {
    logger.error('Failed to track Docker metrics:', error);
  }
}

export async function recordBuildIssue(issue: BuildIssue) {
  try {
    const issues = JSON.parse(await fs.readFile(BUILD_ISSUES_FILE, 'utf-8'));
    issues.push(issue);
    await fs.writeFile(BUILD_ISSUES_FILE, JSON.stringify(issues, null, 2));
  } catch (error) {
    logger.error('Failed to record build issue:', error);
  }
}

// Start metrics tracking on module import
initializeMetricsTracking().then(() => {
  // Track metrics every 5 minutes
  setInterval(trackDockerMetrics, 5 * 60 * 1000);
  trackDockerMetrics(); // Initial tracking
}); 