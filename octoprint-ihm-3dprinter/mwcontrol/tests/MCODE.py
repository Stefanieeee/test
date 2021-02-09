import unittest
from unittest.mock import MagicMock
from mwcontrol.MCODE import *


class TestMCODE(unittest.TestCase):
    def setUp(self):
        self.mcode = MCODE(log_console_enabled=False, logger_level='INFO')
        self.mcode.heater = MagicMock()
        self.mcode.sensor = MagicMock()
        self.mcode.temperature = MagicMock()
        try:
            self.mcode_command = self.mcode._MCODEcallbacks[self.__class__.__name__]
        except:
            pass

    def tearDown(self):
        del self.mcode

    def invalid_parameters(self, _mcode, parameters):
        for parameter in parameters:
            with self.subTest('Invalid parameters', command=self.__class__.__name__, parameter=parameter):
                with self.assertRaises(MCODEUnkownParameterError):
                    self.mcode_command([parameter])
                self.assertFalse(self.mcode.onMCODEMessage(f'{self.__class__.__name__} {parameter}'))

class M149(TestMCODE):

    def test_valid(self): =
        for u in ['C', 'K', 'F']:
            with self.subTest('Test valid unit codes', unit=u):
                self.mcode_command([f'{u}'])
                self.assertEqual(self.mcode.unit_temperature, u)
            with self.subTest('Test MCODE parser', message=f'{self.__class__.__name__} {u}'):
                self.mcode.onMCODEMessage(f'{self.__class__.__name__} {u}')
                self.assertEqual(self.mcode.unit_temperature, u)

    def test_invalid(self):
        for u in ['°C', 'Degree']:
            with self.subTest('Test unkown parameters', unit=u):
                with self.assertRaises(MCODEUnkownParameterError):
                    self.mcode_command([f'{u}'])
        for u in ['Kelvin', 'Fahrenheit']:
            with self.subTest('Test invalid unit names', unit=u):
                self.assertFalse(self.mcode_command([f'{u}']))


# class M400(TestMCODE):
#
#     def test_toggle(self):
#         for i in [0, 1]:
#             with self.subTest(f'{self.__class__.__name__} callback', state=i):
#                 self.mcode_command([f'RF{i}'])
#                 self.assertEqual(self.mcode.heater.rf, i)
#             mcode_message = f'{self.__class__.__name__} RF{i}'
#             with self.subTest('MCODE Parser', message=mcode_message):
#                 self.mcode.onMCODEMessage(mcode_message)
#                 self.assertEqual(self.mcode.heater.rf, i)
#
#     def test_invalid(self):
#         self.invalid_parameters(self.__class__.__name__, ['R', 'F'])
#         with self.assertRaises(MCODEParameterError):
#             self.mcode_command(['RF2'])
#
#     def test_empty(self):
#         self.assertFalse(self.mcode_command([]))


class M401(TestMCODE):

    def test_invalid(self):
        self.invalid_parameters(self.__class__.__name__, ['MI', 'MA', 'M', '2', '-'])
        with self.assertRaises(MCODEParameterError):
            self.mcode_command(['MINn'])

    def test_empty(self):
        self.assertFalse(self.mcode_command([]))
        self.assertFalse(self.mcode_command(['MIN', 'MAX']))

    def test_minimum(self):
        self.assertTrue(self.mcode_command(['MIN10000']))
        self.assertEqual(self.mcode.heater.ontime_min, 10000)

    def test_maximum(self):
        self.assertTrue(self.mcode_command(['MAX20000']))
        self.assertEqual(self.mcode.heater.ontime_max, 20000)

    def test_disable(self):
        self.assertTrue(self.mcode_command(['MIN0', 'MAX0']))
        self.assertIsNone(self.mcode.heater.ontime_min)
        self.assertIsNone(self.mcode.heater.ontime_max)


class M402(TestMCODE):

    def test_invalid(self):
        with self.assertRaises(MCODEUnkownParameterError):
            self.mcode_command(['OFF'])
        with self.assertRaises(MCODEParameterError):
            self.mcode_command(['OFFTIME'])
        with self.assertRaises(MCODETimeError):
            self.mcode_command(['OFFT-10.2'])

    def test_empty(self):
        self.assertFalse(self.mcode_command([]))

    def test_valid(self):
        self.assertTrue(self.mcode_command(['OFFT1000000']))
        self.assertEqual(self.mcode.heater.offtime, 1000000)


class M403(TestMCODE):

    def test_invalid(self):
        with self.assertRaises(MCODEUnkownParameterError):
            self.mcode_command(['A'])
        with self.assertRaises(MCODEParameterError):
            self.mcode_command(['MINn'])

    def test_empty(self):
        self.assertFalse(self.mcode_command([]))

    def test_valid_minimum(self):
        self.assertTrue(self.mcode_command(['MIN10']))
        self.assertEqual(self.mcode.heater.power_min, 10)

    def test_valid_maximum(self):
        self.assertTrue(self.mcode_command(['MAX20']))
        self.assertEqual(self.mcode.heater.power_max, 20)

    def test_no_value(self):
        self.assertTrue(self.mcode_command(['MIN0', 'MAX0']))
        self.assertIsNone(self.mcode.heater.power_min)
        self.assertIsNone(self.mcode.heater.power_max)


