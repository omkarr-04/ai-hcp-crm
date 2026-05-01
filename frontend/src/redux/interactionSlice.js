/**
 * Interaction Redux Slice
 * Manages state for HCP interaction CRUD operations
 */

import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import api from '../services/api'

// Async thunks for API calls
export const fetchInteractions = createAsyncThunk(
  'interactions/fetchInteractions',
  async (_, { rejectWithValue }) => {
    try {
      const response = await api.get('/api/interaction')
      return response.data.items || []
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch interactions')
    }
  }
)

export const createInteraction = createAsyncThunk(
  'interactions/createInteraction',
  async (interactionData, { rejectWithValue }) => {
    try {
      const response = await api.post('/api/interaction', interactionData)
      return response.data
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to create interaction')
    }
  }
)

export const updateInteraction = createAsyncThunk(
  'interactions/updateInteraction',
  async ({ id, data }, { rejectWithValue }) => {
    try {
      const response = await api.put(`/api/interaction/${id}`, data)
      return response.data
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to update interaction')
    }
  }
)

export const deleteInteraction = createAsyncThunk(
  'interactions/deleteInteraction',
  async (id, { rejectWithValue }) => {
    try {
      await api.delete(`/api/interaction/${id}`)
      return id
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to delete interaction')
    }
  }
)

// Initial state
const initialState = {
  interactions: [],
  currentInteraction: null,
  loading: false,
  error: null,
  success: false
}

// Slice
const interactionSlice = createSlice({
  name: 'interactions',
  initialState,
  reducers: {
    // Clear current interaction
    clearCurrentInteraction: (state) => {
      state.currentInteraction = null
    },
    // Clear error
    clearError: (state) => {
      state.error = null
    },
    // Clear success flag
    clearSuccess: (state) => {
      state.success = false
    }
  },
  extraReducers: (builder) => {
    builder
      // Fetch Interactions
      .addCase(fetchInteractions.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(fetchInteractions.fulfilled, (state, action) => {
        state.loading = false
        state.interactions = action.payload
      })
      .addCase(fetchInteractions.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload
      })
      // Create Interaction
      .addCase(createInteraction.pending, (state) => {
        state.loading = true
        state.error = null
        state.success = false
      })
      .addCase(createInteraction.fulfilled, (state, action) => {
        state.loading = false
        state.interactions.unshift(action.payload)
        state.success = true
      })
      .addCase(createInteraction.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload
      })
      // Update Interaction
      .addCase(updateInteraction.pending, (state) => {
        state.loading = true
        state.error = null
        state.success = false
      })
      .addCase(updateInteraction.fulfilled, (state, action) => {
        state.loading = false
        const index = state.interactions.findIndex(i => i.id === action.payload.id)
        if (index !== -1) {
          state.interactions[index] = action.payload
        }
        state.success = true
      })
      .addCase(updateInteraction.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload
      })
      // Delete Interaction
      .addCase(deleteInteraction.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(deleteInteraction.fulfilled, (state, action) => {
        state.loading = false
        state.interactions = state.interactions.filter(i => i.id !== action.payload)
      })
      .addCase(deleteInteraction.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload
      })
  }
})

// Export actions
export const { clearCurrentInteraction, clearError, clearSuccess } = interactionSlice.actions

// Export reducer
export default interactionSlice.reducer