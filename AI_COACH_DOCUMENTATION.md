# AI Coach Implementation

The Oracle Platform now features an advanced AI coach system that provides intelligent relationship and personal growth guidance.

## How It Works

The AI coach system uses OpenAI's GPT-4 to generate personalized responses based on:

1. The selected coach personality (Supportive, Direct, Strategic, or Intuitive)
2. The user's message content with deep context analysis
3. The conversation history and relationship context
4. Advanced emotional and situation analysis
5. Pattern recognition for relationship dynamics

## Enhanced Personalization Features

The AI coach now features advanced personalization capabilities:

1. **Name Recognition**: Identifies and uses names mentioned in conversation
2. **Relationship Duration Analysis**: Recognizes how long situations have been ongoing
3. **Emotional State Detection**: Identifies the user's emotional state from their message
4. **Relationship Status Recognition**: Detects relationship type and stage
5. **Core Concern Identification**: Pinpoints the main issue the user is struggling with
6. **Topic Relevance Scoring**: Prioritizes responses based on the most important topics
7. **Context-Aware Responses**: Builds on previous conversation exchanges

## Features

- **Four Distinct Coaching Personalities**: Each coach has a unique style and approach
- **Real AI Responses**: Using OpenAI's GPT-4 for intelligent, contextual coaching
- **Fallback System**: An advanced fallback system if API is unavailable
- **Conversation History**: Records and learns from previous exchanges
- **Emotional Analysis**: Recognizes emotional states and responds appropriately
- **Relationship Pattern Recognition**: Identifies common relationship dynamics

## Usage

To use the AI Coach:

1. Navigate to the `/ai-coach` route
2. Select your preferred coaching style
3. Enter your situation or question
4. Receive personalized guidance from your chosen coach

## Technical Implementation

- Backend: Flask API with OpenAI integration
- Frontend: Interactive JavaScript interface
- Database: Stores conversations for continuity
- Fallback: Advanced rule-based system when API is unavailable

## Required API Key

The system works best with a valid OpenAI API key in the `.env` file:

```
OPENAI_API_KEY=your_openai_api_key_here
```

Without a valid key, the system will still function using the advanced fallback system, which provides intelligent responses based on message content analysis.

## Error Handling

If you see the error "Error on conversation request", possible causes are:

1. Missing or invalid OpenAI API key
2. Network connectivity issues
3. API rate limits or quota exceeded
4. Backend server errors

The system will automatically fall back to the rule-based response system in these cases.
