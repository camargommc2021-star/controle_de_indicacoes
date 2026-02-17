"""
Módulo de componentes UI para o aplicativo de Controle de Cursos.

Este módulo fornece componentes reutilizáveis para renderização de UI
usando Streamlit, separando a lógica de apresentação do app principal.
"""

# Cards
from .cards import (
    render_curso_card,
    render_curso_card_compact,
    render_metric_card,
    render_status_badge,
    render_priority_badge,
    render_prazo_indicator,
)

# Forms
from .forms import (
    render_form_novo_curso,
    render_form_editar_curso,
    render_form_editar_fic,
    render_form_fic_com_autocomplete,
)

# Tables
from .tables import (
    render_tabela_cursos,
    render_tabela_cursos_filtrada,
    render_lista_cursos_por_estado,
    render_cursos_concluidos,
    render_tabela_fics,
    render_tabela_fics_filtrada,
    render_fic_card,
)

# Alerts
from .alerts import (
    show_success,
    show_error,
    show_warning,
    show_info,
    show_validation_errors,
    show_empty_state,
)

# Sidebar
from .sidebar import (
    render_sidebar,
    render_menu_navigation,
    render_filtros_globais,
    render_status_resumo,
)

# Calendar
from .calendar_view import CalendarView

__all__ = [
    # Cards
    'render_curso_card',
    'render_curso_card_compact',
    'render_metric_card',
    'render_status_badge',
    'render_priority_badge',
    'render_prazo_indicator',
    # Forms
    'render_form_novo_curso',
    'render_form_editar_curso',
    'render_form_editar_fic',
    'render_form_fic_com_autocomplete',
    # Tables
    'render_tabela_cursos',
    'render_tabela_cursos_filtrada',
    'render_lista_cursos_por_estado',
    'render_cursos_concluidos',
    'render_tabela_fics',
    'render_tabela_fics_filtrada',
    'render_fic_card',
    # Alerts
    'show_success',
    'show_error',
    'show_warning',
    'show_info',
    'show_validation_errors',
    'show_empty_state',
    # Sidebar
    'render_sidebar',
    'render_menu_navigation',
    'render_filtros_globais',
    'render_status_resumo',
    # Calendar
    'CalendarView',
]
