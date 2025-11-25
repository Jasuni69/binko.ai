import { useState } from 'react';
import { IdeaWithFeedback, FeedbackRating, FeedbackReason } from '../types';
import { copyToClipboard, formatIdeaForCopy } from '../utils';

interface IdeaCardProps {
  idea: IdeaWithFeedback;
  index: number;
  onFeedback: (ideaId: string, rating: FeedbackRating, reason?: FeedbackReason) => void;
  onRegenerate: (ideaId: string) => void;
}

export function IdeaCard({ idea, index, onFeedback, onRegenerate }: IdeaCardProps) {
  const [showReasonDropdown, setShowReasonDropdown] = useState(false);
  const [copySuccess, setCopySuccess] = useState(false);

  const handleThumbsUp = () => {
    onFeedback(idea.id, 'up');
    setShowReasonDropdown(false);
  };

  const handleThumbsDown = () => {
    if (idea.feedback?.rating === 'down') {
      setShowReasonDropdown(!showReasonDropdown);
    } else {
      onFeedback(idea.id, 'down');
      setShowReasonDropdown(true);
    }
  };

  const handleReasonSelect = (reason: FeedbackReason) => {
    onFeedback(idea.id, 'down', reason);
    setShowReasonDropdown(false);
  };

  const handleCopy = async () => {
    const text = formatIdeaForCopy(idea);
    const success = await copyToClipboard(text);
    if (success) {
      setCopySuccess(true);
      setTimeout(() => setCopySuccess(false), 2000);
    }
  };

  const getMatchColor = (): string => {
    if (!idea.skillMatch) return 'yellow';
    const { percentage } = idea.skillMatch;
    if (percentage >= 60) return 'green';
    if (percentage >= 30) return 'yellow';
    return 'red';
  };

  const reasonLabels: Record<FeedbackReason, string> = {
    wrong_tech_stack: 'Wrong tech stack for me',
    too_expensive: 'Too expensive',
    too_difficult: 'Too difficult',
    not_interesting: 'Not interesting',
    other: 'Other',
  };

  return (
    <div className="idea-card">
      <div className="idea-header">
        <h3>#{index + 1} {idea.title}</h3>
        <div className="idea-actions">
          <button
            className={`thumb-btn ${idea.feedback?.rating === 'up' ? 'active' : ''}`}
            onClick={handleThumbsUp}
            title="Good suggestion"
          >
            👍
          </button>
          <button
            className={`thumb-btn ${idea.feedback?.rating === 'down' ? 'active' : ''}`}
            onClick={handleThumbsDown}
            title="Bad suggestion"
          >
            👎
          </button>
          <button
            className="action-btn"
            onClick={handleCopy}
            title={copySuccess ? 'Copied!' : 'Copy idea'}
          >
            {copySuccess ? '✓' : '📋'}
          </button>
          <button
            className="action-btn"
            onClick={() => onRegenerate(idea.id)}
            title="Regenerate this idea"
          >
            🔄
          </button>
        </div>
      </div>

      {showReasonDropdown && (
        <div className="feedback-dropdown">
          <p>Why is this bad?</p>
          {(Object.keys(reasonLabels) as FeedbackReason[]).map((reason) => (
            <button
              key={reason}
              className="reason-btn"
              onClick={() => handleReasonSelect(reason)}
            >
              {reasonLabels[reason]}
            </button>
          ))}
        </div>
      )}

      {idea.skillMatch && (
        <div className="skill-match">
          <div className="skill-match-label">
            Matches {idea.skillMatch.matchedCount}/{idea.skillMatch.totalCount} of your skills
          </div>
          <div className="skill-match-bar">
            <div
              className={`skill-match-fill ${getMatchColor()}`}
              style={{ width: `${idea.skillMatch.percentage}%` }}
            />
          </div>
        </div>
      )}

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
