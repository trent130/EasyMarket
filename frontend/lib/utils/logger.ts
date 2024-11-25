import fs from 'fs';
import path from 'path';

const LOG_FILE = path.join(process.cwd(), 'security.log');

export function logSecurityEvent(event: string, details: Record<string, any>) {
  const timestamp = new Date().toISOString();
  const logEntry = `[${timestamp}] ${event}: ${JSON.stringify(details)}\n`;

  fs.appendFile(LOG_FILE, logEntry, (err) => {
    if (err) {
      console.error('Error writing to log file:', err);
    }
  });
}
