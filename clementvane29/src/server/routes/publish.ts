import { Hono } from 'hono';
import { z } from 'zod';
import { publishEssay } from '../core/publish';

const publishSchema = z.object({
  title: z.string().min(1),
  text: z.string().optional(),
  url: z.string().url().optional(),
  subredditName: z.string().optional().default('NoMoreSmokeCults'),
});

export const publishRoute = new Hono();

publishRoute.post('/submit', async (c) => {
  try {
    const body = await c.req.json();
    const parsed = publishSchema.safeParse(body);

    if (!parsed.success) {
      return c.json(
        {
          success: false,
          error: 'Validation failed',
          issues: parsed.error.issues,
        },
        400
      );
    }

    const submission = await publishEssay(parsed.data);

    return c.json({
      success: true,
      post: {
        id: submission.id,
        url: submission.url,
        permalink: submission.permalink ? `https://www.reddit.com${submission.permalink}` : submission.url,
      },
    });
  } catch (error: any) {
    console.error('[Publish Route Error]:', error);
    return c.json(
      {
        success: false,
        error: error.message || 'Failed to publish post',
      },
      500
    );
  }
});
