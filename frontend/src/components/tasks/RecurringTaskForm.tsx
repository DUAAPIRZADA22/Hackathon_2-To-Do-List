/**
 * RecurringTaskForm Component - UI for recurring task configuration (T096)
 *
 * Allows users to configure:
 * - Recurrence frequency (daily, weekly, monthly) (T097)
 * - Weekly day selection (T098)
 * - End date picker (T099)
 */

'use client';

import { useState } from 'react';
import { RecurrenceRule } from '@/types';

interface RecurringTaskFormProps {
  value?: RecurrenceRule;
  onChange: (rule: RecurrenceRule | undefined) => void;
  disabled?: boolean;
}

const DAYS_OF_WEEK = [
  'monday', 'tuesday', 'wednesday', 'thursday',
  'friday', 'saturday', 'sunday'
];

export function RecurringTaskForm({ value, onChange, disabled }: RecurringTaskFormProps) {
  const [frequency, setFrequency] = useState<RecurrenceRule['frequency']>(value?.frequency || 'weekly');
  const [interval, setInterval] = useState(value?.interval || 1);
  const [days, setDays] = useState<string[]>(value?.days || ['monday']);
  const [monthDay, setMonthDay] = useState(value?.month_day || 1);
  const [endDate, setEndDate] = useState(value?.end_date || '');

  const updateRule = () => {
    if (!frequency) {
      onChange(undefined);
      return;
    }

    const rule: RecurrenceRule = {
      frequency,
      interval,
    };

    if (frequency === 'weekly' && days.length > 0) {
      rule.days = days;
    }

    if (frequency === 'monthly') {
      rule.month_day = monthDay;
    }

    if (endDate) {
      rule.end_date = endDate;
    }

    onChange(rule);
  };

  const toggleDay = (day: string) => {
    setDays(prev =>
      prev.includes(day)
        ? prev.filter(d => d !== day)
        : [...prev, day]
    );
  };

  return (
    <div className="space-y-4 p-4 border rounded-lg bg-gray-50">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium">Recurring Task</h3>
        <button
          type="button"
          onClick={() => onChange(undefined)}
          className="text-xs text-red-600 hover:text-red-700"
          disabled={disabled}
        >
          Remove recurrence
        </button>
      </div>

      {/* Frequency selector (T097) */}
      <div>
        <label className="block text-sm font-medium mb-1">Frequency</label>
        <select
          value={frequency}
          onChange={(e) => {
            setFrequency(e.target.value as RecurrenceRule['frequency']);
            setTimeout(updateRule, 0);
          }}
          disabled={disabled}
          className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="daily">Daily</option>
          <option value="weekly">Weekly</option>
          <option value="monthly">Monthly</option>
        </select>
      </div>

      {/* Interval */}
      <div>
        <label className="block text-sm font-medium mb-1">
          Every {frequency === 'daily' ? 'day(s)' : frequency === 'weekly' ? 'week(s)' : 'month(s)'}
        </label>
        <input
          type="number"
          min="1"
          max="365"
          value={interval}
          onChange={(e) => {
            setInterval(parseInt(e.target.value) || 1);
            setTimeout(updateRule, 0);
          }}
          disabled={disabled}
          className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      {/* Weekly day selector (T098) */}
      {frequency === 'weekly' && (
        <div>
          <label className="block text-sm font-medium mb-2">Repeat on</label>
          <div className="flex flex-wrap gap-2">
            {DAYS_OF_WEEK.map((day) => (
              <button
                key={day}
                type="button"
                onClick={() => {
                  toggleDay(day);
                  setTimeout(updateRule, 0);
                }}
                disabled={disabled}
                className={`
                  px-3 py-1 text-sm rounded-full border transition-colors
                  ${days.includes(day)
                    ? 'bg-blue-500 text-white border-blue-500'
                    : 'bg-white text-gray-700 border-gray-300 hover:border-blue-300'
                  }
                  ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
                `}
              >
                {day.slice(0, 3).toUpperCase()}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Monthly day selector */}
      {frequency === 'monthly' && (
        <div>
          <label className="block text-sm font-medium mb-1">Day of month</label>
          <input
            type="number"
            min="1"
            max="31"
            value={monthDay}
            onChange={(e) => {
              setMonthDay(parseInt(e.target.value) || 1);
              setTimeout(updateRule, 0);
            }}
            disabled={disabled}
            className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      )}

      {/* End date picker (T099) */}
      <div>
        <label className="block text-sm font-medium mb-1">
          End date (optional)
        </label>
        <input
          type="date"
          value={endDate}
          onChange={(e) => {
            setEndDate(e.target.value);
            setTimeout(updateRule, 0);
          }}
          disabled={disabled}
          min={new Date().toISOString().split('T')[0]}
          className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <p className="text-xs text-gray-500 mt-1">
          Leave empty for indefinite recurrence
        </p>
      </div>

      {/* Preview */}
      {value && (
        <div className="p-3 bg-blue-50 border border-blue-200 rounded-md">
          <p className="text-sm text-blue-800">
            <strong>Recurrence:</strong> Every {interval} {frequency}
            {frequency === 'weekly' && ` on ${days.map(d => d.slice(0, 3)).join(', ')}`}
            {frequency === 'monthly' && ` on day ${monthDay}`}
            {endDate && ` until ${new Date(endDate).toLocaleDateString()}`}
          </p>
        </div>
      )}
    </div>
  );
}

export default RecurringTaskForm;
