import { reddit } from '@devvit/web/server';

export interface SetupReport {
  rules: string[];
  postFlairs: string[];
  userFlairs: string[];
  autoMod: string;
  errors: string[];
}

export const COMMUNITY_RULES = [
  {
    shortName: 'Methodological Neutrality & Forensic Tone',
    description: 'All discourse must focus on systems, documented claims, and financial structures. Ad hominem attacks, insults, or sensationalized drama are strictly forbidden.',
    violationReason: 'Violation of Rule 1: Non-forensic or abusive discourse.',
    kind: 'all' as const,
  },
  {
    shortName: 'Absolute Whistleblower Anonymity',
    description: 'Never disclose Personally Identifiable Information (PII) of victims or whistleblowers. Redact names, addresses, and private contacts prior to posting.',
    violationReason: 'Violation of Rule 2: Doxxing or unredacted personal data.',
    kind: 'all' as const,
  },
  {
    shortName: 'Verifiable Sources Mandatory',
    description: 'Every factual claim must cite primary sources: corporate registries, Form 990 filings, peer-reviewed literature, official sanctions, or public transcripts.',
    violationReason: 'Violation of Rule 3: Unsubstantiated claims lacking primary sources.',
    kind: 'all' as const,
  },
  {
    shortName: 'Zero Local or Personal Feuds',
    description: 'This space investigates global institutional architectures. Private interpersonal disputes or local territorial gossip will be purged immediately.',
    violationReason: 'Violation of Rule 4: Personal grievance or non-global dispute.',
    kind: 'all' as const,
  },
  {
    shortName: 'Mandatory Post Flairs',
    description: 'Every submission must be tagged with the appropriate flair to ensure indexing and rigorous archival structure.',
    violationReason: 'Violation of Rule 5: Missing or miscategorized post flair.',
    kind: 'all' as const,
  },
  {
    shortName: 'Zero Commercial Grift or Spiritual Selling',
    description: 'No promotion of alternative gurus, coaching academies, retreats, crypto tokens, or spiritual services. Commercial extractivism will trigger a ban.',
    violationReason: 'Violation of Rule 6: Commercial promotion or spiritual grifting.',
    kind: 'all' as const,
  },
];

export const POST_FLAIRS = [
  { text: 'Forensic Dossier', backgroundColor: '#800020' },
  { text: 'Eco-Cult Alert', backgroundColor: '#D97706' },
  { text: 'Pseudo-Science Deconstruct', backgroundColor: '#0284C7' },
  { text: 'Entheogen Extraction', backgroundColor: '#7C3AED' },
  { text: 'Legal & Filings', backgroundColor: '#4B5563' },
  { text: 'Discussion & Support', backgroundColor: '#059669' },
];

export const USER_FLAIRS = [
  { text: 'Investigator / Analyst', backgroundColor: '#1E3A8A', modOnly: false },
  { text: 'Verified Whistleblower', backgroundColor: '#B91C1C', modOnly: true },
  { text: 'Independent Academic', backgroundColor: '#047857', modOnly: false },
  { text: 'Community Member', backgroundColor: '#374151', modOnly: false },
];

export const AUTOMOD_CONFIG = `---
# AutoModerator: Mensaje de bienvenida y recordatorio forense
type: submission
is_edited: false
comment: |
    Welcome to **r/NoMoreSmokeCults**.

    *Please ensure your contribution complies with our 6 Community Standards:*
    1. **Primary Sources:** Back all claims with filings, public statements, or scientific literature.
    2. **Anonymity:** Redact all Personally Identifiable Information (PII).
    3. **Tone:** Maintain methodological neutrality. No personal feuds.

    *Archive and long-form dossiers:* [clementvane.substack.com](https://clementvane.substack.com/)
comment_stickied: true
---
# Filtro de palabras clave de estafas comerciales
type: any
body (includes-word): ["buy my course", "crypto spiritual", "exclusive retreat $", "secret awakening", "ascension coaching"]
action: filter
action_reason: "Keyword match for commercial spiritual promotion / grift"
---
`;

