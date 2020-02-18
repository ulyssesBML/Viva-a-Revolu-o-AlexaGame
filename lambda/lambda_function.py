# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import logging
import random
import ask_sdk_core.utils as ask_utils
import boto3
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_core.attributes_manager import AbstractPersistenceAdapter
from ask_sdk_core.utils.request_util import get_slot
from ask_sdk_model import Response
from ask_sdk_dynamodb.partition_keygen import user_id_partition_keygen
from ask_sdk_dynamodb.adapter import DynamoDbAdapter, user_id_partition_keygen
from boto3.dynamodb.conditions import Key, Attr
from utils import get_story_frase

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


boto_sts=boto3.client('sts')
stsresponse = boto_sts.assume_role(
    RoleArn="",
    RoleSessionName=''
)

# Save the details from assumed role into vars
newsession_id = stsresponse["Credentials"]["AccessKeyId"]
newsession_key = stsresponse["Credentials"]["SecretAccessKey"]
newsession_token = stsresponse["Credentials"]["SessionToken"]

ddb2 = boto3.resource(
    'dynamodb',
    region_name='sa-east-1',
    aws_access_key_id=newsession_id,
    aws_secret_access_key=newsession_key,
    aws_session_token=newsession_token
)

db = DynamoDbAdapter(table_name="dynamo_revolucao",partition_key_name="id",partition_keygen=user_id_partition_keygen,dynamodb_resource=ddb2)


class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input, ):
        # type: (HandlerInput) -> Response
        speak_output = ""        
        try:# checar se usuario existe
            request_envelope = handler_input.request_envelope

            user = db.get_attributes(request_envelope=request_envelope)

            if not user.get('apelido'):
                user['kills'] = 0
                user['deaths'] = 0
                db.save_attributes(request_envelope=request_envelope,attributes=user)
                speak_output = speak_output +   """
                                                    <speak>
                                                        Pelo jeito você não tem uma conta ainda. Vamos começar com seu apelido <break/> para cadastrar um apelido fale <break/> meu apelido é e fale seu apelido <break/>
                                                    </speak>
                                                """
            elif not user.get('frase'):
                speak_output = speak_output + """ <break/>Ok {}. Agora cadestre agora sa frase de vitória basta falar <break/> Minha frase de vitória é <break/> então diga sua frase. Essa frase será apresentada para o adiversario perdedor. """.format(user.get('apelido'))

            elif not user.get('time'):
                speak_output = speak_output + """ <break/>Tudo certo. Agora escolha entre time coxinha ou mortadela."""
            else:
                speak_output = speak_output + "<speak>Ola {}. Vamos jogar, para atacar escolha pedra, papel ou tesoura. Caso queira ver a historia diga ver historia.</speak>".format(user.get('apelido'))
        
        except Exception as e:
            speak_output = "ocorreu um erro"
        
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class CreateName(AbstractRequestHandler):
    """Handler for Hello World Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("CreateName")(handler_input)

    def handle(self, handler_input):
        
        apelido = ask_utils.get_slot_value(handler_input=handler_input, slot_name="apelido")
        speak_output = "Seu apelido agora é " + apelido
        request_envelope = handler_input.request_envelope
        
        try:# checar se usuario existe
            user = db.get_attributes(request_envelope=request_envelope)
            user['apelido'] = apelido
            db.save_attributes(request_envelope=request_envelope,attributes=user)
            if not user.get('time'):
                speak_output = speak_output
        except Exception as e:
            speak_output = "Ocorreu um problema."
            
        return LaunchRequestHandler().handle(handler_input)
        #return handler_input.response_builder.speak(speak_output).ask(speak_output).response

class CreateVictoryPhrase(AbstractRequestHandler):
    """Handler for Hello World Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("VictoryPhrase")(handler_input)

    def handle(self, handler_input):
        try:# checar se usuario existe
            frase = ask_utils.get_slot_value(handler_input=handler_input, slot_name="frase")
            request_envelope = handler_input.request_envelope
            speak_output = "Sua frase de vitória é " + frase
            user = db.get_attributes(request_envelope=request_envelope)
            user['frase'] = frase
            db.save_attributes(request_envelope=request_envelope,attributes=user)
        except Exception as e:
            #speak_output = str(e)
            speak_output = "Ocorreu um problema."
        return LaunchRequestHandler().handle(handler_input)

