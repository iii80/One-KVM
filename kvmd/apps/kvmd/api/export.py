# ========================================================================== #
#                                                                            #
#    KVMD - The main Pi-KVM daemon.                                          #
#                                                                            #
#    Copyright (C) 2018  Maxim Devaev <mdevaev@gmail.com>                    #
#                                                                            #
#    This program is free software: you can redistribute it and/or modify    #
#    it under the terms of the GNU General Public License as published by    #
#    the Free Software Foundation, either version 3 of the License, or       #
#    (at your option) any later version.                                     #
#                                                                            #
#    This program is distributed in the hope that it will be useful,         #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of          #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the           #
#    GNU General Public License for more details.                            #
#                                                                            #
#    You should have received a copy of the GNU General Public License       #
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.  #
#                                                                            #
# ========================================================================== #


import asyncio
import operator

from typing import Any
from typing import List

from aiohttp.web import Request
from aiohttp.web import Response

from ....plugins.atx import BaseAtx

from ..info import InfoManager

from ..http import exposed_http


# =====
class ExportApi:
    def __init__(self, info_manager: InfoManager, atx: BaseAtx) -> None:
        self.__info_manager = info_manager
        self.__atx = atx

    # =====

    @exposed_http("GET", "/export/prometheus/metrics")
    async def __prometheus_metrics_handler(self, _: Request) -> Response:
        (atx_state, hw_state) = await asyncio.gather(*[
            self.__atx.get_state(),
            self.__info_manager.get_submanager("hw").get_state(),
        ])
        rows: List[str] = []
        self.__append_prometheus_rows(rows, atx_state["enabled"], "pikvm_atx_enabled")
        self.__append_prometheus_rows(rows, atx_state["leds"]["power"], "pikvm_atx_power")
        if hw_state is not None:
            self.__append_prometheus_rows(rows, hw_state["health"], "pikvm_hw")
        return Response(text="\n".join(rows))

    def __append_prometheus_rows(self, rows: List[str], value: Any, path: str) -> None:
        if isinstance(value, bool):
            value = int(value)
        if isinstance(value, (int, float)):
            rows.extend([
                f"# TYPE {path} gauge",
                f"{path} {value}",
                "",
            ])
        elif isinstance(value, dict):
            for (sub_key, sub_value) in sorted(value.items(), key=operator.itemgetter(0)):
                sub_path = (f"{path}_{sub_key}" if sub_key != "parsed_flags" else path)
                self.__append_prometheus_rows(rows, sub_value, sub_path)
