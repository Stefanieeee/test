/**
 * ViewModel for heater connection interface
 *
 * @class HeaterConnectionViewModel
 * @param {Array} parameters - ViewModel dependencies
 *
 */

function HeaterConnectionViewModel (parameters) {
  var self = this
  self.octoprint_control = parameters[0]
  self.label = ko.observable('Connection')
  self.host = ko.observable()
  self.newHost = ko.observable()
  self.host.subscribe(newHost => self.newHost() === undefined ? self.newHost(newHost) : null)
  self.newHostValid = ko.observable(false)

  self.newHost.subscribe(newHost => {
    const ipRegExp = new RegExp('^(?=.*[^\.]$)((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.?){4}$')

    if (newHost.match(ipRegExp) === null) {
      console.error(`${newHost} is not a valid IP address (0.0.0.0 - 255.255.255.255)`)
      self.newHostValid(false)
    } else {
      self.newHostValid(true)
    }
  })

  self.port = ko.observable()
  self.portMin = 0
  self.portMax = 65535
  self.newPortValid = ko.observable(false)
  self.newPort = ko.observable()
  self.port.subscribe(newPort => self.newPort() === undefined ? self.newPort(newPort) : null)
  self.newPort.subscribe(newPort => {
    if (newPort < self.portMin || newPort > self.portMax || isNaN(newPort)) {
      console.error(`Port must be in range ${self.portMin}-${self.portMax}`)
      self.newPortValid(false)
    } else {
      self.newPortValid(true)
    }
  })

  self.newConnectionValid = ko.computed(() => self.newPortValid() && self.newHostValid())
  self.available = ko.observable(false)

  /**
   * Handle received data
   *
   * @param {String} id - The sender ID
   * @param {Object} message - The message payload
   *
   */

  self.onDataUpdaterPluginMessage = (id, message) => {
    if (id !== PLUGIN_UID) return
    self.port(message.heater.port)
    self.host(message.heater.host)
    self.available(message.heater.available)
  }

  self.setConnection = () => {
    // Check if values are withing minimum.
    if (!self.newConnectionValid()) return
    const payload = {
      command: `M408 HOST${self.newHost()} PORT${self.newPort()}`
    }
    self.octoprint_control.sendCustomCommand(payload)
    console.info(`Send ${payload.command}`)
    self.host(self.newHost())
    self.port(self.newPort())
  }
}

$(function () {
  OCTOPRINT_VIEWMODELS.push({
    construct: HeaterConnectionViewModel,
    dependencies: ['controlViewModel'],
    elements: ['#heaterConnectionControl']
  })
})
