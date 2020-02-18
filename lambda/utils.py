import logging
import os
import boto3
from botocore.exceptions import ClientError


story_coxinha = [
    (0,"Você foi recrutado pelo exército para combater a ameaça mortadela que assola nosso país, quanto mais pedra papel e tesouras você ganhar mais voce progride na sua carreira. atualmente você é um soldado raso."),
    (5,"Parabéns voce foi promovido a cabo por sua exelencia em combate, você parece ser uma estrela em ascensão nesse exército"),
    (10,"Olha o novo sargento ai, essa batalha chega ficou mais facil com você no time. Mas ela ainda não acabou temos que proteger a capital."),
    (18,"Você foi promovido a subtenente, trabalhe só mais um pouco e chegara em tenente."),
    (26,"Incrivel voce é uma maquina no pedra papel e tesoura, você agora é um dos nossos incriveis tenentes"),
    (30,"O capitão do setor 34 foi destruido no pedra papel e tesoura, parabens você é o novo capitão."),
    (40,"A capital foi invadida você é nossa unica esperança, salve a todos o grande major"),
    (50,"Você salvou a cidade mesmo com a traição do general Hamilton, fique com o cargo de general dele por sua valentia."),
    (70,"Nosso marechal infelizmente morreu, mas com o seu sucesso nas batalhas esse cargo vai para você parabens você chegou no ápice da sua carreira.")
]

story_mortadela = [
    (0,"Obrigado por acreditar na casa mortadela, nossa contra o governo coxinha atual só esta começando. Vença varios oponentes no pedra papel e tesoura para evoluir dentro na nossa revolução."),
    (7,"Lacrou pindola de borboleta. você foi muito bem para um iniciante, você recebeu uma promoção agora é militante nivel 2 "),
    (15,"O partido amou sua performase, voce foi transferido para a capital para preparar a invasão do proletariado, se a classe trabalhadora tudo produz a ela tudo pertence."),
    (20,"Ui Ui. todo trabalhado na revolução. Arrasou entramos na cidade mas ainda temos muitas pedra pra carregar."),
    (24,"A gerra do jokenpo chegou no apice, muitos dedos cansados. lute mais um pouco para nossa revolução."),
    (35,"Você perdeu seus dedos. só um milagre para a gente vencer essa guerra. "),
    (47,"Você é o milagre, esta jogando com os dedos do pé. Você é incrivel o nome do meu filho vai ser o seu."),
    (63,"Ganhamos a revolução e como bom combatente você virou o grande lider da nossa nação.")
]


def get_story_frase(time, kills):
    aux_array = story_coxinha if time == 'coxinha' else story_mortadela
    
    for i, obj  in enumerate(aux_array):
        if obj != aux_array[-1] and aux_array[i+1][0] >= kills:
            return "{} .Você precisa ter {} vitórias para progredir para o proximo trecho de historia, atualmente você tem {} vitórias. Tente conseguir mais. Vamos lá escolha pedra papel ou tesoura".format(obj[1],aux_array[i+1][0],kills)
    return aux_array[-1][1] + ".Parabens você chegou no cargo maximo."


def create_presigned_url(object_name):
    """Generate a presigned URL to share an S3 object with a capped expiration of 60 seconds

    :param object_name: string
    :return: Presigned URL as string. If error, returns None.
    """
    s3_client = boto3.client('s3', config=boto3.session.Config(signature_version='s3v4',s3={'addressing_style': 'path'}))
    try:
        bucket_name = os.environ.get('S3_PERSISTENCE_BUCKET')
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket_name,
                                                            'Key': object_name},
                                                    ExpiresIn=60*1)
    except ClientError as e:
        logging.error(e)
        return None

    # The response contains the presigned URL
    return response
    