class M404(TestMCODE):

    def test_invalid(self):
        with self.assertRaises(MCODEUnkownParameterError):
            self.mcode_command(['STE'])
        with self.assertRaises(MCODEParameterError):
            self.mcode_command(['STEPSIZE'])

    def test_empty(self):
        self.assertFalse(self.mcode_command([]))

    def test_valid(self):
        self.assertTrue(self.mcode_command(['STEP10.2']))
        self.assertEqual(self.mcode.heater.power_step, 10.2)

    def test_negative(self):
        self.assertTrue(self.mcode_command(['STEP-10.2']))
        self.assertEqual(self.mcode.heater.power_step, 0)

    def test_no_value(self):
        self.assertTrue(self.mcode_command(['STEP0']))
        self.assertEqual(self.mcode.heater.power_step, 0)

class M405(TestMCODE):

    def test_invalid(self):
        with self.assertRaises(MCODEUnkownParameterError):
            self.mcode_command(['FRE'])
        with self.assertRaises(MCODEParameterError):
            self.mcode_command(['FREQUENCY'])

    def test_empty(self):
        self.assertFalse(self.mcode_command([]))
        self.assertFalse(self.mcode_command(['FREQ']))

    def test_valid(self):
        self.assertTrue(self.mcode_command(['FREQ250000']))
        self.assertEqual(self.mcode.heater.frequency, 250000)

    def test_negative(self):
        with self.assertRaises(MCODENegativeError):
            self.mcode_command(['FREQ-245000'])


class M406(TestMCODE):

    def test_invalid(self):
        with self.assertRaises(MCODEUnkownParameterError):
            self.mcode_command(['MOD'])
        with self.assertRaises(MCODEParameterError):
            self.mcode_command(['MODE0'])

    def test_empty(self):
        self.assertFalse(self.mcode_command([]))
        self.assertFalse(self.mcode_command(['MODE']))

    def test_valid(self):
        for mode in ['PWM', 'CW', 'NWA', 'PWM-NWA']:
            with self.subTest(mode=mode):
                self.assertTrue(self.mcode_command([f'MODE{mode}']))
                self.assertEqual(self.mcode.heater.mode, mode)

class M407(TestMCODE):
    pass

class M408(TestMCODE):
    pass

class M409(TestMCODE):
    pass


class M410(TestMCODE):

    def test_invalid_parameters(self):
        self.invalid_parameters(self.__class__.__name__, ['MI', 'MA', 'M', '2', '-'])


    def test_empty(self):
        self.assertFalse(self.mcode_command([]))

    def test_disable(self):
        with self.subTest('Disable minimum'):
            self.mcode.temperature.target_minimum = 0
            self.mcode.onMCODEMessage(f'{self.__class__.__name__} MIN')
            self.assertIsNone(self.mcode.temperature.target_minimum)
            self.mcode.temperature.target_minimum = 0
            self.assertTrue(self.mcode_command(['MIN']))
            self.assertIsNone(self.mcode.temperature.target_minimum)
        with self.subTest('Disable maximum'):
            self.mcode.temperature.target_maximum = 0
            self.mcode.onMCODEMessage(f'{self.__class__.__name__} MAX')
            self.assertIsNone(self.mcode.temperature.target_maximum)
            self.mcode.temperature.target_maximum = 0
            self.assertTrue(self.mcode_command(['MAX']))
            self.assertIsNone(self.mcode.temperature.target_maximum)    #
    # def test_valid(self):
    #     for mode in ['PWM', 'CW', 'NWA', 'PWM-NWA']:
    #         with self.subTest(mode=mode):
    #             self.assertTrue(self.mcode_command([f'MODE{mode}']))
    #             self.assertEqual(self.mcode.heater.mode, mode)

class M411(TestMCODE):

    def test_invalid_parameters(self):
        self.invalid_parameters(self.__class__.__name__, ['G', 'F', 'M', '2', '-'])


    def test_empty(self):
        self.assertFalse(self.mcode_command([]))

class M412(TestMCODE):

    def test_invalid_parameters(self):
        self.invalid_parameters(self.__class__.__name__, ['MI', 'MA', 'M', '2', '-'])

    def test_empty(self):
        self.assertFalse(self.mcode_command([]))

class M413(TestMCODE):

    def test_invalid_parameters(self):
        self.invalid_parameters(self.__class__.__name__, ['SAMP', 'AMP', 'S', '2', '?'])


    def test_empty(self):
        self.assertFalse(self.mcode_command([]))

if __name__ == '__main__':
    unittest.main()
