import { useState } from 'react';
import { ProfileForm } from './components/ProfileForm';
import { IdeaCard } from './components/IdeaCard';
import { generateIdeas } from './services/api';
import { UserProfile, GenerationResponse } from './types';

function App() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<GenerationResponse | null>(null);

  const handleSubmit = async (profile: UserProfile) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await generateIdeas({
        profile,
        num_ideas: 3,
      });
      setResult(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate ideas');
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

      {result && !isLoading && (
        <div className="results">
          {result.profile_summary && (
            <div className="profile-summary">
              "{result.profile_summary}"
            </div>
          )}

          {result.ideas.map((idea, index) => (
            <IdeaCard key={index} idea={idea} index={index} />
          ))}
        </div>
      )}
    </div>
  );
}

export default App;
