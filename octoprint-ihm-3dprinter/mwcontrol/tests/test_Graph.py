# coding=utf-8

from mwcontrol.RemoteSensor import RemoteSensor, RemoteSensorSimulator
from mwcontrol.Temperatures import Temperature
from mwcontrol.NozzleControl import NozzleControl
from hpg import Simulator as HPGSimulator
import random
import os
import time

import matplotlib
matplotlib.use('TkAgg')

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
from scipy import signal

class TemperatureGraphs(object):
    def __init__(self):
        self.setUp()
        self.temperature_to_control(self.ramp(), 'temperature_pid_ramp.png')
        self.tearDown()

    def setUp(self):
        self.temp = Temperature()
        self.temp.updateSettings({'pid':{'output':{'minimum':0, 'maximum': 20}}})
        self.temp.updateSettings({'pid':{'tunings':{'Ki':1, 'Kp':0.1, 'Kd':0.1}}})
        self.targetDir = 'docs/source/figures'

    def tearDown(self):
        pass

    def ramp(self, duration=60, samples=600, r=(0,100)):
        _time = np.linspace(0, duration, samples)
        _value = np.linspace(r[0], r[1], samples)
        return [(_time[i], _value[i]) for i in range(0, len(_time))]

    def sawtooth(self):
        times = np.linspace(0, 60, 60*10)
        temps = np.clip(signal.sawtooth(2*np.pi*30*times),0,0.5)*100
        return [(times[i], temps[i]) for i in range(0, len(times))]

    def sine(self):
        times = np.linspace(0, 60, 600)
        temps = np.abs(np.sin(2*np.pi*10*times))*55
        return [(times[i], temps[i]) for i in range(0, len(times))]

    def square(self):
        times = np.linspace(0, 60, 600)
        temps = np.clip(signal.square(2*np.pi*times*0.05), 0, 1)*50
        return [(times[i], temps[i]) for i in range(0, len(times))]

    def temperature_to_control(self, sig, filename):
        self.temp.pid.reset()
        _ctrl = []
        _time = []
        _temp = []
        self.temp.target = 40
        for value in sig:
            _time.append(value[0])
            _temp.append(value[1])
            self.temp.current = value[1]
            _ctrl.append(self.temp.control)
            time.sleep(0.01)
        figure, ax1 = plt.subplots()
        plt_legend = []
        line_time, = ax1.plot(_time, _temp, color='r', label='Sensor T [Deg. C]', linestyle='--')
        plt_legend.append(line_time)
        line_target, = ax1.plot(_time, [self.temp.target]*len(_time), color='r', label='Target T [Deg. C]', linestyle=':')
        plt_legend.append(line_target)
        ax1.set_xlabel('Time [s]')
        ax1.set_ylabel('Temperature [Deg. C]')
        ax1.set_ylim(0, None)
        ax2 = ax1.twinx()
        line_control, = ax2.plot(_time, _ctrl, color='b', label='PID control', linestyle='-')
        plt_legend.append(line_control)
        ax2.set_ylabel('PID Control []')
        ax2.set_ylim(0, None)

        plt.legend(handles=plt_legend, mode='expand', ncol=3)
        figure.tight_layout()
        plt.savefig(os.path.join(self.targetDir, filename))


class NozzleControlGraph(object):
    def __init__(self):
        self.targetDir = 'docs/source/figures'
        self.setUp()
        self.overview()
        self.tearDown()

    def sine(self):
        times = np.linspace(0, 60, 600)
        temps = np.abs(np.sin(2*np.pi*20*times))*55
        return [(times[i], temps[i]) for i in range(0, len(times))]

    def preset1(self):
        pass

    def overview(self, filename='overview.png'):
        # self.nozzle.updateSettings({'heater':{'power':{'step': 5}}})
        self.nozzle.updateSettings({'sensor': {'temperature': {'pid':{'output':{'minimum':0, 'maximum': 20}}}}})
        self.nozzle.updateSettings({'sensor': {'temperature': {'pid':{'tunings':{'Ki':0.72, 'Kp':0.6, 'Kd':0.075}}}}})
        self.nozzle.sensor.temperature.pid.reset()

        # Initialize graph
        gs = gridspec.GridSpec(3,1)
        figure = plt.figure()
        plt_legend = []

        # Initialize empty lists and collect values
        _time = []
        _ontime = []
        _temp = []
        _ctrl = []
        _power = []
        _pwm_power = []
        self.nozzle.heater.power_step = 10


        _time = np.linspace(0, 60, 600) # 60s at 10Hz
        _target = np.concatenate([np.zeros(60), np.ones(240)*50, np.ones(200)*120, np.ones(100)])
        _sens = _time*3
        for t in range(len(_time)):
            self.nozzle.sensor.temperature.target = _target[t]
            self.RemoteSensorSimulator.sendTemperature(_sens[t])
            time.sleep(0.01)
            _ontime.append(self.nozzle.heater.ontime)
            _power.append(self.nozzle.heater.power)
            _temp.append(self.nozzle.sensor.temperature.current)
            _ctrl.append(self.nozzle.sensor.temperature.control)
            _pwm_power.append(self.nozzle.heater.pwm_power)

        # First plot
        ax1 = figure.add_subplot(gs[0])
        line_temp, = ax1.plot(_time, _temp, color='r', label='Sensor T [Deg. C]', linestyle='-')
        line_target, = ax1.plot(_time, _target, color='r', label='Target T [Deg. C]', linestyle=':')
        # plt_legend.append(line_temp)
        line_control, = ax1.plot(_time, _ctrl, color='b', label='PID Control', linestyle='--')
        # plt_legend.append(line_control)
        ax1.set_ylabel('Temperature [Deg. C]')
        ax1.set_ylim(0, None)
        plt.tick_params(axis='x', labelbottom='off')

        # Second plot
        ax2  = figure.add_subplot(gs[1], sharex=ax1)
        line_ontime, = ax2.plot(_time, _ontime, color='g', label='ontime [ns]', linestyle=':')
        # plt_legend.append(line_ontime)
        ax2.set_ylabel('ontime [ns]')
        ax2.set_ylim(0, None)

        # Second plot
        ax3  = figure.add_subplot(gs[2], sharex=ax1)
        line_power, = ax3.plot(_time, _power, color='b', label='Power [W]', linestyle=':')
        line_pwm_power, = ax3.plot(_time, _pwm_power, color='b', label='Power [W]', linestyle='-')
        # plt_legend.append(line_ontime)
        ax3.set_ylabel('Power [W]')
        ax3.set_ylim(0, None)
        ax3.set_xlabel('Time [s]')

        # plt.legend(handles=plt_legend, mode='expand', ncol=3)
        figure.tight_layout()
        plt.savefig(os.path.join(self.targetDir, filename))

    def setUp(self):
        self.HPGSimulator = HPGSimulator()
        self.RemoteSensorSimulator = RemoteSensorSimulator()
        self.nozzle = NozzleControl()
        self.nozzle.start()
        self.nozzle.updateSettings({'sensor': {'temperature': {'pid':{'output':{'minimum':0, 'maximum': 20}}}}})
        self.nozzle.updateSettings({'sensor': {'temperature': {'pid':{'tunings':{'Ki':1, 'Kp':1, 'Kd':0}}}}})

    def tearDown(self):
        time.sleep(1)
        self.nozzle.stop()
        self.HPGSimulator.stop()

if __name__ == '__main__':
    #t = TemperatureGraphs()
    t = NozzleControlGraph()