class CoxinhaTeam(AbstractRequestHandler):
    """Handler for Hello World Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("Coxinha")(handler_input)

    def handle(self, handler_input):
        try:# checar se usuario existe
            speak_output = "Você agora é do time coxinha."
            request_envelope = handler_input.request_envelope
            user = db.get_attributes(request_envelope=request_envelope)
            user['time'] = "coxinha"
            db.save_attributes(request_envelope=request_envelope,attributes=user)
            if not user.get('frase'):
                speak_output = speak_output + ""
        except Exception as e:
            speak_output = "Ocorreu um problema."
        
        return LaunchRequestHandler().handle(handler_input)
        #return handler_input.response_builder.speak(speak_output).ask(speak_output).response
    
class MortadelaTeam(AbstractRequestHandler):
    """Handler for Hello World Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("Mortadela")(handler_input)

    def handle(self, handler_input):
        
        try:# checar se usuario existe
            speak_output = "Você agora é do time mortadela"
            request_envelope = handler_input.request_envelope
            user = db.get_attributes(request_envelope=request_envelope)
            user['time'] = "mortadela"
            db.save_attributes(request_envelope=request_envelope,attributes=user)
            if not user.get('frase'):
                speak_output = speak_output + "<break/> Agora cadestre agora sua frase de vitória basta falar <break/> Minha frase de vitória é <break/> então diga sua frase. Essa frase será apresentada para o adiversario perdedor."
        except Exception as e:
            speak_output = "Ocorreu um problema."
            speak_output = str(e)
        
        return LaunchRequestHandler().handle(handler_input)
        #return handler_input.response_builder.speak(speak_output).ask(speak_output).response

class AttackHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("Attack")(handler_input)

    def handle(self, handler_input):
        
        try:
            request_envelope = handler_input.request_envelope
            user = db.get_attributes(request_envelope=request_envelope)
            
            if not user.get('apelido'): 
                speak_output = "Você ainda não tem seu apelido cadastrado. Faça isso falando meu apelido é <break/> e então diga seu apelido."
            elif not user.get('frase'):
                speak_output = "Você ainda não tem uma frase cadastrada. Faça isso falando minha frase é <break/> e então diga sua frase."
            elif not user.get('time'):
                speak_output = "Você ainda não esta em nenhum time. Quer ser do time coxinha ou dos mortadelas."
            else:
                time = 'coxinha' if user.get('time') == 'mortadela' else 'mortadela'
                weapon = user['arma']
                table = ddb2.Table('dynamo_revolucao')
                response = table.scan(
                    FilterExpression=Attr('attributes.time').eq(time),
                    Limit=1000
                )
                opponents = response["Items"]
                if not opponents:
                    speak_output = "Não temos usuarios cadastrados neo seu time cadastrado. Volte mais tarde para jogar. Fale sair para sair"
                    return handler_input.response_builder.speak(speak_output).ask(speak_output).response

                random_num = random.randint(0,len(opponents)-1)
                selected_opponent = opponents[random_num]['attributes']

                win = False
                if weapon == selected_opponent['arma']:
                    win = None
                elif weapon == 'pedra':
                    if selected_opponent['arma'] == 'tesoura':
                        win = True
                elif weapon == 'papel':
                    if selected_opponent['arma'] == 'pedra':
                        win = True
                elif weapon == 'tesoura':
                    if selected_opponent['arma'] == 'papel':
                        win = True
                if win == None:
                    speak_output = "O jogo empatou seu oponente usou {}. Tente de novo. Pedra papel ou tesoura ?".format(weapon)
                elif win:
                    speak_output = """Parabens. Você ganhou do {}. Ele deve ta chorando agora, ouvindo sua mensagem da vitória.<break/> Vença mais oponentes, vamos de novo, vai querer o que ? pedra papel ou tesoura ?""".format(selected_opponent['apelido'])
                    user['kills'] = user['kills'] + 1
                else:
                    speak_output = """Vish seu oponente usou {}. Você perdeu pro {} do time {}. A frase que ele gostaria de te falar é {}.<break/> não deixe isso barato jogue de novo, vamos lá. Vai querer pedra papel ou tesoura ?""".format(selected_opponent['arma'],selected_opponent['apelido'], selected_opponent['time'], selected_opponent['frase'])
                    user['deaths'] = user['deaths'] + 1
                db.save_attributes(request_envelope=request_envelope,attributes=user)
        except Exception as e:
            #speak_output = str(e)   
            return LaunchRequestHandler().handle(handler_input)
            
        return handler_input.response_builder.speak(speak_output).ask(speak_output).response


class PedraHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("Pedra")(handler_input)

    def handle(self, handler_input):
        
        try:# checar se usuario existe
            speak_output = "Você escolheu pedra."
            request_envelope = handler_input.request_envelope
            user = db.get_attributes(request_envelope=request_envelope)
            user['arma'] = "pedra"
            db.save_attributes(request_envelope=request_envelope,attributes=user)
        except Exception as e:
            
            speak_output = "Ocorreu um problema."
        return AttackHandler().handle(handler_input)
        #return handler_input.response_builder.speak(speak_output).ask(speak_output).response

class PapelHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("Papel")(handler_input)

    def handle(self, handler_input):
        try:# checar se usuario existe
            speak_output = "Você escolheu papel."
            request_envelope = handler_input.request_envelope
            user = db.get_attributes(request_envelope=request_envelope)
            user['arma'] = "papel"
            db.save_attributes(request_envelope=request_envelope,attributes=user)
        except Exception as e:
            speak_output = "Ocorreu um problema."
        
        return AttackHandler().handle(handler_input)


class TesouraHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("Tesoura")(handler_input)

    def handle(self, handler_input):

        try:# checar se usuario existe
            speak_output = "Você escolheu tesoura."
            request_envelope = handler_input.request_envelope
            user = db.get_attributes(request_envelope=request_envelope)
            user['arma'] = "tesoura"
            db.save_attributes(request_envelope=request_envelope,attributes=user)
        except Exception as e:
            speak_output = "Ocorreu um problema."
        return AttackHandler().handle(handler_input)

class StoryHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("Story")(handler_input)
    def handle(self, handler_input):
        try:# checar se usuario existe
            request_envelope = handler_input.request_envelope
            user = db.get_attributes(request_envelope=request_envelope)
            if not user.get('apelido'): 
                speak_output = "Você ainda não tem seu apelido cadastrado.  Faça isso falando meu apelido é <break/> então diga seu apelido."
            elif not user.get('frase'):
                speak_output = "Você ainda nnão tem uma frase cadastrada. Faça isso falando minha frase é <break/> então diga sua frase."
            elif not user.get('time'):
                speak_output = "Você ainda não esta em nenhum time. Quer ser do time coxinha ou dos mortadelas."
            else:
                kills = user.get('kills')
                time = user.get('time')  
                speak_output = get_story_frase(time,kills)
        except Exception as e:
            #speak_output = str(e)
            return LaunchRequestHandler().handle(handler_input)

        return handler_input.response_builder.speak(speak_output).ask(speak_output).response


class DidNotUnderstandHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("DidNotUnderstand")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = '''Não te entendi. fale ajuda para você entender melhor os comando desse jogo'''
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Os comandos desse jogo são. pedra papel e tesoura para atacar. ver historia para ver a historia. Voce tambem pode alterar seu apelido com a seguinte frase mudar apelido para fulano, dando tambem para mudar a frase falando mudar frase para frase desejada e respectivamente para time."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = '''Volte sempre que quiser, esse jogo está sempre melhorando, até a próxima. <say-as interpret-as="interjection">tchau.</say-as>'''

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Me descupa o extresse me deixou confusa, tente me operar mais tarde."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.


sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())


sb.add_request_handler(CreateName())
sb.add_request_handler(CreateVictoryPhrase())
sb.add_request_handler(CoxinhaTeam())
sb.add_request_handler(MortadelaTeam())
sb.add_request_handler(PedraHandler())
sb.add_request_handler(PapelHandler())
sb.add_request_handler(TesouraHandler())
sb.add_request_handler(AttackHandler())
sb.add_request_handler(StoryHandler())

sb.add_request_handler(DidNotUnderstandHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
#sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()
