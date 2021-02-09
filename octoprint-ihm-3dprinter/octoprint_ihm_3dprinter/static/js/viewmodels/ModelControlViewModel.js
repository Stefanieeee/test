/**
 * ViewModel for model control interface
 *
 * @class ModelControlViewModel
 * @param {Array} parameters - ViewModel dependencies
 *
 */

function ModelControlViewModel (parameters) {
  var self = this
  self.octoprint_control = parameters[0]
  self.microwave_control = parameters[1]
  self.heater = parameters[2]
  self.power = parameters[3]
  self.ontime = parameters[4]
  self.filament_speed = parameters[5]
  self.virtual_filament_speed = parameters[6]

  // Model offset
  self.offset = ko.observable()
  self.newOffset = ko.observable()
  self.offset.subscribe(v => self.newOffset() === undefined ? self.newOffset(v) : null)
  self.offsetName = ko.observable('Offset')
  self.offsetUnit = ko.observable('W')

  // Model coefficient value
  self.coefficient = ko.observable()
  self.newCoefficient = ko.observable()
  self.coefficient.subscribe(v => self.newCoefficient() === undefined ? self.newCoefficient(v) : null)
  self.coefficientName = ko.observable('Coefficient')
  self.coefficientUnit = ko.observable('W')

  self.sensor = ko.observable()

  /**
   * Handle received data
   *
   * @param {String} id - The sender ID
   * @param {Object} message - The message payload
   *
   */

  self.onDataUpdaterPluginMessage = (id, message) => {
    if (id !== PLUGIN_UID) return
    self.offset(message.control.model.offset)
    self.coefficient(message.control.model.coefficient)
    self.sensor(message.control.model.sensor)
  }

  /**
   * Set the offset parameter
   *
   * @param {Number} offset - The offset value
   *
   */

  self.setOffset = offset => {
    const payload = { command: `M1001 P${offset}` }
    self.octoprint_control.sendCustomCommand(payload)
    console.info(`Send ${payload.command}`)
  }

  /**
   * Set the coefficient value
   *
   * @param {Number} coefficient - The coefficient value
   */

  self.setCoefficient = coefficient => {
    coefficient = coefficient === null ? '0' : coefficient;
    const payload = { command: `M1002 P${coefficient}` }
    self.octoprint_control.sendCustomCommand(payload)
    console.info(`Send ${payload.command}`)
  }

  /**
   * Set the coefficient value
   *
   * @param {Number} coefficient - The coefficient value
   */

  self.setSensor = sensor_id => {
    const payload = { command: `M1004 P${sensor_id}` }
    self.octoprint_control.sendCustomCommand(payload)
    console.info(`Send ${payload.command}`)
  }

}

$(function () {
  OCTOPRINT_VIEWMODELS.push({
    construct: ModelControlViewModel,
    dependencies: [
      'controlViewModel',
      'microwaveControlViewModel',
      'heaterStatusViewModel',
      'heaterPowerViewModel',
      'heaterOntimeViewModel',
      'filamentSpeedViewModel',
      'virtualFilamentSpeedViewModel'
    ],
    elements: ['#modelControlMode']
  })
})
