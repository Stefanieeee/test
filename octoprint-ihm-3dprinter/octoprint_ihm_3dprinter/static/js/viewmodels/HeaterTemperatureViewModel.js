/**
 * ViewModel for heater temperature interface
 *
 * @class HeaterTemperatureViewModel
 * @param {Array} parameters - ViewModel dependencies
 *
 */

function HeaterTemperatureViewModel (parameters) {
  var self = this
  setUpValue(self, '°C', 'Microwave Generator')
  setUpValuePlot(self, 'Microwave Generator', '.heaterTemperature', 90)
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
    self.value(message.heater.temperature)
    // self.minimum(msg.heater.temperature_minimum)
    // self.maximum(msg.heater.temperature_maximum)
  }
}

$(function () {
  OCTOPRINT_VIEWMODELS.push({
    construct: HeaterTemperatureViewModel,
    elements: ['#heaterTemperaturePlot']
  })
})
