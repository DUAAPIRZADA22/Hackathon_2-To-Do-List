/**
 * ReminderSettings Component - UI for reminder configuration (T102)
 *
 * Allows users to configure:
 * - Reminder times (e.g., 1h, 1d, 1w before due) (T103)
 * - Enable/disable toggle (T104)
 */

'use client';

import { useState } from 'react';
import { ReminderSettings } from '@/types';

interface ReminderSettingsFormProps {
  value?: ReminderSettings;
  onChange: (settings: ReminderSettings | undefined) => void;
  disabled?: boolean;
}

const PRESET_TIMES = [
  { label: '15 minutes before', value: '15m' },
  { label: '1 hour before', value: '1h' },
  { label: '1 day before', value: '1d' },
  { label: '1 week before', value: '1w' },
];

export function ReminderSettingsForm({ value, onChange, disabled }: ReminderSettingsFormProps) {
  const [enabled, setEnabled] = useState(value?.enabled ?? true);
  const [reminderTimes, setReminderTimes] = useState<string[]>(value?.reminder_times || []);

  const updateSettings = () => {
    if (!enabled || reminderTimes.length === 0) {
      onChange(undefined);
      return;
    }

    const settings: ReminderSettings = {
      enabled,
      reminder_times: reminderTimes,
      notification_method: 'email', // Only email supported initially
    };

    onChange(settings);
  };

  const toggleTime = (time: string) => {
    setReminderTimes(prev =>
      prev.includes(time)
        ? prev.filter(t => t !== time)
        : [...prev, time]
    );
    setTimeout(updateRule, 0);
  };

  const updateRule = () => {
    if (!enabled || reminderTimes.length === 0) {
      onChange(undefined);
      return;
    }

    const settings: ReminderSettings = {
      enabled,
      reminder_times: reminderTimes,
      notification_method: 'email',
    };

    onChange(settings);
  };

  return (
    <div className="space-y-4 p-4 border rounded-lg bg-gray-50">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium">Reminders</h3>

        {/* Enable/disable toggle (T104) */}
        <button
          type="button"
          onClick={() => {
            setEnabled(!enabled);
            setTimeout(updateRule, 0);
          }}
          disabled={disabled}
          className={`
            relative inline-flex h-6 w-11 items-center rounded-full transition-colors
            ${enabled ? 'bg-blue-500' : 'bg-gray-300'}
            ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
          `}
        >
          <span
            className={`
              inline-block h-4 w-4 transform rounded-full bg-white transition-transform
              ${enabled ? 'translate-x-6' : 'translate-x-1'}
            `}
          />
        </button>
      </div>

      {enabled && (
        <>
          {/* Reminder time selector (T103) */}
          <div>
            <label className="block text-sm font-medium mb-2">
              Remind me before due date:
            </label>
            <div className="space-y-2">
              {PRESET_TIMES.map((preset) => (
                <label
                  key={preset.value}
                  className={`
                    flex items-center p-3 border rounded-md cursor-pointer transition-colors
                    ${reminderTimes.includes(preset.value)
                      ? 'bg-blue-50 border-blue-500'
                      : 'bg-white border-gray-300 hover:border-blue-300'
                    }
                    ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
                  `}
                >
                  <input
                    type="checkbox"
                    checked={reminderTimes.includes(preset.value)}
                    onChange={() => {
                      toggleTime(preset.value);
                    }}
                    disabled={disabled}
                    className="mr-3"
                  />
                  <span className="text-sm">{preset.label}</span>
                </label>
              ))}
            </div>
          </div>

          {/* Custom reminder time input */}
          <div>
            <label className="block text-sm font-medium mb-1">
              Custom reminder (optional)
            </label>
            <div className="flex gap-2">
              <input
                type="number"
                min="1"
                max="52"
                placeholder="1"
                className="flex-1 px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                disabled={disabled}
              />
              <select
                className="px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                disabled={disabled}
              >
                <option value="m">Minutes</option>
                <option value="h">Hours</option>
                <option value="d">Days</option>
                <option value="w">Weeks</option>
              </select>
              <button
                type="button"
                className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 disabled:opacity-50"
                disabled={disabled}
              >
                Add
              </button>
            </div>
            <p className="text-xs text-gray-500 mt-1">
              Maximum 5 reminders per task
            </p>
          </div>

          {/* Preview */}
          {reminderTimes.length > 0 && (
            <div className="p-3 bg-green-50 border border-green-200 rounded-md">
              <p className="text-sm text-green-800">
                <strong>Reminders set:</strong>{' '}
                {reminderTimes.join(', ')}
              </p>
            </div>
          )}
        </>
      )}

      {!enabled && (
        <p className="text-sm text-gray-500 italic">
          Reminders are disabled. Enable to set notification times.
        </p>
      )}
    </div>
  );
}

export default ReminderSettingsForm;
