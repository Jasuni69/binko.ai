import { GeneratedIdea } from '../types';

interface IdeaCardProps {
  idea: GeneratedIdea;
  index: number;
}

export function IdeaCard({ idea, index }: IdeaCardProps) {
  return (
    <div className="idea-card">
      <h3>#{index + 1} {idea.title}</h3>
      <p>{idea.description}</p>

      <div className="fit">
        <strong>Why this fits you:</strong> {idea.why_good_fit}
      </div>

      <div className="steps">
        <h4>First Steps</h4>
        <ol>
          {idea.first_steps.map((step, i) => (
            <li key={i}>{step}</li>
          ))}
        </ol>
      </div>

      <div className="tech">
        {idea.tech_recommendations.map((tech, i) => (
          <span key={i}>{tech}</span>
        ))}
      </div>
    </div>
  );
}
