import { Hono } from 'hono';
import type { UiResponse } from '@devvit/web/shared';
import { createPost } from '../core/post';
import { seedCommunity } from '../core/seed';
import { configureCommunity } from '../core/setup';

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

menu.post('/auto-configure', async (c) => {
  try {
    const res = await configureCommunity('NoMoreSmokeCults');
    const msg = `Applied ${res.rules.length} rules, ${res.postFlairs.length} post flairs, ${res.userFlairs.length} user flairs!`;
    console.log(`[Devvit Menu] ${msg}`);
    return c.json<UiResponse>(
      {
        showToast: msg,
      },
      200
    );
  } catch (error: any) {
    console.error(`Error auto-configuring community: ${error}`);
    return c.json<UiResponse>(
      {
        showToast: `Config failed: ${error?.message || error}`,
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
          showToast: `Seeded ${result.count}/5 foundational posts to r/NoMoreSmokeCults!`,
        },
        200
      );
    } else {
      return c.json<UiResponse>(
        {
          showToast: `Active posts: ${result.count}/5. (${result.errors.length} errors)`,
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

menu.post('/complete-setup-and-seed', async (c) => {
  try {
    const configRes = await configureCommunity('NoMoreSmokeCults');
    const seedRes = await seedCommunity('NoMoreSmokeCults');
    const msg = `Complete! Configured rules/flairs and ${seedRes.count}/5 posts live.`;
    return c.json<UiResponse>(
      {
        showToast: msg,
      },
      200
    );
  } catch (error: any) {
    console.error(`Error in complete setup: ${error}`);
    return c.json<UiResponse>(
      {
        showToast: `Setup failed: ${error?.message || error}`,
      },
      400
    );
  }
});
