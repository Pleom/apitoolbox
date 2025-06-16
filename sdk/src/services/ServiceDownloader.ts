import { ServicePage } from '../types';
import * as https from 'https';
import * as http from 'http';

// Global constant for the API base URL
const API_BASE_URL = 'https://apitoolbox.dev';

export class ServiceDownloader {
  /**
   * Downloads a service page from the API.
   * @param servicePath - The service path (e.g., 'vercel' or 'vercel/access-groups').
   * @returns The service page data or null if not found.
   */
  public async downloadServicePage(
    servicePath: string
  ): Promise<ServicePage | null> {
    const serviceUrl = `${API_BASE_URL}/services/${servicePath}.json`;
    return this.downloadJson<ServicePage>(serviceUrl);
  }

  private async downloadJson<T>(url: string): Promise<T | null> {
    return new Promise((resolve) => {
      const client = url.startsWith('https:') ? https : http;
      client
        .get(url, (res) => {
          if (res.statusCode !== 200) {
            if (res.statusCode !== 404)
              console.warn(`Failed to download ${url}: ${res.statusCode}`);
            resolve(null);
            return;
          }
          let data = '';
          res.on('data', (chunk) => (data += chunk));
          res.on('end', () => {
            try {
              resolve(JSON.parse(data));
            } catch (error) {
              console.warn(`Failed to parse JSON from ${url}:`, error);
              resolve(null);
            }
          });
        })
        .on('error', (error) => {
          console.warn(`Request error for ${url}:`, error);
          resolve(null);
        })
        .setTimeout(10000, () => {
          console.warn(`Request timeout for ${url}`);
          resolve(null);
        });
    });
  }
}
