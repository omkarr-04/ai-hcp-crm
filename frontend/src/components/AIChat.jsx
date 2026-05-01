/**
 * AIChat Component
 * Conversational interface for logging interactions using AI
 * Uses LangGraph + Groq LLM to convert natural language to structured data
 */

import React, { useState, useRef, useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { sendChatMessage, clearChat } from '../redux/chatSlice'

const AIChat = ({ onFormData }) => {
  const dispatch = useDispatch()
  const { messages, loading, error } = useSelector((state) => state.chat)
  const [inputMessage, setInputMessage] = useState('')
  const messagesEndRef = useRef(null)

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Handle input change
  const handleInputChange = (e) => {
    setInputMessage(e.target.value)
  }

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!inputMessage.trim() || loading) return

    const userMessage = inputMessage.trim()
    setInputMessage('')

    try {
      // Send message to AI
      const result = await dispatch(sendChatMessage(userMessage)).unwrap()
      
      // If AI returns structured data, populate the form
      if (result.extracted_data) {
        onFormData(result.extracted_data)
      }
    } catch (err) {
      console.error('Chat error:', err)
    }
  }

  // Handle key press (Enter to send)
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  // Handle "Use Data" button click
  const handleUseData = (formData) => {
    onFormData(formData)
  }

  // Handle clear chat
  const handleClearChat = () => {
    dispatch(clearChat())
  }

  return (
    <div className="flex flex-col h-[500px]">
      {/* Chat Messages Area */}
      <div className="flex-1 overflow-y-auto space-y-4 mb-4 pr-2">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center mb-4">
              <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">AI Assistant Ready</h3>
            <p className="text-sm text-gray-500 max-w-xs">
              Describe your HCP interaction in natural language. I'll extract the details and populate the form for you.
            </p>
            <div className="mt-6 text-left w-full max-w-xs">
              <p className="text-xs font-medium text-gray-700 mb-2">Example prompts:</p>
              <ul className="text-xs text-gray-500 space-y-1">
                <li>• "Visited Dr. Sarah Johnson today to discuss our new diabetes drug"</li>
                <li>• "Had a productive call with Dr. Michael Chen about clinical trial results"</li>
                <li>• "Met with Dr. Emily Williams at the hospital, discussed new treatment protocols"</li>
              </ul>
            </div>
          </div>
        ) : (
          messages.map((message, index) => (
            <div
              key={index}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[85%] rounded-2xl px-4 py-3 ${
                  message.role === 'user'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-900'
                }`}
              >
                {/* Message Content */}
                <div className="text-sm whitespace-pre-wrap">{message.content}</div>
                
                {/* AI Response - Form Data Option */}
                {message.role === 'assistant' && message.form_data && (
                  <div className="mt-4 pt-3 border-t border-gray-200">
                    <p className="text-xs font-medium text-gray-600 mb-2">
                      Extracted Data:
                    </p>
                    <div className="space-y-1 text-xs">
                      <p><span className="font-medium">HCP:</span> {message.form_data.hcp_name}</p>
                      <p><span className="font-medium">Type:</span> {message.form_data.interaction_type}</p>
                      <p><span className="font-medium">Sentiment:</span> {message.form_data.sentiment}</p>
                    </div>
                    <button
                      onClick={() => handleUseData(message.form_data)}
                      className="mt-3 w-full bg-green-600 text-white py-2 px-3 rounded-lg text-sm font-medium hover:bg-green-700 transition-colors"
                    >
                      Use This Data
                    </button>
                  </div>
                )}
              </div>
            </div>
          ))
        )}

        {/* Loading Indicator */}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 rounded-2xl px-4 py-3">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <form onSubmit={handleSubmit} className="border-t border-gray-200 pt-4">
        <div className="flex space-x-2">
          <input
            type="text"
            value={inputMessage}
            onChange={handleInputChange}
            onKeyPress={handleKeyPress}
            placeholder="Describe your HCP interaction..."
            disabled={loading}
            className="flex-1 px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={loading || !inputMessage.trim()}
            className="px-4 py-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 focus:ring-4 focus:ring-blue-200 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
          </button>
        </div>
        {messages.length > 0 && (
          <div className="mt-2 flex justify-end">
            <button
              type="button"
              onClick={handleClearChat}
              className="text-xs text-gray-500 hover:text-gray-700 transition-colors"
            >
              Clear Chat
            </button>
          </div>
        )}
      </form>

      {/* Error Display */}
      {error && (
        <div className="mt-2 p-2 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-xs text-red-600">{error}</p>
        </div>
      )}
    </div>
  )
}

export default AIChat