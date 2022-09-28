import streamlit as st
import hydralit_components as hc
import extra_streamlit_components as stx

from ..core.labels import gl


class Menu:
    def __init__(self, use_nav_bar=False):

        # specify the primary menu definition
        menu_data = [
            {"id": "athlete", "icon": "💗"},
            {"id": "race", "icon": "🌍"},
            {"id": "perf", "icon": "🏊🚴🏃"},
            {"id": "simulation", "icon": "🏆"},
            # {"id": "about", "icon": "💻"},
        ]
        self.menu_steps = [m["id"] for m in menu_data]
        for m in menu_data:
            m["label"] = gl(m["id"])

        if use_nav_bar:
            self.menu_id = hc.nav_bar(
                menu_definition=menu_data,
                override_theme={"txc_inactive": "#FFFFFF"},
                hide_streamlit_markers=False,
                sticky_nav=True,
                sticky_mode="pinned",
            )
        else:
            self.menu_id = stx.stepper_bar(steps=self.menu_steps)

    def is_menu(self, code):
        def is_menu_str(c):
            return self.menu_id == c or self.menu_id == self.menu_steps.index(c)

        if type(code) is list:
            for c in code:
                if is_menu_str(c):
                    return True
            return False
        else:
            return is_menu_str(code)
