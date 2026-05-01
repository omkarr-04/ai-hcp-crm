/**
 * Redux store configuration for AI-HCP CRM.
 * Sets up the store with middleware and reducers.
 */

import { configureStore } from '@reduxjs/toolkit'
import interactionReducer from './interactionSlice'
import chatReducer from './chatSlice'

// Configure the Redux store
export const store = configureStore({
  reducer: {
    // Interaction slice for managing interaction form data
    interactions: interactionReducer,
    // Chat slice for managing AI chat state
    chat: chatReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        // Ignore these action types for serialization check
        ignoredActions: ['chat/addMessage'],
      },
    }),
})

// Export types for TypeScript (if used)
export default store