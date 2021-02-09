/**
 * ViewModel for heater pwm interface
 *
 * @class HeaterPWMViewModel
 * @param {Array} parameters - ViewModel dependencies
 *
 */

function HeaterPWMViewModel (parameters) {
  var self = this
  setUpValue(self, 'heaterPWM', 60, '')
  self.value.subscribe(newValue => updatePlot(self, newValue))

  self.onAfterTabChange = (current, previous) => {
    const chartElement = $(`#${self.id}`)

    if (chartElement.is(':visible')) {
      self.plot = $.plot(chartElement, [[]], PLOT_BASE_OPTIONS)
    }
  }

  /**
   * Handle received data
   *
   * @param {String} id - The sender ID
   * @param {Object} message - The message payload
   *
   */

  self.onDataUpdaterPluginMessage = (id, message) => {
    if (id !== PLUGIN_UID) return
    self.value(message.heater.pwm)
    self.index++
  }
}
