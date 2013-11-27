# -*- coding: utf8 -*-
# Custom Settings
from mezzanine.conf import register_setting

register_setting(
    name="CEP_ORIGIN",
    description="Cep de Origem no cálculo",
    editable=True,
    default="",
)

