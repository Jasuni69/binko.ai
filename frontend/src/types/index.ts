export interface UserProfile {
  technical_skills: string[];
  non_technical_skills: string[];
  experience_level: 'beginner' | 'intermediate' | 'experienced';
  preferred_niches: string[];
  preferred_types: string[];
  hours_per_week?: number;
  budget?: string;
  income_goal?: string;
  timeline?: string;
  interests?: string;
  background?: string;
}

export interface GeneratedIdea {
  title: string;
  description: string;
  why_good_fit: string;
  first_steps: string[];
  tech_recommendations: string[];
  source_idea_ids: string[];
}

export interface GenerationResponse {
  ideas: GeneratedIdea[];
  profile_summary: string;
}

export interface GenerationRequest {
  profile: UserProfile;
  num_ideas: number;
}
