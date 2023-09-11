import textbase
from textbase.message import Message
from openai import Model
import openai
import os
from typing import List
import random
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
English_Learning_Prompt = "Welcome to the English Language Learning Chatbot! I'll guide you through learning English step by step. Let's start by learning some basic phrases. Choose one path:\n 1)translation \n2)grammar "
English_Grmmar_Prompt = "Now that you know some basic phrases of English, lets study about its grammar, choose grammar or translation"
# Set up OpenAI API key
openai.api_key = "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"


def find_sim(user_input, correct_answer):
    corpus = [user_input] + correct_answer

    # Create the TF-IDF vectorizer
    vectorizer = TfidfVectorizer()

    # Fit and transform the corpus to TF-IDF vectors
    tfidf_matrix = vectorizer.fit_transform(corpus)

    # Calculate cosine similarity between the question and answers
    similarity_scores = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])

    return similarity_scores[0]
    
learning_phrases = [
    {"hindi": "नमस्ते", "english": "Hello"},
    {"hindi": "कैसे हो तुम?", "english": "How are you?"},
    {"hindi": "मैं ठीक हूँ, धन्यवाद", "english": "I'm fine, thank you."},
    {"hindi": "क्या आपका नाम क्या है?", "english": "What is your name?"},
    
    {"hindi": "आप कहाँ से हो?", "english": "Where are you from?"},
    {"hindi": "मैं भारत से हूँ", "english": "I am from India."},
    {"hindi": "क्या आपको खाना पसंद है?", "english": "Do you like food?"},
    {"hindi": "हां, मुझे खाना पसंद है", "english": "Yes, I like food."},
    {"hindi": "आपकी उम्र क्या है?", "english": "What is your age?"},
    
    {"hindi": "आपका पसंदीदा खाना क्या है?", "english": "What is your favorite food?"},
    {"hindi": "मेरे लिए खाने की कोई पसंदीदा चीज नहीं है", "english": "I don't have a favorite food."},
    {"hindi": "आपकी पसंदीदा फिल्म क्या है?", "english": "What is your favorite movie?"},
    {"hindi": "मैं फिल्में नहीं देख सकता, लेकिन मैं बहुत कुछ सीख सकता हूँ", "english": "I can't watch movies, but I can learn a lot."},
    {"hindi": "आपका शौक क्या है?", "english": "What are your hobbies?"},
    {"hindi": "मेरा शौक सिर्फ़ बातचीत करना है और सीखना है", "english": "My hobby is just chatting and learning."},
    {"hindi": "धन्यवाद", "english": "Thank you"},
    {"hindi": "कृपया", "english": "Please"},
    {"hindi": "माफ़ कीजिए", "english": "Excuse me"},
    {"hindi": "आपको दिन शुभ हो", "english": "Have a good day"},
]

def call_openai(prompt):
    ai_response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=1000,
        stop=None,
        temperature=0.3
    )
    return ai_response.choices[0].text.strip()

