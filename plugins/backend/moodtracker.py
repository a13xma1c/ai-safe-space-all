def after_ai_reply(user_message, ai_reply, user_id):
    # Dummy example: if user mentions "sad", nudge mood wheel
    if "sad" in user_message:
        return ai_reply + "<br>Would you like to try the mood wheel?"
    return ai_reply
