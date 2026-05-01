/**
 * InteractionForm Component
 * Structured form for logging HCP interactions
 * Supports both manual entry and AI-populated data
 */

import React, { useState, useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { createInteraction, updateInteraction, fetchInteractions } from '../redux/interactionSlice'

const InteractionForm = ({ selectedInteraction, onSuccess }) => {
  const dispatch = useDispatch()
  const { loading, error } = useSelector((state) => state.interactions)
  
  // Form state
  const [formData, setFormData] = useState({
    hcp_name: '',
    interaction_type: '',
    discussion_notes: '',
    sentiment: '',
    summary: '',
    follow_up: '',
    attendees: '',
    topics_discussed: '',
    materials_shared: '',
    samples_distributed: '',
    outcomes: ''
  })

  // Reset form when selectedInteraction changes
  useEffect(() => {
    if (selectedInteraction) {
      setFormData({
        hcp_name: selectedInteraction.hcp_name || '',
        interaction_type: selectedInteraction.interaction_type || '',
        discussion_notes: selectedInteraction.discussion_notes || selectedInteraction.summary || '',
        sentiment: selectedInteraction.sentiment || '',
        summary: selectedInteraction.summary || '',
        follow_up: selectedInteraction.follow_up || '',
        attendees: selectedInteraction.attendees || '',
        topics_discussed: selectedInteraction.topics_discussed || '',
        materials_shared: selectedInteraction.materials_shared || '',
        samples_distributed: selectedInteraction.samples_distributed || '',
        outcomes: selectedInteraction.outcomes || ''
      })
    } else {
      resetForm()
    }
  }, [selectedInteraction])

  const resetForm = () => {
    setFormData({
      hcp_name: '',
      interaction_type: '',
      discussion_notes: '',
      sentiment: '',
      summary: '',
      follow_up: '',
      attendees: '',
      topics_discussed: '',
      materials_shared: '',
      samples_distributed: '',
      outcomes: ''
    })
  }

  // Handle input changes
  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: value
    }))
  }

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault()
    
    // Prepare data for API
    const interactionData = {
      hcp_name: formData.hcp_name,
      interaction_type: formData.interaction_type,
      discussion_notes: formData.discussion_notes,
      sentiment: formData.sentiment,
      summary: formData.summary || formData.discussion_notes,
      follow_up: formData.follow_up,
      attendees: formData.attendees,
      topics_discussed: formData.topics_discussed,
      materials_shared: formData.materials_shared,
      samples_distributed: formData.samples_distributed,
      outcomes: formData.outcomes
    }

    try {
      if (selectedInteraction?.id) {
        // Update existing interaction
        await dispatch(updateInteraction({ 
          id: selectedInteraction.id, 
          data: interactionData 
        })).unwrap()
        onSuccess('Interaction updated successfully!')
      } else {
        // Create new interaction
        await dispatch(createInteraction(interactionData)).unwrap()
        onSuccess('Interaction logged successfully!')
      }
      resetForm()
      dispatch(fetchInteractions())
    } catch (err) {
      console.error('Error saving interaction:', err)
    }
  }

  // Handle cancel/reset
  const handleCancel = () => {
    resetForm()
    if (selectedInteraction) {
      onSuccess('')
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {/* HCP Name */}
      <div>
        <label htmlFor="hcp_name" className="block text-sm font-medium text-gray-700 mb-1">
          HCP Name <span className="text-red-500">*</span>
        </label>
        <input
          type="text"
          id="hcp_name"
          name="hcp_name"
          value={formData.hcp_name}
          onChange={handleChange}
          required
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
          placeholder="Dr. John Smith"
        />
      </div>

      {/* Interaction Type */}
      <div>
        <label htmlFor="interaction_type" className="block text-sm font-medium text-gray-700 mb-1">
          Interaction Type <span className="text-red-500">*</span>
        </label>
        <select
          id="interaction_type"
          name="interaction_type"
          value={formData.interaction_type}
          onChange={handleChange}
          required
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
        >
          <option value="">Select interaction type</option>
          <option value="In-Person Visit">In-Person Visit</option>
          <option value="Virtual Meeting">Virtual Meeting</option>
          <option value="Phone Call">Phone Call</option>
          <option value="Email">Email</option>
          <option value="Conference">Conference</option>
          <option value="Product Demo">Product Demo</option>
        </select>
      </div>

      {/* Two Column Layout */}
      <div className="grid grid-cols-2 gap-4">
        {/* Attendees */}
        <div>
          <label htmlFor="attendees" className="block text-sm font-medium text-gray-700 mb-1">
            Attendees
          </label>
          <input
            type="text"
            id="attendees"
            name="attendees"
            value={formData.attendees}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
            placeholder="Dr. Smith, Nurse Jane"
          />
        </div>

        {/* Sentiment */}
        <div>
          <label htmlFor="sentiment" className="block text-sm font-medium text-gray-700 mb-1">
            Sentiment <span className="text-red-500">*</span>
          </label>
          <select
            id="sentiment"
            name="sentiment"
            value={formData.sentiment}
            onChange={handleChange}
            required
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
          >
            <option value="">Select sentiment</option>
            <option value="positive">Positive</option>
            <option value="neutral">Neutral</option>
            <option value="negative">Negative</option>
          </select>
        </div>
      </div>

      {/* Topics Discussed */}
      <div>
        <label htmlFor="topics_discussed" className="block text-sm font-medium text-gray-700 mb-1">
          Topics Discussed
        </label>
        <input
          type="text"
          id="topics_discussed"
          name="topics_discussed"
          value={formData.topics_discussed}
          onChange={handleChange}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
          placeholder="New drug efficacy, Treatment protocols"
        />
      </div>

      {/* Materials Shared */}
      <div>
        <label htmlFor="materials_shared" className="block text-sm font-medium text-gray-700 mb-1">
          Materials Shared
        </label>
        <input
          type="text"
          id="materials_shared"
          name="materials_shared"
          value={formData.materials_shared}
          onChange={handleChange}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
          placeholder="Brochures, Sample packs, Clinical data"
        />
      </div>

      {/* Samples Distributed */}
      <div>
        <label htmlFor="samples_distributed" className="block text-sm font-medium text-gray-700 mb-1">
          Samples Distributed
        </label>
        <input
          type="text"
          id="samples_distributed"
          name="samples_distributed"
          value={formData.samples_distributed}
          onChange={handleChange}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
          placeholder="Product samples, Trial packs"
        />
      </div>

      {/* Discussion Notes */}
      <div>
        <label htmlFor="discussion_notes" className="block text-sm font-medium text-gray-700 mb-1">
          Discussion Notes
        </label>
        <textarea
          id="discussion_notes"
          name="discussion_notes"
          value={formData.discussion_notes}
          onChange={handleChange}
          rows={4}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors resize-none"
          placeholder="Describe the key points of your interaction..."
        />
      </div>

      {/* Outcomes */}
      <div>
        <label htmlFor="outcomes" className="block text-sm font-medium text-gray-700 mb-1">
          Outcomes
        </label>
        <input
          type="text"
          id="outcomes"
          name="outcomes"
          value={formData.outcomes}
          onChange={handleChange}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
          placeholder="Prescription written, Next meeting scheduled"
        />
      </div>

      {/* Follow-up Actions */}
      <div>
        <label htmlFor="follow_up" className="block text-sm font-medium text-gray-700 mb-1">
          Follow-up Actions
        </label>
        <textarea
          id="follow_up"
          name="follow_up"
          value={formData.follow_up}
          onChange={handleChange}
          rows={3}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors resize-none"
          placeholder="Actions to take after this interaction..."
        />
      </div>

      {/* Form Actions */}
      <div className="flex space-x-3 pt-4">
        <button
          type="submit"
          disabled={loading}
          className="flex-1 bg-blue-600 text-white py-2.5 px-4 rounded-lg hover:bg-blue-700 focus:ring-4 focus:ring-blue-200 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
        >
          {loading ? (
            <span className="flex items-center justify-center">
              <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Saving...
            </span>
          ) : selectedInteraction?.id ? (
            'Update Interaction'
          ) : (
            'Log Interaction'
          )}
        </button>
        {selectedInteraction?.id && (
          <button
            type="button"
            onClick={handleCancel}
            className="px-4 py-2.5 border border-gray-300 rounded-lg hover:bg-gray-50 focus:ring-4 focus:ring-gray-200 transition-colors font-medium text-gray-700"
          >
            Cancel
          </button>
        )}
      </div>

      {/* Error Display */}
      {error && (
        <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm text-red-600">{error}</p>
        </div>
      )}
    </form>
  )
}

export default InteractionForm