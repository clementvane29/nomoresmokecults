import { Hono } from 'hono';
import { serve } from '@hono/node-server';
import { trpcServer } from '@hono/trpc-server';

import { createServer, getServerPort } from '@devvit/web/server';
import { menu } from './routes/menu';
import { triggers } from './routes/triggers';
import { publishRoute } from './routes/publish';
import { appRouter } from './trpc';
import { createContext } from './context';
import { configureCommunity } from './core/setup';
import { seedCommunity } from './core/seed';

const app = new Hono();

const api = new Hono();
api.route('/publish', publishRoute);
api.use(
  '/trpc/*',
  trpcServer({
    endpoint: '/api/trpc',
    router: appRouter,
    createContext,
  })
);

const internal = new Hono();
internal.route('/menu', menu);
internal.route('/triggers', triggers);
internal.route('/publish', publishRoute);

app.route('/api', api);
app.route('/internal', internal);

serve({
  fetch: app.fetch,
  createServer: createServer,
  port: getServerPort(),
});

// Run automated community setup and seeding on launch
setTimeout(async () => {
  try {
    console.log('[Devvit Auto-Launch] Initiating full community setup and seeding...');
    const configResult = await configureCommunity('NoMoreSmokeCults');
    console.log('[Devvit Auto-Launch] Configuration result:', JSON.stringify(configResult));
    const seedResult = await seedCommunity('NoMoreSmokeCults');
    console.log('[Devvit Auto-Launch] Seed result:', JSON.stringify(seedResult));
  } catch (error) {
    console.error('[Devvit Auto-Launch Error]:', error);
  }
}, 1500);
