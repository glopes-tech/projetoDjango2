from django.core.management.base import BaseCommand
from enquete.models import Pergunta

class Command(BaseCommand):
    help = 'Atualiza valores de tipo de pergunta para os nomes constantes no código'

    def handle(self, *args, **kwargs):
        mapa_tipos = {
            'unica': 'UNICA_ESCOLHA',
            'multipla': 'MULTIPLA_ESCOLHA'
        }

        atualizadas = 0
        for pergunta in Pergunta.objects.all():
            if pergunta.tipo in mapa_tipos:
                pergunta.tipo = mapa_tipos[pergunta.tipo]
                pergunta.save()
                atualizadas += 1
                self.stdout.write(f'✅ Pergunta atualizada: {pergunta.texto[:50]}')

        if atualizadas == 0:
            self.stdout.write('⚠ Nenhuma pergunta precisava de ajuste.')
        else:
            self.stdout.write(f'\n🎉 {atualizadas} perguntas atualizadas com sucesso.')
