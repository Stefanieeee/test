/**
 * ViewModel for heater status interface
 *
 * @class HeaterStatusViewModel
 * @param {Array} parameters - ViewModel dependencies
 *
 */

function HeaterStatusViewModel (parameters) {
  var self = this
  self.octoprint_control = parameters[0]  // controlViewModel
  self.connection = parameters[1]         // heaterConnectionViewModel
  self.temperature = parameters[2]        // heaterTemperatureViewModel
  self.power_forward = parameters[3]      // heaterPowerForwardViewModel
  self.power_reflected = parameters[4]    // heaterPowerReflectedViewModel
  self.frequency = parameters[5]          // heaterFrequencyViewModel
  self.offtime = parameters[6]            // heaterOfftimeViewModel
  self.power = parameters[7]              // heaterPowerViewModel
  self.ontime = parameters[8]             // heaterOntimeViewModel

  self.ready = ko.observable(false)       // Indicate it the heating system is ready
  self.active = ko.observable(false)      // Indicate if the heating system is active (connected)
  self.rf = ko.observable(false)          // Indicate if the RF output is enabled
  self.mode = ko.observable()             // Sore the operation mode

  self.getActiveLabel = ko.computed(() => self.active() ? 'YES' : 'NO', self)
  self.getRFLabel = ko.computed(() => self.rf() ? 'ON' : 'OFF', self)
  self.getAvailableLabel = ko.computed(() => self.connection.available() ? 'YES' : 'NO', self)

  /**
   * Handle received data
   *
   * @param {String} id - The sender ID
   * @param {Object} message - The message payload
   *
   */

  self.onDataUpdaterPluginMessage = (id, message) => {
    if (id !== PLUGIN_UID) return
    self.active(message.heater.active)
    self.rf(message.heater.rf)
    self.ready(message.heater.ready)
    self.mode(message.heater.mode)
  }

  self.setMode = mode => {
    const payload = {
      command: `M406 MODE${mode}`
    }
    self.octoprint_control.sendCustomCommand(payload)
    console.info(`Send ${payload.command}`)
  }

  self.setActive = value => {
    const payload = {
      command: `M1040 ACTIVE${value}`
    }
    self.octoprint_control.sendCustomCommand(payload)
    console.info(`Send ${payload.command}`)
  }

  self.loadDefaults = () => {
    self.octoprint_control.sendCustomCommand({
      commands: [
        'M404 STEP10',
        'M403 VAL30',
        'M411 P1 I0.5 D0.5',
        'M405 FREQ245000',
        'M406 MODEPWM'
      ]
    })
  }
}

$(function () {
  OCTOPRINT_VIEWMODELS.push({
    construct: HeaterStatusViewModel,
    dependencies: [
      'controlViewModel',
      'heaterConnectionViewModel',
      'heaterTemperatureViewModel',
      'heaterPowerForwardViewModel',
      'heaterPowerReflectedViewModel',
      'heaterFrequencyViewModel',
      'heaterOfftimeViewModel',
      'heaterPowerViewModel',
      'heaterOntimeViewModel'
    ],
    elements: ['#heaterStatusControl']
  })
})
