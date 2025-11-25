import { useForm, Controller } from 'react-hook-form';
import { UserProfile } from '../types';
import { TagInput } from './TagInput';

interface ProfileFormProps {
  onSubmit: (profile: UserProfile) => void;
  isLoading: boolean;
}

export function ProfileForm({ onSubmit, isLoading }: ProfileFormProps) {
  const { register, handleSubmit, control } = useForm<UserProfile>({
    defaultValues: {
      technical_skills: [],
      non_technical_skills: [],
      experience_level: 'beginner',
      preferred_niches: [],
      preferred_types: [],
    },
  });

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <div className="form-section">
        <h2>Your Skills</h2>

        <div className="form-group">
          <label>Technical Skills (press Enter to add)</label>
          <Controller
            name="technical_skills"
            control={control}
            render={({ field }) => (
              <TagInput
                value={field.value}
                onChange={field.onChange}
                placeholder="python, react, aws, sql..."
              />
            )}
          />
        </div>

        <div className="form-group">
          <label>Other Skills</label>
          <Controller
            name="non_technical_skills"
            control={control}
            render={({ field }) => (
              <TagInput
                value={field.value}
                onChange={field.onChange}
                placeholder="marketing, sales, writing..."
              />
            )}
          />
        </div>

        <div className="form-group">
          <label>Experience Level</label>
          <select {...register('experience_level')}>
            <option value="beginner">Beginner - Just starting out</option>
            <option value="intermediate">Intermediate - Built some projects</option>
            <option value="experienced">Experienced - Shipped products before</option>
          </select>
        </div>
      </div>

      <div className="form-section">
        <h2>Preferences</h2>

        <div className="form-group">
          <label>Niches you're interested in</label>
          <Controller
            name="preferred_niches"
            control={control}
            render={({ field }) => (
              <TagInput
                value={field.value}
                onChange={field.onChange}
                placeholder="fintech, health, education, ecommerce..."
              />
            )}
          />
        </div>

        <div className="form-group">
          <label>Project types you prefer</label>
          <Controller
            name="preferred_types"
            control={control}
            render={({ field }) => (
              <TagInput
                value={field.value}
                onChange={field.onChange}
                placeholder="saas, service, content, marketplace..."
              />
            )}
          />
        </div>
      </div>

      <div className="form-section">
        <h2>Constraints & Goals</h2>

        <div className="row">
          <div className="form-group">
            <label>Hours per week available</label>
            <input
              type="number"
              {...register('hours_per_week', { valueAsNumber: true })}
              placeholder="10"
            />
          </div>

          <div className="form-group">
            <label>Budget</label>
            <select {...register('budget')}>
              <option value="">Not specified</option>
              <option value="free">$0 - Free only</option>
              <option value="<$100">Under $100</option>
              <option value="<$1000">Under $1,000</option>
              <option value=">$1000">$1,000+</option>
            </select>
          </div>
        </div>

        <div className="row">
          <div className="form-group">
            <label>Income Goal</label>
            <select {...register('income_goal')}>
              <option value="">Not specified</option>
              <option value="side_income">Side income ($500-2k/mo)</option>
              <option value="replace_job">Replace job ($5k+/mo)</option>
              <option value="scale_big">Build something big</option>
            </select>
          </div>

          <div className="form-group">
            <label>Timeline</label>
            <select {...register('timeline')}>
              <option value="">Flexible</option>
              <option value="asap">ASAP - Start earning quick</option>
              <option value="3_months">3 months</option>
              <option value="6_months">6 months</option>
              <option value="1_year">1 year+</option>
            </select>
          </div>
        </div>
      </div>

      <div className="form-section">
        <h2>More About You (Optional)</h2>

        <div className="form-group">
          <label>Interests & Passions</label>
          <textarea
            {...register('interests')}
            rows={2}
            placeholder="What do you genuinely enjoy? Gaming, fitness, investing, cooking..."
          />
        </div>

        <div className="form-group">
          <label>Background</label>
          <textarea
            {...register('background')}
            rows={2}
            placeholder="Current job, past projects, unique experiences..."
          />
        </div>
      </div>

      <button type="submit" disabled={isLoading}>
        {isLoading ? 'Generating Ideas...' : 'Generate Project Ideas'}
      </button>
    </form>
  );
}
