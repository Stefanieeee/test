/**
 * ViewModel for heater power reflected interface
 *
 * @class HeaterPowerReflectedViewModel
 * @param {Array} parameters - ViewModel dependencies
 *
 */

function HeaterPowerReflectedViewModel (parameters) {
  var self = this
  setUpValue(self, 'W', 'Reflected power')
  setUpValuePlot(self, 'Reflected power', '.heaterPowerReflected')
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
    self.value(message.heater.power_reflected)
    // self.minimum(msg.heater.power_reflected_minimum)
    // self.maximum(msg.heater.power_reflected_maximum)
  }
}

$(function () {
  OCTOPRINT_VIEWMODELS.push({
    construct: HeaterPowerReflectedViewModel,
  })
})
