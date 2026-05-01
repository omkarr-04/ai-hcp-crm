/**
 * Dashboard page - Main CRM interface
 * Split layout with interaction form (left) and AI chat (right)
 */

import React, { useState, useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import InteractionForm from '../components/InteractionForm'
import AIChat from '../components/AIChat'
import { fetchInteractions } from '../redux/interactionSlice'

const Dashboard = () => {
  const dispatch = useDispatch()
  const { interactions, loading, error } = useSelector((state) => state.interactions)
  const [selectedInteraction, setSelectedInteraction] = useState(null)
  const [showToast, setShowToast] = useState(false)
  const [toastMessage, setToastMessage] = useState('')

  const normalizeSentiment = (sentiment) => (sentiment || '').toLowerCase()

  useEffect(() => {
    // Fetch interactions on component mount
    dispatch(fetchInteractions())
  }, [dispatch])

  // Handle interaction selection for editing
  const handleEditInteraction = (interaction) => {
    setSelectedInteraction(interaction)
  }

  // Handle successful form submission
  const handleFormSuccess = (message) => {
    setToastMessage(message)
    setShowToast(true)
    setSelectedInteraction(null)
    setTimeout(() => {
      setShowToast(false)
    }, 3000)
  }

  // Handle AI chat data to populate form
  const handleAIFormData = (formData) => {
    setSelectedInteraction(formData)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <div>
                <h1 className="text-xl font-semibold text-gray-900">AI-HCP CRM</h1>
                <p className="text-sm text-gray-500">Healthcare Professional Interaction Logging</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-500">
                {interactions.length} Interactions
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content - Split Layout */}
      <main className="max-w-7xl mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left Panel - Interaction Form */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">Log Interaction</h2>
              <p className="text-sm text-gray-500">Record details of your HCP visit</p>
            </div>
            <div className="p-6">
              <InteractionForm 
                selectedInteraction={selectedInteraction}
                onSuccess={handleFormSuccess}
              />
            </div>
          </div>

          {/* Right Panel - AI Chat */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200">
            <div className="px-6 py-4 border-b border-gray-200">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                  <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                </div>
                <div>
                  <h2 className="text-lg font-semibold text-gray-900">AI Assistant</h2>
                  <p className="text-sm text-gray-500">Natural language interaction logging</p>
                </div>
              </div>
            </div>
            <div className="p-6">
              <AIChat onFormData={handleAIFormData} />
            </div>
          </div>
        </div>

        {/* Recent Interactions List */}
        <div className="mt-6 bg-white rounded-xl shadow-sm border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">Recent Interactions</h2>
          </div>
          <div className="p-6">
            {loading ? (
              <div className="flex items-center justify-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              </div>
            ) : error ? (
              <div className="text-center py-8 text-red-500">{error}</div>
            ) : interactions.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                No interactions yet. Start by logging an interaction or using the AI assistant.
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-gray-200">
                      <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">HCP Name</th>
                      <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Type</th>
                      <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Date</th>
                      <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Sentiment</th>
                      <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Summary</th>
                      <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {interactions.slice(0, 5).map((interaction) => (
                      <tr key={interaction.id} className="border-b border-gray-100 hover:bg-gray-50">
                        <td className="py-3 px-4 text-sm text-gray-900">{interaction.hcp_name}</td>
                        <td className="py-3 px-4 text-sm text-gray-600">{interaction.interaction_type}</td>
                        <td className="py-3 px-4 text-sm text-gray-600">
                          {new Date(interaction.created_at).toLocaleDateString()}
                        </td>
                        <td className="py-3 px-4">
                          {(() => {
                            const normalizedSentiment = normalizeSentiment(interaction.sentiment)
                            return (
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
                            ${normalizedSentiment === 'positive' ? 'bg-green-100 text-green-800' :
                              normalizedSentiment === 'negative' ? 'bg-red-100 text-red-800' :
                              'bg-gray-100 text-gray-800'}`}>
                            {interaction.sentiment}
                          </span>
                            )
                          })()}
                        </td>
                        <td className="py-3 px-4 text-sm text-gray-600 max-w-xs truncate">
                          {interaction.summary}
                        </td>
                        <td className="py-3 px-4">
                          <button
                            onClick={() => handleEditInteraction(interaction)}
                            className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                          >
                            Edit
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Toast Notification */}
      {showToast && (
        <div className="fixed bottom-4 right-4 bg-green-600 text-white px-6 py-3 rounded-lg shadow-lg flex items-center space-x-2">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
          <span>{toastMessage}</span>
        </div>
      )}
    </div>
  )
}

export default Dashboard