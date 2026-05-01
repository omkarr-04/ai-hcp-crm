/**
 * Chat Redux Slice
 * Manages state for AI chat functionality
 */

import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import api from '../services/api'

// Async thunk for sending chat messages
export const sendChatMessage = createAsyncThunk(
  'chat/sendChatMessage',
  async (message, { rejectWithValue }) => {
    try {
      const response = await api.post('/api/ai/chat', { message })
      return { ...response.data, userMessage: message }
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to send message')
    }
  }
)

// Initial state
const initialState = {
  messages: [],
  loading: false,
  error: null
}

// Slice
const chatSlice = createSlice({
  name: 'chat',
  initialState,
  reducers: {
    // Add user message to chat
    addUserMessage: (state, action) => {
      state.messages.push({
        role: 'user',
        content: action.payload,
        timestamp: new Date().toISOString()
      })
    },
    // Add AI response to chat
    addAssistantMessage: (state, action) => {
      state.messages.push({
        role: 'assistant',
        content: action.payload.content,
        form_data: action.payload.form_data,
        timestamp: new Date().toISOString()
      })
    },
    // Clear chat history
    clearChat: (state) => {
      state.messages = []
      state.error = null
    },
    // Clear error
    clearError: (state) => {
      state.error = null
    }
  },
  extraReducers: (builder) => {
    builder
      // Send Chat Message
      .addCase(sendChatMessage.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(sendChatMessage.fulfilled, (state, action) => {
        state.loading = false
        const userMessage = action.payload.userMessage || ''
        state.messages.push({
          role: 'user',
          content: userMessage,
          timestamp: new Date().toISOString()
        })
        state.messages.push({
          role: 'assistant',
          content: action.payload.response,
          form_data: action.payload.extracted_data,
          timestamp: new Date().toISOString()
        })
      })
      .addCase(sendChatMessage.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload
      })
  }
})

// Export actions
export const { addUserMessage, addAssistantMessage, clearChat, clearError } = chatSlice.actions

// Export reducer
export default chatSlice.reducer