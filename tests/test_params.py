#!/usr/bin/env python
# encoding: utf-8
#
# pmatic - A simple API to to the Homematic CCU2
# Copyright (C) 2016 Lars Michelsen <lm@larsmichelsen.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

# Add Python 3.x behaviour to 2.7
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import pytest

from test_api_remote import TestRemoteAPI
from pmatic.entities import Channel, Device
from pmatic.params import Parameter, ParameterINTEGER, ParameterFLOAT, ParameterBOOL, ParameterACTION, ParameterSTRING, ParameterENUM
from pmatic import utils, PMException

class TestParameter(TestRemoteAPI):
    @pytest.fixture(scope="class")
    def p(self, API):
        device = Device(API, {
            'address': 'KEQ0970393',
            #'children': ['KEQ0970393:0',
            #             'KEQ0970393:1',
            #             'KEQ0970393:2',
            #             'KEQ0970393:3',
            #             'KEQ0970393:4',
            #             'KEQ0970393:5',
            #             'KEQ0970393:6',
            'firmware': '1.4',
            'flags': 1,
            'interface': 'KEQ0714972',
            #'paramsets': ['MASTER'],
            'roaming': False,
            'type': 'HM-ES-PMSw1-Pl',
            'updatable': '1',
            'version': 1,
            'channels': [],
        })
        # address of channel
        "address",
        # communication direction of channel:
        # 0 = DIRECTION_NONE (Kanal unterstützt keine direkte Verknüpfung)
        # 1 = DIRECTION_SENDER
        # 2 = DIRECTION_RECEIVER
        "direction",
        # see device flags (0x01 visible, 0x02 internal, 0x08 can not be deleted)
        "flags",
        # channel number
        "index",
        # possible roles as sender
        "link_source_roles",
        # possible roles as receiver
        "link_target_roles",
        # list of available parameter sets
        "paramsets",
        # type of this channel
        "type",
        # version of the channel description
        "version",
        channel = Channel(device, {
            'address': 'KEQ0970393:1',
            'direction': 1,
            'flags': 1,
            'index': 1,
            'link_source_roles': [
                'KEYMATIC',
                'SWITCH',
                'WINDOW_SWITCH_RECEIVER',
                'WINMATIC'
            ],
            'link_target_roles': [],
            'paramsets': ['LINK', 'MASTER', 'VALUES'],
            'type': 'SHUTTER_CONTACT',
            'version': 15,
        })
        return Parameter(channel, {
            'control': 'SWITCH.STATE',
            'operations': 7,
            'name': 'STATE',
            'min': '0',
            'default': '0',
            'max': '1',
            '_value': True,
            'tab_order': 0,
            'flags': 1,
            'unit': '',
            'type': 'BOOL',
            'id': 'STATE',
            'channel': channel,
        })


    def test_attributes(self, p):
        assert p.control == "SWITCH.STATE"
        assert type(p.operations) == int
        assert p.operations == 7
        assert p.name == "STATE"
        assert p._value == "0"
        assert type(p.tab_order) == int
        assert type(p.flags) == int
        assert utils.is_text(p.unit)
        assert p.unit == ""
        assert p.type == "BOOL"
        assert p.id == "STATE"
        assert isinstance(p.channel, Channel)


    def test_from_api_value(self, p):
        p._from_api_value("X") == "X"


    def test_to_api_value(self, p):
        p._to_api_value("X") == "X"


    def test_validate(self, p):
        p._validate("X") == True


    def test_readable(self, p):
        assert p.readable == True

        p.operations = 4
        assert p.readable == False

        p.operations = 0
        assert p.readable == False

        p.operations = 3
        assert p.readable == True

        p.operations = 7


    def test_writable(self, p):
        assert p.writable == True

        p.operations = 4
        assert p.writable == False

        p.operations = 2
        assert p.writable == True

        p.operations = 7


    def test_title(self, p):
        assert p.title == "State"

        p.name = "X_XABC"
        assert p.title == "X Xabc"


    def test_value(self, p):
        assert p.value == p._value


    def test_value_setter(self, p):
        p.operations = 5
        with pytest.raises(PMException) as e:
            p.value = "XXX"
        assert 'can not be changed' in str(e.value)

        with pytest.raises(PMException) as e:
            assert p.set("YYY") == False
        assert 'can not be changed' in str(e.value)

        p.operations = 7
        p.datatype = "boolean" # fake for setting
        p.value = "false"

        p.set("false")


    def test_set_to_default(self, p):
        p.datatype = "boolean" # fake for setting
        p.value = "true"
        p.set_to_default()
        assert p.value == p.default


    def test_formated(self, p):
        assert p.formated() == "0"
        p.unit = "X"

        assert p.formated() == "0 X"

        p.unit = "%"
        assert p.formated() == "0%"

        p.unit = ""


    def test_magic_str_unicode_bytes(self, p):
        if utils.is_py2():
            assert utils.is_byte_string(p.__str__())
            assert utils.is_text(p.__unicode__())
        else:
            assert utils.is_text(p.__str__())
            assert utils.is_byte_string(p.__bytes__())

        assert str(p) == "0"
        assert bytes(p) == b"0"



