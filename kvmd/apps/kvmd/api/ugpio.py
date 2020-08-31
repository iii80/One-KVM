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


from aiohttp.web import Request
from aiohttp.web import Response

from ....validators.basic import valid_bool
from ....validators.basic import valid_float_f0

from ....validators.kvm import valid_ugpio_channel

from ..ugpio import UserGpio

from ..http import exposed_http
from ..http import make_json_response


# =====
class UserGpioApi:
    def __init__(self, user_gpio: UserGpio) -> None:
        self.__user_gpio = user_gpio

    # =====

    @exposed_http("GET", "/gpio")
    async def __state_handler(self, _: Request) -> Response:
        return make_json_response({
            "scheme": (await self.__user_gpio.get_scheme()),
            "view": (await self.__user_gpio.get_view()),
            "state": (await self.__user_gpio.get_state()),
        })

    @exposed_http("POST", "/gpio/switch")
    async def __switch_handler(self, request: Request) -> Response:
        channel = valid_ugpio_channel(request.query.get("channel"))
        state = valid_bool(request.query.get("state"))
        done = await self.__user_gpio.switch(channel, state)
        return make_json_response({"done": done})

    @exposed_http("POST", "/gpio/pulse")
    async def __pulse_handler(self, request: Request) -> Response:
        channel = valid_ugpio_channel(request.query.get("channel"))
        delay = valid_float_f0(request.query.get("delay", "0"))
        await self.__user_gpio.pulse(channel, delay)
        return make_json_response()
