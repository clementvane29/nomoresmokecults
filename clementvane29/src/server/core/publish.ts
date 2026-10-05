import { reddit } from '@devvit/web/server';

export interface PublishEssayParams {
  title: string;
  text?: string;
  url?: string;
  subredditName?: string;
}

export async function publishEssay({
  title,
  text,
  url,
  subredditName = 'NoMoreSmokeCults',
}: PublishEssayParams) {
  if (!text && !url) {
    throw new Error('Post must have either text content or a URL.');
  }

  const cleanSubreddit = subredditName.replace(/^r\//, '');
  console.log(`[Devvit Publish] Submitting to r/${cleanSubreddit}: "${title}"`);

  const submission = await reddit.submitPost({
    subredditName: cleanSubreddit,
    title,
    text,
    url,
  });

  console.log(`[Devvit Publish] Success! ID: ${submission.id}, URL: ${submission.url}`);
  return submission;
}
