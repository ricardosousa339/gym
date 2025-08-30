import os
import unicodedata
import re
from typing import Optional, Union

def map_exercise_to_group(name: str) -> str:
    """Mapeia exercício para grupo muscular"""
    if not isinstance(name, str):
        return 'Outros'
    s = name.strip().lower()
    groups = [
        (['supino', 'bench', 'crucifixo', 'crossover', 'peck deck', 'fly'], 'Peito'),
        (['remada', 'puxada', 'pulldown', 'barra fixa', 'serrote', 'pullover', 'row'], 'Costas'),
        (['agachamento', 'squat', 'leg press', 'hack', 'afundo', 'lunge', 'extensora', 'flexora', 'adutora', 'abdutora'], 'Pernas'),
        (['desenvolvimento', 'elevação lateral', 'elevação frontal', 'arnold', 'shoulder', 'militar'], 'Ombros'),
        (['rosca', 'curl', 'bíceps', 'biceps'], 'Bíceps'),
        (['tríceps', 'triceps', 'paralelas', 'mergulho', 'pulley', 'testa'], 'Tríceps'),
        (['glúteo', 'gluteo', 'hip thrust', 'coice', 'abdução', 'elevação pélvica'], 'Glúteos'),
        (['panturrilha', 'gemelar', 'calf'], 'Panturrilha'),
        (['abdominal', 'abs', 'prancha', 'crunch', 'core'], 'Core'),
        (['esteira', 'bike', 'spinning', 'corrida', 'remador', 'rower'], 'Cardio'),
    ]
    for keywords, grp in groups:
        if any(k in s for k in keywords):
            return grp
    return 'Outros'

def get_group_icon_path(group: str) -> str:
    """Retorna o caminho do ícone para um grupo muscular"""
    base = 'icons/grupo'
    slug = {
        'Peito': 'peito', 'Costas': 'costas', 'Pernas': 'pernas', 'Ombros': 'ombros',
        'Bíceps': 'biceps', 'Tríceps': 'triceps', 'Glúteos': 'gluteos', 'Panturrilha': 'panturrilha',
        'Core': 'core', 'Cardio': 'cardio'
    }.get(group, 'core')
    path = f"{base}/{slug}.svg"
    return path if os.path.exists(path) else f"{base}/core.svg"

def alias_name(name: str, max_len: int = 16) -> str:
    """Cria um alias curto para o nome do exercício"""
    if not isinstance(name, str) or not name:
        return ''
    s = name
    # remove conteúdo entre parênteses e múltiplos espaços
    s = re.sub(r"\s*\([^)]*\)", "", s).strip()
    parts = s.split()
    # manter 1–2 palavras
    s = " ".join(parts[:2]) if len(" ".join(parts[:2])) >= 6 else (" ".join(parts[:3]) if len(parts) >= 3 else s)
    if len(s) > max_len:
        s = s[: max_len - 1].rstrip() + '…'
    return s

def get_group_emoji(group: Optional[str]) -> str:
    """Retorna emoji para um grupo muscular"""
    m = {
        'Peito': '🏋️',
        'Costas': '🧗',
        'Pernas': '🦵',
        'Ombros': '🧍',
        'Bíceps': '💪',
        'Tríceps': '🦾',
        'Glúteos': '🟤',
        'Panturrilha': '🦶',
        'Core': '🧘',
        'Cardio': '❤️',
    }
    return m.get(group or '', '')

def get_exercise_emoji(exercise: Optional[str], group: Optional[str] = None) -> str:
    """Retorna emoji específico para um exercício"""
    if isinstance(exercise, str):
        s = exercise.lower()
        # por palavras-chave do exercício
        if any(k in s for k in ['supino']):
            return '🏋️'
        if any(k in s for k in ['agachamento', 'leg press', 'hack']):
            return '🦵'
        if any(k in s for k in ['terra']):
            return '🏋️'
        if any(k in s for k in ['remada', 'remador']):
            return '🚣'
        if any(k in s for k in ['barra fixa', 'pull-up', 'puxada', 'pulldown']):
            return '🧗'
        if any(k in s for k in ['rosca', 'bíceps', 'biceps', 'curl']):
            return '💪'
        if any(k in s for k in ['tríceps', 'triceps', 'testa', 'mergulho']):
            return '🦾'
        if any(k in s for k in ['panturrilha', 'calf']):
            return '🦶'
        if any(k in s for k in ['abdominal', 'abs', 'prancha', 'crunch', 'core']):
            return '🧘'
        if any(k in s for k in ['esteira', 'corrida']):
            return '🏃'
        if any(k in s for k in ['bike', 'spinning']):
            return '🚴'
    # fallback para o grupo
    return get_group_emoji(group or '')

def get_exercise_icon_path(exercise: str, group: Optional[str] = None) -> str:
    """Retorna o caminho do ícone para um exercício"""
    # tenta ícone específico do exercício e faz fallback para ícone do grupo
    if isinstance(exercise, str) and exercise:
        # slugify leve: remover acentos, deixar letras/números e '-'
        txt = unicodedata.normalize('NFKD', exercise)
        txt = ''.join(c for c in txt if not unicodedata.combining(c))
        slug = re.sub(r'[^a-zA-Z0-9]+', '-', txt).strip('-').lower()
        path = f"icons/exercicio/{slug}.svg"
        if os.path.exists(path):
            return path
    return get_group_icon_path(group or map_exercise_to_group(exercise))
