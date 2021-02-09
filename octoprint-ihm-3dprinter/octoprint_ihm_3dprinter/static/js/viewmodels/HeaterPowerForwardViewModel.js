/**
 * ViewModel for heater power forward sensor
 *
 * @class HeaterPowerForwardViewModel
 * @param {Array} parameters - ViewModel dependencies
 *
 */

function HeaterPowerForwardViewModel (parameters) {
  var self = this
  setUpValue(self, 'W', 'Forward power')
  setUpValuePlot(self, 'Forward power', '.heaterPowerForward')
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
    self.value(message.heater.power_forward)
    // self.minimum(msg.heater.power_forward_min)
    // self.maximum(msg.heater.power_forward_max)
  }
}

$(function () {
  OCTOPRINT_VIEWMODELS.push({
    construct: HeaterPowerForwardViewModel,
  })
})
