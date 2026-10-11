"""
Módulo de componentes UI para o aplicativo de Controle de Cursos.
"""

from .alerts import (
    show_success,
    show_error,
    show_warning,
    show_info,
    show_validation_errors,
    show_empty_state,
    show_confirm_dialog,
    show_backup_success,
    show_import_summary,
    show_loading_spinner,
    show_curso_salvo,
    show_curso_excluido,
    show_toast,
)

from .ui import (
    page_header,
    page_title,
    status_do_curso,
    texto_relativo_prazo,
    render_faixa_curso,
    render_cabecalho_cursos,
    render_faixa_compacta,
    render_andamento_indicacoes,
    render_totais_painel,
    plural,
    limpar_confirmacoes_exclusao,
)

from .forms import (
    render_form_novo_curso,
    render_form_editar_curso,
)

from .topbar import (
    render_topbar,
    navegar_para,
)

from .sidebar import (
    render_sidebar,
)

from .calendar_view import CalendarView

__all__ = [
    'show_success',
    'show_error',
    'show_warning',
    'show_info',
    'show_validation_errors',
    'show_empty_state',
    'show_confirm_dialog',
    'show_backup_success',
    'show_import_summary',
    'show_loading_spinner',
    'show_curso_salvo',
    'show_curso_excluido',
    'show_toast',
    'page_header',
    'page_title',
    'status_do_curso',
    'texto_relativo_prazo',
    'render_faixa_curso',
    'render_cabecalho_cursos',
    'render_faixa_compacta',
    'render_andamento_indicacoes',
    'render_totais_painel',
    'plural',
    'render_form_novo_curso',
    'render_form_editar_curso',
    'render_topbar',
    'render_sidebar',
    'navegar_para',
    'CalendarView',
    'limpar_confirmacoes_exclusao',
]
