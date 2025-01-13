import logging
import ask_sdk_core.utils as ask_utils

from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)



class LaunchRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        speak_output = (
            "Welcome to my TTS skill! You can ask me to say something like, "
            '"say hello," or "say this loudly."'
        )
        return (
            handler_input.response_builder
            .speak(speak_output)
            .reprompt("What would you like me to say?")
            .response
        )


# TTS Intent Handler
class TTSIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (
            ask_utils.is_request_type("IntentRequest")(handler_input)
            and ask_utils.get_intent_name(handler_input) == "ttsintent"
        )

    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        text_to_say = slots["text"].value if "text" in slots and slots["text"].value else "I didn’t catch that."

        # SSML Settings
        keywords = {
            "loudly": {"volume": "loud"},
            "softly": {"volume": "x-soft"},
            "slowly": {"rate": "slow"},
            "quickly": {"rate": "fast"},
            "whisper": {"effect": "whispered"},
        }
        volume = "medium"
        rate = "medium"
        effect = None

    
        for keyword, settings in keywords.items():
            if keyword in text_to_say.lower():
                if "volume" in settings:
                    volume = settings["volume"]
                if "rate" in settings:
                    rate = settings["rate"]
                if "effect" in settings:
                    effect = settings["effect"]

                
                text_to_say = text_to_say.replace(keyword, "").strip()

        # Build SSML response
        if effect == "whispered":
            ssml_output = f"<speak><amazon:effect name='whispered'>{text_to_say}</amazon:effect></speak>"
        else:
            ssml_output = (
                f"<speak><prosody volume='{volume}' rate='{rate}'>{text_to_say}</prosody></speak>"
            )

        return handler_input.response_builder.speak(ssml_output).reprompt("What else would you like me to say?").response


# Help Intent Handler
class HelpIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (
            ask_utils.is_request_type("IntentRequest")(handler_input)
            and ask_utils.get_intent_name(handler_input) == "AMAZON.HelpIntent"
        )

    def handle(self, handler_input):
        speak_output = (
            'You can ask me to say something by providing the text. Try saying, "Say this loudly," or "Say this softly."'
        )
        return handler_input.response_builder.speak(speak_output).reprompt("What would you like me to say?").response


# Cancel and Stop Intent Handler
class CancelAndStopIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (
            ask_utils.is_request_type("IntentRequest")(handler_input)
            and ask_utils.get_intent_name(handler_input)
            in ["AMAZON.CancelIntent", "AMAZON.StopIntent"]
        )

    def handle(self, handler_input):
        speak_output = "Goodbye!"
        return handler_input.response_builder.speak(speak_output).response


# Fallback Intent Handler
class FallbackIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (
            ask_utils.is_request_type("IntentRequest")(handler_input)
            and ask_utils.get_intent_name(handler_input) == "AMAZON.FallbackIntent"
        )

    def handle(self, handler_input):
        speak_output = (
            "Sorry, I didn’t understand that. You can ask me to say something by providing the text."
        )
        return handler_input.response_builder.speak(speak_output).reprompt("What would you like me to say?").response


# Generic Error Handler
class ErrorHandler(AbstractExceptionHandler):
    def can_handle(self, handler_input, exception):
        return True

    def handle(self, handler_input, exception):
        logger.error(exception, exc_info=True)
        speak_output = "Sorry, I had trouble doing what you asked. Please try again."
        return handler_input.response_builder.speak(speak_output).reprompt("What would you like me to say?").response


# Skill Builder
from ask_sdk_core.skill_builder import SkillBuilder

sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(TTSIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelAndStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_exception_handler(ErrorHandler())

lambda_handler = sb.lambda_handler()
