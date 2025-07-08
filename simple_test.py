from app import extract_main_concern, extract_emotion, generate_advanced_fallback_response

message = "hey, i need advice, my boyfriend just disappeared on my birthday"
concern = extract_main_concern(message)
emotion = extract_emotion(message)

print(f"Message: '{message}'")
print(f"Detected Concern: {concern}")
print(f"Detected Emotion: {emotion}")

# Test direct coach only
coach_type = "direct"
response = generate_advanced_fallback_response(message, coach_type, [])

# Write to file
with open("direct_response.txt", "w") as f:
    f.write(f"Direct Coach Response:\n{response}")
