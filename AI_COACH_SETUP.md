# AI Coach Setup Guide

This guide provides instructions for setting up and using the new AI Coach system with real AI-powered responses.

## Requirements

- Python 3.6+
- Flask
- OpenAI API key (for GPT-4)
- Internet connection for API calls

## Setup Instructions

1. **Install Dependencies**

   Make sure all required packages are installed:

   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment Variables**

   Create or update your `.env` file with the following:

   ```
   # OpenAI Settings
   OPENAI_API_KEY=your_openai_api_key_here
   ```

   Replace `your_openai_api_key_here` with your actual OpenAI API key.

3. **Restart the Application**

   Restart the Flask application to apply the changes:

   ```bash
   python3 app.py
   ```

## AI Coach Features

The AI Coach now provides real AI-powered responses using OpenAI's GPT-4. Each coach personality has been configured with specific:

- **Personality traits** - Defining the coach's approach and tone
- **Coaching style** - How they present advice and feedback
- **Response formatting** - Including characteristic emojis and communication patterns

### Available Coaches

1. **Supportive Maya (💚)**
   - Gentle, empathetic guidance
   - Emotional validation and nurturing support
   - Focuses on emotional healing and gentle boundary setting

2. **Direct Dana (🔥)**
   - Straight-talk coaching with tough love
   - No-nonsense reality checks
   - Focuses on action and accountability

3. **Strategic Sam (🧠)**
   - Analytical approach with logical frameworks
   - Data-driven insights and pattern recognition
   - Focuses on step-by-step action plans

4. **Intuitive Iris (✨)**
   - Wisdom-based guidance
   - Focus on inner knowing and spiritual growth
   - Connects emotional patterns to deeper meanings

### Coach Conversations

- All conversations are stored securely in the database
- User can view past conversation history
- The system maintains context between messages
- Fallback responses are provided if the API is unavailable

## Testing the AI Coach

1. Log in to the platform
2. Navigate to the AI Coach page (`/ai-coach`)
3. Select a coach type
4. Start a conversation by typing a message
5. Observe the AI-generated response
6. Test different coach types to experience their unique styles

## Troubleshooting

- **API Errors**: Check your OpenAI API key and network connection
- **Slow Responses**: The AI may take a moment to generate thoughtful responses
- **Page Not Loading**: Ensure the Flask application is running properly

## Notes for Developers

- The AI response system is in `app.py` under `generate_ai_coach_response()`
- Conversation history is stored in the `ai_coach_conversations` table
- Frontend code in `templates/ai-coach.html` handles the UI interactions
- The system has a fallback mechanism if the API fails
