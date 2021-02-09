/**
 * ViewModel for microwave control system interface
 * @class MicrowaveControlViewModel
 * @param {Array} parameters - ViewModel dependencies
 */

function MicrowaveControlViewModel (parameters) {
  var self = this
  self.octoprint_control = parameters[0]
  self.heater = parameters[1]
  self.mode = ko.observable()
  self.ready = ko.computed(() => self.mode() !== null && self.heater.ready())

  self.modeVisible = ko.observable()
  self.mode.subscribe(newValue => {
    if (self.modeVisible() === undefined) {
      self.modeVisible(newValue)
    }
  })

  /**
   * Handle received data
   *
   * @param {String} id - The sender ID
   * @param {Object} message - The message payload
   *
   */

  self.onDataUpdaterPluginMessage = (id, message) => {
    if (id !== PLUGIN_UID) return
    self.mode(message.control.mode)
  }

  self.setMode = mode => {
    const payload = { command: `M1000 ${mode}` }
    self.octoprint_control.sendCustomCommand(payload)
    console.info(`Send ${payload.command}`)
  }

  self.loadDefaults = () => {
    self.setMode('PID')
    self.heater.loadDefaults()
  }

  self.normalStop = () => {
    const payload = { command: 'M0' }
    self.octoprint_control.sendCustomCommand(payload)
    console.info(`Send ${payload.command}`)
  }

  self.emergencyStop = () => {
    const payload = { command: 'M112' }
    self.octoprint_control.sendCustomCommand(payload)
    console.info(`Send ${payload.command}`)
  }

  self.bedOn = () => {
    const payload = { command: 'M140 S50' }
    self.octoprint_control.sendCustomCommand(payload)
    console.info(`Send ${payload.command}`)
  }

  self.bedOff = () => {
    const payload = { command: 'M140 S0' }
    self.octoprint_control.sendCustomCommand(payload)
    console.info(`Send ${payload.command}`)
  }

  self.homeAll = () => {
    let payload = { command: 'G28 X Y' }
    self.octoprint_control.sendCustomCommand(payload)
    console.info(`Send ${payload.command}`)
    payload = { command: 'G28 Z' }
    self.octoprint_control.sendCustomCommand(payload)
    console.info(`Send ${payload.command}`)
  }
}

$(function () {
  OCTOPRINT_VIEWMODELS.push({
    construct: MicrowaveControlViewModel,
    dependencies: ['controlViewModel', 'heaterStatusViewModel'],
    elements: [
      '#microwaveSelectControlMode',
      '#microwaveStatus',
      '#microwaveDefaults'
    ]
  })
})
