import { drizzle } from 'drizzle-orm/sqlite-proxy';
import { Database } from '@vscode/sqlite3';
import { join } from 'path';
import logger from '../utils/logger';
import * as schema from './schema';

const dbPath = join(process.cwd(), 'data', 'perplexica.db');

const sqlite = new Database(dbPath, (err) => {
  if (err) {
    logger.error('Error opening database:', err);
    process.exit(1);
  }
});

// Create a proxy for drizzle-orm that matches the expected interface
const dbProxy = async (sql: string, params: any[], method: 'run' | 'all' | 'values' | 'get'): Promise<{ rows: any[] }> => {
  return new Promise((resolve, reject) => {
    switch (method) {
      case 'run':
        sqlite.run(sql, params, function(err) {
          if (err) reject(err);
          else resolve({ rows: [{ lastID: this.lastID, changes: this.changes }] });
        });
        break;
      case 'get':
        sqlite.get(sql, params, (err, row) => {
          if (err) reject(err);
          else resolve({ rows: row ? [row] : [] });
        });
        break;
      case 'all':
      case 'values':
        sqlite.all(sql, params, (err, rows) => {
          if (err) reject(err);
          else resolve({ rows: rows || [] });
        });
        break;
    }
  });
};

export const db = drizzle(dbProxy, { schema });

// Ensure database is closed on process exit
process.on('SIGINT', () => {
  sqlite.close((err) => {
    if (err) {
      logger.error('Error closing database:', err);
      process.exit(1);
    }
    process.exit(0);
  });
});