export async function setupRules(subredditName: string): Promise<{ success: string[]; errors: string[] }> {
  const success: string[] = [];
  const errors: string[] = [];
  const cleanSub = subredditName.replace(/^r\//, '');

  let existingShortNames = new Set<string>();
  try {
    const rules = await reddit.getRules(cleanSub);
    existingShortNames = new Set(rules.map((r) => r.shortName));
  } catch (err) {
    console.warn(`[Setup Rules] Could not fetch existing rules, proceeding to create:`, err);
  }

  for (const rule of COMMUNITY_RULES) {
    if (existingShortNames.has(rule.shortName)) {
      success.push(`[Rule Exists] "${rule.shortName}"`);
      continue;
    }
    try {
      await reddit.createRule(cleanSub, {
        shortName: rule.shortName,
        description: rule.description,
        kind: rule.kind,
        violationReason: rule.violationReason,
      });
      success.push(`[Rule Created] "${rule.shortName}"`);
      console.log(`[Devvit Setup] Created rule: ${rule.shortName}`);
    } catch (err: any) {
      const msg = `Failed to create rule "${rule.shortName}": ${err?.message || err}`;
      console.error(`[Devvit Setup Error] ${msg}`);
      errors.push(msg);
    }
  }

  return { success, errors };
}

export async function setupFlairs(subredditName: string): Promise<{ postFlairs: string[]; userFlairs: string[]; errors: string[] }> {
  const postFlairs: string[] = [];
  const userFlairs: string[] = [];
  const errors: string[] = [];
  const cleanSub = subredditName.replace(/^r\//, '');

  // Post Flairs
  let existingPostTexts = new Set<string>();
  try {
    const existing = await reddit.getPostFlairTemplates(cleanSub);
    existingPostTexts = new Set(existing.map((f) => f.text));
  } catch (err) {
    console.warn(`[Setup Post Flairs] Could not fetch existing flairs:`, err);
  }

  for (const flair of POST_FLAIRS) {
    if (existingPostTexts.has(flair.text)) {
      postFlairs.push(`[Post Flair Exists] "${flair.text}"`);
      continue;
    }
    try {
      await reddit.createPostFlairTemplate({
        subredditName: cleanSub,
        text: flair.text,
        backgroundColor: flair.backgroundColor,
        textColor: 'light',
      });
      postFlairs.push(`[Post Flair Created] "${flair.text}"`);
      console.log(`[Devvit Setup] Created post flair: ${flair.text}`);
    } catch (err: any) {
      const msg = `Failed to create post flair "${flair.text}": ${err?.message || err}`;
      errors.push(msg);
    }
  }

  // User Flairs
  let existingUserTexts = new Set<string>();
  try {
    const existing = await reddit.getUserFlairTemplates(cleanSub);
    existingUserTexts = new Set(existing.map((f) => f.text));
  } catch (err) {
    console.warn(`[Setup User Flairs] Could not fetch existing flairs:`, err);
  }

  for (const flair of USER_FLAIRS) {
    if (existingUserTexts.has(flair.text)) {
      userFlairs.push(`[User Flair Exists] "${flair.text}"`);
      continue;
    }
    try {
      await reddit.createUserFlairTemplate({
        subredditName: cleanSub,
        text: flair.text,
        backgroundColor: flair.backgroundColor,
        textColor: 'light',
        modOnly: flair.modOnly,
      });
      userFlairs.push(`[User Flair Created] "${flair.text}"`);
      console.log(`[Devvit Setup] Created user flair: ${flair.text}`);
    } catch (err: any) {
      const msg = `Failed to create user flair "${flair.text}": ${err?.message || err}`;
      errors.push(msg);
    }
  }

  return { postFlairs, userFlairs, errors };
}

export async function setupAutoMod(subredditName: string): Promise<{ success: boolean; message: string }> {
  const cleanSub = subredditName.replace(/^r\//, '');
  try {
    await reddit.updateWikiPage({
      subredditName: cleanSub,
      page: 'config/automoderator',
      content: AUTOMOD_CONFIG,
      reason: 'Automated configuration of forensic standards and anti-spam filters',
    });
    return { success: true, message: 'AutoModerator wiki configuration updated successfully.' };
  } catch (err: any) {
    const msg = `Failed to update AutoModerator: ${err?.message || err}`;
    console.error(`[Devvit AutoMod Error] ${msg}`);
    return { success: false, message: msg };
  }
}

export async function configureCommunity(subredditName: string = 'NoMoreSmokeCults'): Promise<SetupReport> {
  const cleanSub = subredditName.replace(/^r\//, '');
  console.log(`[Devvit Setup] Starting complete community configuration for r/${cleanSub}...`);

  const ruleRes = await setupRules(cleanSub);
  const flairRes = await setupFlairs(cleanSub);
  const autoModRes = await setupAutoMod(cleanSub);

  const errors = [...ruleRes.errors, ...flairRes.errors];
  if (!autoModRes.success) {
    errors.push(autoModRes.message);
  }

  return {
    rules: ruleRes.success,
    postFlairs: flairRes.postFlairs,
    userFlairs: flairRes.userFlairs,
    autoMod: autoModRes.message,
    errors,
  };
}