@textbase.chatbot("english-learning-bot")
def on_message(message_history: List[Message], state: dict = None):

    if state is None or "counter" not in state:
        state = {"counter": 0, "practice_option": "choose_path"}
        response=English_Learning_Prompt
        return response,state
    
    user_input = message_history[-1].content.strip().lower()
          
    if state["practice_option"] == "choose_path":
        if user_input == "1" or user_input == "translation":
            response = "Great! You've chosen Translation Practice. Type 'start' to begin."
            state["practice_option"] = "translation"
        elif user_input == "2" or user_input == "grammar":
            response = "Great! You've chosen Grammar Practice. Type 'start' to begin."
            state["practice_option"] = "grammar"
        else:
            response = "Invalid choice. Please select a valid path:\n1. Translation Practice\n2. Grammar Practice"
        return response, state
            
    elif user_input == "start":
        if state["practice_option"] == "translation":
            phrase = random.choice(learning_phrases)
            response = f"Great! Let's learn a phrase:\nHindi: {phrase['hindi']}\nTranslate to English:"
            state["current_phrase"] = phrase
            state["learning_phase"] = "verify_translation"
        elif state["practice_option"] == "grammar":
            response = "Great! Let's start with grammar practice. Type a sentence to practice grammar:"
            state["learning_phase"] = "grammar_practice"
        return response,state

    elif user_input == "quit":
        response = "Sure! Let's go back and choose a path again."
        state["practice_option"] = "choose_path"
        state["learning_phase"] = "choose_path"
        return response,state
                 
    #translation path
    elif state["practice_option"] == "translation":
        
        if state["learning_phase"] == "learning_phrases" or user_input.lower()=="next":
            phrase = random.choice(learning_phrases)
            response = f"Great! Let's learn a phrase:\nHindi: {phrase['hindi']}\nTranslate to English:"
            state["current_phrase"] = phrase
            state["learning_phase"] = "verify_translation"
            return response,state
        else:

            if state["learning_phase"] == "verify_translation":
                correct_translation = state["current_phrase"]["english"]

                if user_input.lower() == correct_translation.lower():
                    response = "Excellent! You got it right. Let's practice more.For next translation, type NEXT"
                    state["learning_phase"] = "learning_phrases"
                    return response,state
                else:
                    
                    customPrompt = f"Does the statement '{user_input}' holds the same meaning as '{correct_translation.lower()}',also grammar and spellings should be correct:true or false?"

                    answer = call_openai(customPrompt)
                
                    
                    
                    print(answer)
                    if "true" in answer.lower() or "yes" in answer.lower():
                        response = f"Excellent! You got it right. Most accurate answer was '{correct_translation}'.Let's practice more.For next translation, type NEXT"
                        state["learning_phase"] = "learning_phrases"
                        return response,state
                        
                    else:
                        response = f"Oops! That's not quite right. Try again. The correct translation is '{correct_translation}'.For next translation, type NEXT"
                        if user_input.lower()=="next":
                            state["learning_phase"] = "learning_phrases"
                        else:
                            state["learning_phase"] = "verify_translation"
                            return response,state

    #grammar
    elif state["practice_option"] == "grammar": 
        if state["learning_phase"] == "grammar_practice" or user_input.lower()=="next":
            phrase = random.choice(learning_phrases)
            prompt = f"Ask one English grammar question, it can be of 3 types: first, fill in the blanks; second: correct the error in the sentence, third, translate hindi '{phrase['hindi']}' into English with correct grammar and spellings and store it as question:, correct_answer:"
            text = call_openai(prompt)

            lines = text.split('\n')

            question = None
            correct_answer = None

            # Loop through each line and check for question and answer
            for line in lines:
                if line.startswith("Question:"):
                    question = line[len("Question:"):].strip()
                elif line.startswith("Correct Answer:"):
                    correct_answer = line[len("Correct Answer:"):].strip()

            # Print the extracted question and answer
            print("Question:", question)
            print("Correct Answer:", correct_answer)
            
            # Extract question and answer from the response
            
            response=question
            
            state["current_phrase"] = phrase
            state["correct_answer"] = correct_answer  # Store the correct answer in the state
            state["learning_phase"] = "verify_grammar"
            return response, state
        else:

            if state["learning_phase"] == "verify_grammar":                
                print(user_input)
                print(state["correct_answer"])
                if find_sim(user_input,[state["correct_answer"]])>0.7:
                    response = f"Excellent! You got it right. Most accurate answer was '{state['correct_answer']}'.Let's practice more.For next question, type NEXT"
                    state["learning_phase"] = "grammar_practice"
                    return response,state

                        
                else:
                    response = f"Oops! That's not quite right. Try again. The correct answer is '{state['correct_answer']}'.For next question, type NEXT"
                    if user_input.lower()=="next":
                        state["learning_phase"] = "grammar_practice"
                    else:
                        state["learning_phase"] = "verify_grammar"
                    return response,state

    return response, state
