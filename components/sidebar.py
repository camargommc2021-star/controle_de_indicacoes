"""
Módulo de compatibilidade - a barra lateral foi descontinuada em favor do topbar.
"""

from components.topbar import render_topbar as render_sidebar, navegar_para

__all__ = ["render_sidebar", "navegar_para"]
