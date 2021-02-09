/**
 * ViewModel for temperature pid interface
 * @class TemperaturePIDViewModel
 * @param {Array} parameters - ViewModel dependencies
 */

function TemperaturePIDViewModel (parameters) {

  var self = this
  self.octoprint_control = parameters[0]
  setUpValue(self, '', 'PID Control')
  setUpValuePlot(self, 'PID Control', '.pidControlChart', 90)
  setUpValuePrecision(self)

  self.P = ko.observable()
  self.newP = ko.observable()
  self.P.subscribe(newP => self.newP() === undefined ? self.newP(newP) : null)

  self.I = ko.observable()
  self.newI = ko.observable()
  self.I.subscribe(newI => self.newI() === undefined ? self.newI(newI) : null)

  self.D = ko.observable()
  self.newD = ko.observable()
  self.D.subscribe(newD => self.newD() === undefined ? self.newD(newD) : null)

  /**
   * Handle received data
   * @param {String} id - The sender ID
   * @param {Object} message - The message payload
   */

  self.onDataUpdaterPluginMessage = (id, message) => {
    if (id !== PLUGIN_UID) return // Ignore message if it's not meant for us
    self.P(message.temperature.pid.Kp)
    self.I(message.temperature.pid.Ki)
    self.D(message.temperature.pid.Kd)
    self.value(message.temperature.pid.control)
  }

  /**
   * Set new PID values
   */

  self.setPID = () => {
    const payload = {
      command: `M411 P${self.newP()} I${self.newI()} D${self.newD()}`
    }
    self.octoprint_control.sendCustomCommand(payload)
    console.info(`Send ${payload.command}`)
  }
}

$(function () {
  OCTOPRINT_VIEWMODELS.push({
    construct: TemperaturePIDViewModel,
    dependencies: ['controlViewModel'],
    elements: ['#temperaturePIDControl']
  })
})
