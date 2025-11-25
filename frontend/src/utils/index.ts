import { IdeaWithFeedback, GeneratedIdea, UserProfile, SkillMatch } from '../types';

const STORAGE_KEY = 'binko_ideas';
const PROFILE_KEY = 'binko_profile';

// localStorage save/load
export function saveIdeas(ideas: IdeaWithFeedback[]): void {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(ideas));
  } catch (e) {
    console.error('Failed save to localStorage', e);
  }
}

export function loadIdeas(): IdeaWithFeedback[] | null {
  try {
    const data = localStorage.getItem(STORAGE_KEY);
    return data ? JSON.parse(data) : null;
  } catch (e) {
    console.error('Failed load from localStorage', e);
    return null;
  }
}

export function saveProfile(profile: UserProfile): void {
  try {
    localStorage.setItem(PROFILE_KEY, JSON.stringify(profile));
  } catch (e) {
    console.error('Failed save profile', e);
  }
}

export function loadProfile(): UserProfile | null {
  try {
    const data = localStorage.getItem(PROFILE_KEY);
    return data ? JSON.parse(data) : null;
  } catch (e) {
    console.error('Failed load profile', e);
    return null;
  }
}

// Copy to clipboard
export async function copyToClipboard(text: string): Promise<boolean> {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch (e) {
    console.error('Failed copy', e);
    return false;
  }
}

// Generate unique ID
export function generateId(): string {
  return Date.now().toString(36) + Math.random().toString(36).substr(2);
}

// Convert GeneratedIdea to IdeaWithFeedback
export function enhanceIdea(
  idea: GeneratedIdea,
  profile: UserProfile
): IdeaWithFeedback {
  return {
    ...idea,
    id: generateId(),
    skillMatch: calculateSkillMatch(idea, profile),
  };
}

// Calculate skill match percentage
export function calculateSkillMatch(
  idea: GeneratedIdea,
  profile: UserProfile
): SkillMatch {
  const allUserSkills = [
    ...profile.technical_skills.map(s => s.toLowerCase()),
    ...profile.non_technical_skills.map(s => s.toLowerCase()),
  ];

  const ideaTechs = idea.tech_recommendations.map(t => t.toLowerCase());

  const matchedSkills = ideaTechs.filter(tech =>
    allUserSkills.some(skill =>
      tech.includes(skill) || skill.includes(tech)
    )
  );

  const matchedCount = matchedSkills.length;
  const totalCount = ideaTechs.length;
  const percentage = totalCount > 0 ? (matchedCount / totalCount) * 100 : 0;

  return {
    matchedCount,
    totalCount,
    percentage: Math.round(percentage),
    matchedSkills,
  };
}

// Format idea for copying
export function formatIdeaForCopy(idea: IdeaWithFeedback): string {
  const steps = idea.first_steps.map((step, i) => `${i + 1}. ${step}`).join('\n');

  return `${idea.title}

${idea.description}

Why good fit:
${idea.why_good_fit}

First steps:
${steps}

Tech stack:
${idea.tech_recommendations.join(', ')}`;
}
