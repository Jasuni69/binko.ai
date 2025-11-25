import { useState, useEffect } from 'react';
import { ProfileForm } from './components/ProfileForm';
import { IdeaCard } from './components/IdeaCard';
import { generateIdeas } from './services/api';
import {
  UserProfile,
  GenerationResponse,
  IdeaWithFeedback,
  FeedbackRating,
  FeedbackReason,
} from './types';
import {
  saveIdeas,
  loadIdeas,
  saveProfile,
  loadProfile,
  enhanceIdea,
} from './utils';

function App() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [ideas, setIdeas] = useState<IdeaWithFeedback[]>([]);
  const [profileSummary, setProfileSummary] = useState<string>('');
  const [currentProfile, setCurrentProfile] = useState<UserProfile | null>(null);

  // Load from localStorage on mount
  useEffect(() => {
    const savedIdeas = loadIdeas();
    const savedProfile = loadProfile();

    if (savedIdeas) {
      setIdeas(savedIdeas);
    }
    if (savedProfile) {
      setCurrentProfile(savedProfile);
    }
  }, []);

  // Save to localStorage when ideas change
  useEffect(() => {
    if (ideas.length > 0) {
      saveIdeas(ideas);
    }
  }, [ideas]);

  const handleSubmit = async (profile: UserProfile) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await generateIdeas({
        profile,
        num_ideas: 3,
      });

      // Convert GeneratedIdea to IdeaWithFeedback
      const enhancedIdeas = response.ideas.map(idea => enhanceIdea(idea, profile));

      setIdeas(enhancedIdeas);
      setProfileSummary(response.profile_summary);
      setCurrentProfile(profile);
      saveProfile(profile);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate ideas');
    } finally {
      setIsLoading(false);
    }
  };

  const handleFeedback = (
    ideaId: string,
    rating: FeedbackRating,
    reason?: FeedbackReason
  ) => {
    setIdeas(prevIdeas =>
      prevIdeas.map(idea =>
        idea.id === ideaId
          ? { ...idea, feedback: { rating, reason } }
          : idea
      )
    );
  };

  const handleRegenerate = async (ideaId: string) => {
    if (!currentProfile) return;

    setIsLoading(true);
    setError(null);

    try {
      // Generate just 1 new idea
      const response = await generateIdeas({
        profile: currentProfile,
        num_ideas: 1,
      });

      if (response.ideas.length > 0) {
        const newIdea = enhanceIdea(response.ideas[0], currentProfile);

        // Replace old idea with new one
        setIdeas(prevIdeas =>
          prevIdeas.map(idea => (idea.id === ideaId ? newIdea : idea))
        );
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to regenerate idea');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container">
      <h1>Binko.ai</h1>
      <p className="subtitle">
        Get personalized project ideas based on your skills, goals, and interests.
      </p>

      <ProfileForm onSubmit={handleSubmit} isLoading={isLoading} />

      {error && <div className="error">{error}</div>}

      {isLoading && (
        <div className="loading">
          <p>Analyzing your profile and generating ideas...</p>
        </div>
      )}

      {ideas.length > 0 && !isLoading && (
        <div className="results">
          {profileSummary && (
            <div className="profile-summary">"{profileSummary}"</div>
          )}

          {ideas.map((idea, index) => (
            <IdeaCard
              key={idea.id}
              idea={idea}
              index={index}
              onFeedback={handleFeedback}
              onRegenerate={handleRegenerate}
            />
          ))}
        </div>
      )}
    </div>
  );
}

export default App;
