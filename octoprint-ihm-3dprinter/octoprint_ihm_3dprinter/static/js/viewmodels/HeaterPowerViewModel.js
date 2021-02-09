/**
 * ViewModel for heater pwm power interface
 *
 * @class HeaterPWMPowerViewModel
 * @param {Array} parameters - ViewModel dependencies
 *
 */

function HeaterPWMPowerViewModel (parameters) {
  var self = this
  setUpValue(self, 'W', 'PWM Power')
  setUpValuePlot(self, 'PWM Power', '.heaterPWMPower')
  setUpValuePrecision(self, 2)

  /**
   * Handle received data
   *
   * @param {String} id - The sender ID
   * @param {Object} message - The message payload
   *
   */

  self.onDataUpdaterPluginMessage = (id, message) => {
    if (id !== PLUGIN_UID) return
    self.value(message.heater.pwm_power)
  }
}

/**
 * ViewModel for heater power interface
 *
 * @class HeaterPowerViewModel
 * @param {Array} parameters - ViewModel dependencies
 *
 */

function HeaterPowerViewModel (parameters) {
  var self = this
  self.octoprint_control = parameters[0]
  self.step = parameters[1]
  self.pwm = parameters[2]
  setUpValue(self, 'W', 'Power')
  setUpValuePrecision(self, 2)

  self.label = 'Power'
  self.index = 90

  self.chartElementSelectors = [
    {selector:'#manual-power-chart', chart: null},
    {selector:'#pid-power-chart', chart: null},
    {selector:'#model-power-chart', chart: null}
  ]
  self.chartData = [
    createDataSeries(self.label, self.index, 'rgba(0,255,0,0.5)', self.unit()),
    createDataSeries(self.pwm.label, self.index, 'rgba(0,0,0,1)', self.pwm.unit()),
    createDataSeries(self.step.label, self.index, 'rgba(255,0,0,0.5)', self.step.unit()),
  ]

  self.updateChart = () => {
    self.index++
    pushToDataSeries(self, 0, self.valueFormatted())
    pushToDataSeries(self, 1, self.pwm.valueFormatted())
    pushToDataSeries(self, 2, self.step.value())
    updateChart(self)
  }

  self.onStartupComplete = () => setInterval( () => self.updateChart(), 100 )

  /**
   * Handle received data
   *
   * @param {String} id - The sender ID
   * @param {Object} message - The message payload
   *
   */

  self.onDataUpdaterPluginMessage = (id, message) => {
    if (id !== PLUGIN_UID) return
    self.value(message.heater.power)
  }

  self.setPower = offset => {
    if (offset !== 0) {
      self.newValue(self.value() + self.step.value() * offset)
    }

    const payload = {
      command: `M403 VAL${self.newValue()}`
    }
    self.octoprint_control.sendCustomCommand(payload)
    console.info(`Send ${payload.command}`)
    self.value(self.newValue())
  }

  self.setLimits = () => {
    const payload = {
      command: `M403 MIN${self.newMinimum()} MAX${self.newMaximum()}`
    }
    self.octoprint_control.sendCustomCommand(payload)
    console.info(`Send ${payload.command}`)
  }
}

/**
 * ViewModel for heater power step interface
 * @class HeaterPowerStepViewModel
 * @param {Array} parameters - ViewModel dependencies
 */

function HeaterPowerStepViewModel (parameters) {
  var self = this
  self.octoprint_control = parameters[0]
  setUpValue(self, 'W', 'Power step')
  setUpValuePlot(self, 'Power step', '.heaterPowerStepChart')

  /**
   * Handle received data
   * @param {String} id - The sender ID
   * @param {Object} message - The message payload
   */

  self.onDataUpdaterPluginMessage = (id, message) => {
    if (id !== PLUGIN_UID) return
    self.value(message.heater.power_step)
  }

  self.setStep = () => {
    const payload = {
      command: `M404 STEP${self.newValue()}`
    }
    self.octoprint_control.sendCustomCommand(payload)
    console.info(`Send ${payload.command}`)
  }
}

$(function () {
  OCTOPRINT_VIEWMODELS.push({
    construct: HeaterPowerViewModel,
    dependencies: [
      'controlViewModel',
      'heaterPowerStepViewModel',
      'heaterPWMPowerViewModel'
    ],
    elements: ['.heaterPowerControl', '.heaterPowerData']
  })

  OCTOPRINT_VIEWMODELS.push({
    construct: HeaterPWMPowerViewModel,
    elements: ['.heaterPWMPowerData']
  })

  OCTOPRINT_VIEWMODELS.push({
    construct: HeaterPowerStepViewModel,
    dependencies: ['controlViewModel'],
    elements: ['.heaterPowerStepData']
  })

})
