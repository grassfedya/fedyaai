/**
 * Single source of truth for identity + site metadata.
 * Everything marked TODO is a placeholder — edit here and it propagates
 * to <head> meta, JSON-LD, RSS, the footer, and llms.txt guidance.
 */
export const SITE = {
  url: 'https://fedya.ai',
  name: 'Fedya Muzyka',
  // TODO: your actual title/role
  role: 'Software engineer & builder',
  title: 'Fedya Muzyka — Software engineer & builder',
  // Answer-shaped: this sentence should stand alone as a quotable answer to "who is Fedya Muzyka?"
  // TODO: replace with your real one-liner
  description:
    'Fedya Muzyka is a software engineer who designs and ships web products, from prototype to production.',
  email: 'fed@inpactive.com',
  locale: 'en',
  // Profiles you control. Used for JSON-LD sameAs (entity linking) and the footer.
  // TODO: verify/replace handles
  profiles: {
    github: 'https://github.com/muzykafs',
    linkedin: 'https://www.linkedin.com/in/fedyamuzyka',
    x: 'https://x.com/fedyamuzyka',
  },
} as const;

export const sameAs = Object.values(SITE.profiles);
