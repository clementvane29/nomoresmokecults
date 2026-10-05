import { Hono } from 'hono';
import type { UiResponse } from '@devvit/web/shared';
import { createPost } from '../core/post';
import { seedCommunity } from '../core/seed';

export const menu = new Hono();

menu.post('/post-create', async (c) => {
  try {
    const post = await createPost();

    return c.json<UiResponse>(
      {
        navigateTo: `https://reddit.com/comments/${post.id}`,
      },
      200
    );
  } catch (error) {
    console.error(`Error creating post: ${error}`);
    return c.json<UiResponse>(
      {
        showToast: 'Failed to create post',
      },
      400
    );
  }
});

menu.post('/seed-community', async (c) => {
  try {
    const result = await seedCommunity('NoMoreSmokeCults');
    if (result.success) {
      return c.json<UiResponse>(
        {
          showToast: `Successfully seeded ${result.count} foundational posts to r/NoMoreSmokeCults!`,
        },
        200
      );
    } else {
      return c.json<UiResponse>(
        {
          showToast: `Seeded ${result.count} posts with ${result.errors.length} errors. Check server logs.`,
        },
        200
      );
    }
  } catch (error: any) {
    console.error(`Error seeding community: ${error}`);
    return c.json<UiResponse>(
      {
        showToast: `Failed to seed: ${error?.message || error}`,
      },
      400
    );
  }
});
