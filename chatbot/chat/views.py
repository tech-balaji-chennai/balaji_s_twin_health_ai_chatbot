# chat/views.py

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from rest_framework.decorators import api_view
import json

from google import genai
from google.genai.errors import APIError

# Import local app components
from .llm_schemas import ClassificationOutput, Status, PYTHON_ESCALATION_MESSAGES
from .knowledge_base import LLM_RAG_CONTEXT
from .models import Conversation, Message  # Import the models we just defined

# --- Initialization ---

# Initialize the Gemini Client using the key from settings.py
try:
    client = genai.Client(api_key=settings.GEMINI_API_KEY)
except Exception as e:
    print(f"Error initializing Gemini client: {e}")
    client = None


# Helper function to load conversation history for context
def get_conversation_history(session_id):
    """Fetches or creates the conversation session and retrieves the message history."""
    try:
        conversation, created = Conversation.objects.get_or_create(session_id=session_id)

        # Retrieve the last 10 messages for context, ordered by time
        history_objs = conversation.messages.all().order_by('-timestamp')[:10]

        # Format history for the LLM prompt: [SENDER]: MESSAGE
        history_formatted = [
            f"[{msg.sender.upper()}]: {msg.text}"
            for msg in reversed(history_objs)  # Reverse to chronological order
        ]

        return conversation, "\n".join(history_formatted)

    except Exception as e:
        print(f"Database error fetching conversation {session_id}: {e}")
        return None, ""


@csrf_exempt  # Required for non-browser-based POST requests
@api_view(['POST'])  # DRF decorator
def chat_classification_api(request):
    """
    Handles incoming chat messages, loads history, calls Gemini for structured
    classification, logs the messages, and returns a JSON response.
    """
    # System check for client initialization
    if not client:
        error_response = PYTHON_ESCALATION_MESSAGES["system_error"]
        return JsonResponse(error_response, status=500)

    try:
        data = json.loads(request.body)
        user_message = data.get('user_message', '').strip()
        session_id = data.get('session_id')

        if not user_message or not session_id:
            return JsonResponse({"status": "error", "message": "Missing message or session ID."}, status=400)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format in request body"}, status=400)

    # --- 1. Get History and Prepare Prompt ---
    conversation, history_context = get_conversation_history(session_id)
    if not conversation:
        # If database fails to connect/fetch, escalate
        error_response = PYTHON_ESCALATION_MESSAGES["system_error"]
        return JsonResponse(error_response, status=503)

    # Log the user's message immediately
    Message.objects.create(conversation=conversation, sender='user', text=user_message)

    # Construct the full context prompt for the LLM
    full_prompt = f"""
    CONVERSATION HISTORY (Most recent message at the bottom):
    {history_context}
    [CURRENT_USER_MESSAGE]: "{user_message}"

    Based ONLY on the CONVERSATION HISTORY and the Classification Rules provided below,
    classify the topic, determine the action status, and generate the response message.

    RULES & CONTEXT:
    {LLM_RAG_CONTEXT}
    """

    # --- 2. Call Gemini for Structured Output ---
    try:
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=full_prompt,
            config={
                "system_instruction": "You are a highly efficient, professional conversation topic classifier for Twin Health. Your sole output MUST strictly adhere to the provided JSON schema. Adhere to all formatting rules in the CONTEXT.",
                "response_mime_type": "application/json",
                "response_json_schema": ClassificationOutput.model_json_schema(),
            }
        )

        # Validate and extract the structured response
        json_response_data = json.loads(response.text)
        validated_output = ClassificationOutput(**json_response_data)

        # --- 3. Log AI Response and Return ---
        ai_message = validated_output.response_message
        ai_status = validated_output.status.value
        ai_topic = validated_output.topic.value

        # Log the AI response message
        if ai_status != Status.NO_RESPONSE.value:
            Message.objects.create(
                conversation=conversation,
                sender='ai',
                text=ai_message,
                topic_category=ai_topic,
                status=ai_status
            )

        # Return the structured response back to the frontend
        return JsonResponse(validated_output.model_dump(), status=200)

    except APIError as e:
        print(f"Gemini API Error: {e}")
        error_response = PYTHON_ESCALATION_MESSAGES["system_error"]
        Message.objects.create(conversation=conversation, sender='ai', text=error_response['message'],
                               status=Status.ESCALATE.value)
        return JsonResponse(error_response, status=503)

    except Exception as e:
        print(f"Unexpected Internal Server Error: {e}")
        error_response = PYTHON_ESCALATION_MESSAGES["system_error"]
        Message.objects.create(conversation=conversation, sender='ai', text=error_response['message'],
                               status=Status.ESCALATE.value)
        return JsonResponse(error_response, status=500)
