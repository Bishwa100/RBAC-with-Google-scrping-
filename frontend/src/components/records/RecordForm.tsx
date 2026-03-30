import React from 'react'
import clsx from 'clsx'
import { Calendar, Clock, MapPin, Phone } from 'lucide-react'

export interface RecordPayload {
  full_name: string
  email: string
  phone_number: string
  date: string
  time: string
  location: string
  notes: string
  [key: string]: any
}

interface RecordFormProps {
  data: RecordPayload
  onChange: (data: RecordPayload) => void
  errors?: Record<string, string>
}

const RecordForm: React.FC<RecordFormProps> = ({ data, onChange, errors = {} }) => {
  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    onChange({ ...data, [name]: value })
  }

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-1">
          <label className="text-[10px] font-mono text-dim uppercase">Full Name</label>
          <input
            type="text"
            name="full_name"
            value={data.full_name || ''}
            onChange={handleChange}
            placeholder="John Doe"
            className={clsx(
              "w-full bg-bg-base border rounded px-4 py-2 font-mono text-sm focus:outline-none transition-all",
              errors.full_name ? "border-danger" : "border-border focus:border-accent"
            )}
          />
          {errors.full_name && <p className="text-[10px] text-danger font-mono uppercase mt-1">{errors.full_name}</p>}
        </div>

        <div className="space-y-1">
          <label className="text-[10px] font-mono text-dim uppercase">Email Address</label>
          <input
            type="email"
            name="email"
            value={data.email || ''}
            onChange={handleChange}
            placeholder="john@example.com"
            className={clsx(
              "w-full bg-bg-base border rounded px-4 py-2 font-mono text-sm focus:outline-none transition-all",
              errors.email ? "border-danger" : "border-border focus:border-accent"
            )}
          />
          {errors.email && <p className="text-[10px] text-danger font-mono uppercase mt-1">{errors.email}</p>}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-1">
          <label className="text-[10px] font-mono text-dim uppercase">Phone Number</label>
          <div className="relative">
            <Phone size={14} className="absolute left-3 top-3 text-dim" />
            <input
              type="tel"
              name="phone_number"
              value={data.phone_number || ''}
              onChange={handleChange}
              placeholder="+91 9876543210"
              className="w-full bg-bg-base border border-border focus:border-accent rounded pl-10 pr-4 py-2 font-mono text-sm focus:outline-none transition-all"
            />
          </div>
        </div>

        <div className="space-y-1">
          <label className="text-[10px] font-mono text-dim uppercase">Location</label>
          <div className="relative">
            <MapPin size={14} className="absolute left-3 top-3 text-dim" />
            <input
              type="text"
              name="location"
              value={data.location || ''}
              onChange={handleChange}
              placeholder="Mumbai, HQ"
              className="w-full bg-bg-base border border-border focus:border-accent rounded pl-10 pr-4 py-2 font-mono text-sm focus:outline-none transition-all"
            />
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-1">
          <label className="text-[10px] font-mono text-dim uppercase">Effective Date</label>
          <div className="relative">
            <Calendar size={14} className="absolute left-3 top-3 text-dim" />
            <input
              type="date"
              name="date"
              value={data.date || ''}
              onChange={handleChange}
              className="w-full bg-bg-base border border-border focus:border-accent rounded pl-10 pr-4 py-2 font-mono text-sm focus:outline-none transition-all"
            />
          </div>
        </div>

        <div className="space-y-1">
          <label className="text-[10px] font-mono text-dim uppercase">Timestamp</label>
          <div className="relative">
            <Clock size={14} className="absolute left-3 top-3 text-dim" />
            <input
              type="time"
              name="time"
              value={data.time || ''}
              onChange={handleChange}
              className="w-full bg-bg-base border border-border focus:border-accent rounded pl-10 pr-4 py-2 font-mono text-sm focus:outline-none transition-all"
            />
          </div>
        </div>
      </div>

      <div className="space-y-1">
        <label className="text-[10px] font-mono text-dim uppercase">Detailed Notes</label>
        <textarea
          name="notes"
          value={data.notes || ''}
          onChange={handleChange}
          placeholder="Enter additional information or context..."
          className="w-full h-24 bg-bg-base border border-border focus:border-accent rounded px-4 py-2 font-mono text-sm focus:outline-none transition-all resize-none"
        />
      </div>
    </div>
  )
}

export default RecordForm