class TestParameterFLOAT(TestRemoteAPI):
    @pytest.fixture(scope="class")
    def p(self, API):
        clima_regulator = Device.get_devices(API, device_name="Bad-Thermostat")[0].channels[1]
        return clima_regulator.values["SETPOINT"]


    def test_attributes(self, p):
        assert type(p) == ParameterFLOAT
        assert p.type == "FLOAT"
        assert p.unit == u"°C"
        assert p.name == "SETPOINT"
        assert type(p.value) == float
        assert type(p.min) == float
        assert type(p.max) == float
        assert type(p.default) == float


    def test_from_api_value(self, p):
        assert p._from_api_value("0.00000000") == 0.0
        assert p._from_api_value("1.00000001") == 1.00000001
        assert p._from_api_value("1") == 1.0


    def test_to_api_value(self, p):
        assert p._to_api_value(1.0) == "1.00"
        assert p._to_api_value(1.001) == "1.00"
        assert p._to_api_value(999.124) == "999.12"


    def test_validate(self, p):
        assert p._validate(10.0) == True
        assert p._validate(10) == True
        with pytest.raises(PMException):
            p._validate(None)
        with pytest.raises(PMException):
            p._validate(p.min-1)
        with pytest.raises(PMException):
            p._validate(p.max+1)


    def test_formated(self, p):
        p._value = 1.0
        assert p.formated() == u"1.00 °C"
        p._value = 1.991
        assert p.formated() == u"1.99 °C"
        p._value = -1.991
        assert p.formated() == u"-1.99 °C"



class TestParameterBOOL(TestRemoteAPI):
    @pytest.fixture(scope="class")
    def p(self, API):
        switch_state_channel = Device.get_devices(API, device_name="Büro-Lampe")[0].channels[0]
        return switch_state_channel.values["STATE"]


    def test_attributes(self, p):
        assert type(p) == ParameterBOOL
        assert p.type == "BOOL"
        assert p.unit == ""
        assert p.name == "STATE"
        assert type(p.value) == bool


    def test_from_api_value(self, p):
        assert p._from_api_value("0") == False
        assert p._from_api_value("1") == True


    def test_to_api_value(self, p):
        assert p._to_api_value(True) == "true"
        assert p._to_api_value(False) == "false"


    def test_validate(self, p):
        assert p._validate(True) == True
        assert p._validate(False) == True
        with pytest.raises(PMException):
            p._validate(None)



class TestParameterACTION(TestParameterBOOL):
    @pytest.fixture(scope="class")
    def p(self, API):
        button0 = Device.get_devices(API, device_name="Büro-Schalter")[0].button(0)
        return button0.values["PRESS_SHORT"]


    def test_attributes(self, p):
        print(p.__dict__)
        assert type(p) == ParameterACTION
        assert p.type == "ACTION"
        assert p.unit == ""
        assert p.name == "PRESS_SHORT"


    def test_readable(self, p):
        assert p.readable == False


    def test_get_value(self, p):
        with pytest.raises(PMException) as e:
            p.value
        assert "can not be read." in str(e.value)


    def test_set(self, p):
        p.value = True
        assert p.set(True)
        with pytest.raises(PMException):
            p.set(None)
        with pytest.raises(PMException):
            p.value = "1"
        with pytest.raises(PMException):
            p.value = None



class TestParameterINTEGER(TestRemoteAPI):
    @pytest.fixture(scope="class")
    def p(self, API):
        clima_vent_drive = Device.get_devices(API, device_name="Bad-Heizung")[0].channels[0]
        return clima_vent_drive.values["VALVE_STATE"]


    def test_attributes(self, p):
        assert type(p) == ParameterINTEGER
        assert p.type == "INTEGER"
        assert p.unit == "%"
        assert p.name == "VALVE_STATE"
        assert type(p.value) == int
        assert type(p.min) == int
        assert type(p.max) == int
        assert type(p.default) == int


    def test_from_api_value(self, p):
        assert p._from_api_value("1") == 1
        with pytest.raises(ValueError):
            p._from_api_value("1.0")


    def test_to_api_value(self, p):
        assert p._to_api_value(1) == "1"
        assert p._to_api_value(1.001) == "1"
        assert p._to_api_value(999) == "999"
        assert p._to_api_value(-999) == "-999"


    def test_validate(self, p):
        assert p._validate(p.min+1) == True
        assert p._validate(p.min) == True
        assert p._validate(p.max) == True

        with pytest.raises(PMException):
            p._validate(1.0)
        with pytest.raises(PMException):
            p._validate(None)
        with pytest.raises(PMException):
            p._validate(p.min-1)
        with pytest.raises(PMException):
            p._validate(p.max+1)


    def test_formated(self, p):
        p._value = 1
        assert p.formated() == "1%"
        p._value = 101
        assert p.formated() == "101%"
        p._value = -100
        assert p.formated() == "-100%"



class TestParameterENUM(TestRemoteAPI):
    @pytest.fixture(scope="class")
    def p(self, API):
        clima_vent_drive = Device.get_devices(API, device_name="Bad-Heizung")[0].channels[0]
        return clima_vent_drive.values["ERROR"]

    def test_attributes(self, p):
        assert type(p) == ParameterENUM
        assert p.type == "ENUM"
        assert p.unit == ""
        assert p.name == "ERROR"
        assert type(p.value) == int
        assert type(p.min) == int
        assert type(p.max) == int
        assert type(p.default) == int
        assert type(p.value_list) == list


    def test_possible_values(self, p):
        assert type(p.possible_values) == list


    def test_formated(self, p):
        assert utils.is_text(p.formated())
        assert p.formated() in p.possible_values



class TestParameterSTRING(TestRemoteAPI):
    @pytest.fixture(scope="class")
    def p(self, API):
        clima_rt_transceiver = Device.get_devices(API, device_name="Schlafzimmer-Links-Heizung")[0].channels[3]
        return clima_rt_transceiver.values["PARTY_MODE_SUBMIT"]

    def test_attributes(self, p):
        assert type(p) == ParameterSTRING
        assert p.type == "STRING"
        assert p.unit == ""
        assert p.name == "PARTY_MODE_SUBMIT"
        assert utils.is_text(p.min)
        assert utils.is_text(p.max)
        assert utils.is_text(p.default)
